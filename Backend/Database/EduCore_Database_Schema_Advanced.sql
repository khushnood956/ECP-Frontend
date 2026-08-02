-- ============================================================================
-- EduCore — Advanced Database Concepts Extension
-- Version: 1.0
-- Apply AFTER EduCore_Database_Schema.sql
--
-- This file adds:
--   1. Least-privilege database roles + grants
--   2. Row-Level Security (RLS) policies (defense-in-depth against
--      broken app-layer authorization, and a mitigation against SQL
--      injection since even a compromised query is scoped by Postgres)
--   3. Notification templates (gap fix from portal review)
--   4. Table partitioning (audit_logs, notifications) by month
--   5. Materialized views for admin analytics
--   6. Full-text search indexes (scholarships, agency offerings)
--   7. Optimistic concurrency control (version column) on agency_offerings
--   8. Worked transaction example (test attempt submission)
--   9. Cross-portal convenience views
-- ============================================================================

-- ============================================================================
-- SECTION 1: DATABASE ROLES & LEAST-PRIVILEGE GRANTS
-- The application connects as one of these roles depending on which portal
-- is making the request — never as a superuser. This is real SQL-injection
-- mitigation: even if a query were compromised, the DB role itself cannot
-- touch tables/rows outside its portal's scope.
-- ============================================================================

CREATE ROLE app_student NOLOGIN;
CREATE ROLE app_agency NOLOGIN;
CREATE ROLE app_admin NOLOGIN;

-- Student-facing app connects as a login role that inherits app_student
-- e.g. CREATE ROLE app_student_login LOGIN PASSWORD '...' IN ROLE app_student;

GRANT SELECT ON tests, questions, question_versions, scholarships,
    scholarship_translations, scholarship_guide_steps, taxonomy_terms,
    taxonomy_term_translations, agency_profiles, agency_offerings TO app_student;
GRANT SELECT, INSERT, UPDATE ON student_profiles, student_target_countries,
    student_target_tests, test_attempts, test_attempt_answers,
    scholarship_bookmarks, leads, lead_messages TO app_student;
GRANT SELECT, UPDATE ON notifications TO app_student; -- can mark own as read, not create

GRANT SELECT ON scholarships, taxonomy_terms, taxonomy_term_translations TO app_agency;
GRANT SELECT, INSERT, UPDATE ON agency_profiles, agency_verification_documents,
    agency_service_countries, agency_offerings, agency_staff_members,
    leads, lead_messages TO app_agency;

-- Admin gets full CRUD on content/moderation tables, but note: even admin
-- does NOT get blanket access to auth_identities.password_hash-adjacent
-- columns via this grant model — see column-level privacy note at bottom.
GRANT SELECT, INSERT, UPDATE, DELETE ON
    users, account_statuses, agency_verification_statuses, tests, questions,
    question_versions, scholarships, scholarship_translations,
    scholarship_guide_steps, taxonomy_types, taxonomy_terms,
    taxonomy_term_translations, agency_profiles, content_reports,
    audit_logs, notifications TO app_admin;

-- ============================================================================
-- SECTION 2: ROW-LEVEL SECURITY (RLS)
-- Enforced by Postgres itself at query time, regardless of what the
-- application's WHERE clause says. This is the key defense-in-depth layer:
-- even a successful SQL injection cannot read/write rows outside what the
-- connected role+policy allows.
-- ============================================================================

ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY student_profiles_own_rows ON student_profiles
    FOR ALL TO app_student
    USING (user_id = current_setting('app.current_user_id')::UUID);

ALTER TABLE test_attempts ENABLE ROW LEVEL SECURITY;
CREATE POLICY test_attempts_own_rows ON test_attempts
    FOR ALL TO app_student
    USING (student_profile_id IN (
        SELECT id FROM student_profiles
        WHERE user_id = current_setting('app.current_user_id')::UUID
    ));

ALTER TABLE agency_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY agency_profiles_own_row ON agency_profiles
    FOR ALL TO app_agency
    USING (user_id = current_setting('app.current_user_id')::UUID);

ALTER TABLE agency_offerings ENABLE ROW LEVEL SECURITY;
CREATE POLICY agency_offerings_own_rows ON agency_offerings
    FOR ALL TO app_agency
    USING (agency_profile_id IN (
        SELECT id FROM agency_profiles
        WHERE user_id = current_setting('app.current_user_id')::UUID
    ));

ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
CREATE POLICY leads_student_side ON leads
    FOR ALL TO app_student
    USING (student_profile_id IN (
        SELECT id FROM student_profiles
        WHERE user_id = current_setting('app.current_user_id')::UUID
    ));
CREATE POLICY leads_agency_side ON leads
    FOR ALL TO app_agency
    USING (agency_profile_id IN (
        SELECT id FROM agency_profiles
        WHERE user_id = current_setting('app.current_user_id')::UUID
    ));

ALTER TABLE lead_messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY lead_messages_participant_only ON lead_messages
    FOR ALL TO app_student, app_agency
    USING (lead_id IN (
        SELECT id FROM leads WHERE
            student_profile_id IN (SELECT id FROM student_profiles WHERE user_id = current_setting('app.current_user_id')::UUID)
            OR agency_profile_id IN (SELECT id FROM agency_profiles WHERE user_id = current_setting('app.current_user_id')::UUID)
    ));

ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
CREATE POLICY notifications_own_rows ON notifications
    FOR ALL TO app_student, app_agency
    USING (user_id = current_setting('app.current_user_id')::UUID);

-- Usage pattern from the app on every connection/request:
--   SET app.current_user_id = '<uuid-of-authenticated-user>';
-- This is typically set once per pooled connection checkout via the
-- backend's request middleware, not per query.

-- ============================================================================
-- SECTION 3: NOTIFICATION TEMPLATES (gap fix)
-- Reusable, admin-editable templates instead of hardcoded strings in app code.
-- ============================================================================

CREATE TABLE notification_templates (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_term_id         UUID NOT NULL REFERENCES taxonomy_terms(id), -- taxonomy_type = notification_type
    language_code        VARCHAR(10) NOT NULL REFERENCES languages(code),
    title_template        TEXT NOT NULL,   -- supports {{placeholders}}
    body_template          TEXT NOT NULL,
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at               TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (type_term_id, language_code)
);
CREATE TRIGGER trg_set_updated_at BEFORE UPDATE ON notification_templates
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================================
-- SECTION 4: TABLE PARTITIONING
-- audit_logs and notifications grow unbounded and are almost always queried
-- by recent time range — classic range-partitioning candidates. Old
-- partitions can be archived to cold storage or dropped instantly (no
-- expensive DELETE scan).
--
-- NOTE: this replaces the plain tables from the base schema file with
-- partitioned equivalents. If the base schema was already applied and has
-- data, migrate via: create partitioned table -> copy data -> rename.
-- Shown here as the target design.
-- ============================================================================

-- Drop the non-partitioned versions from the base script if starting fresh:
-- DROP TABLE IF EXISTS audit_logs, notifications;

CREATE TABLE audit_logs_p (
    id                    UUID DEFAULT uuid_generate_v4(),
    actor_user_id           UUID REFERENCES users(id),
    action                   VARCHAR(100) NOT NULL,
    target_type              VARCHAR(50) NOT NULL,
    target_id                UUID NOT NULL,
    reason                    TEXT,
    metadata                  JSONB NOT NULL DEFAULT '{}',
    created_at                 TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE audit_logs_2026_08 PARTITION OF audit_logs_p
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');
CREATE TABLE audit_logs_2026_09 PARTITION OF audit_logs_p
    FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');
-- New partitions created monthly, ideally via a scheduled job
-- (pg_partman extension automates this in production).

CREATE TABLE notifications_p (
    id                    UUID DEFAULT uuid_generate_v4(),
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type_term_id             UUID NOT NULL REFERENCES taxonomy_terms(id),
    title                    VARCHAR(200) NOT NULL,
    body                     TEXT,
    payload                  JSONB NOT NULL DEFAULT '{}',
    read_at                   TIMESTAMPTZ,
    created_at                 TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE notifications_2026_08 PARTITION OF notifications_p
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');
CREATE TABLE notifications_2026_09 PARTITION OF notifications_p
    FOR VALUES FROM ('2026-09-01') TO ('2026-10-01');

CREATE INDEX idx_audit_logs_p_target ON audit_logs_p(target_type, target_id);
CREATE INDEX idx_notifications_p_user_unread ON notifications_p(user_id, read_at);

-- ============================================================================
-- SECTION 5: MATERIALIZED VIEWS FOR ADMIN ANALYTICS
-- Precomputed and refreshed on a schedule (e.g. every 15 min via cron or
-- pg_cron), so the Admin analytics dashboard never runs expensive live
-- aggregations against transactional tables.
-- ============================================================================

CREATE MATERIALIZED VIEW mv_student_performance_summary AS
SELECT
    sp.id                       AS student_profile_id,
    sp.full_name,
    t.test_category_term_id,
    COUNT(ta.id)                AS attempts_count,
    AVG(ta.score)                AS avg_score,
    MAX(ta.submitted_at)          AS last_attempt_at
FROM student_profiles sp
JOIN test_attempts ta ON ta.student_profile_id = sp.id
JOIN tests t ON t.id = ta.test_id
WHERE ta.submitted_at IS NOT NULL
GROUP BY sp.id, sp.full_name, t.test_category_term_id;

CREATE UNIQUE INDEX idx_mv_student_perf ON mv_student_performance_summary(student_profile_id, test_category_term_id);

CREATE MATERIALIZED VIEW mv_agency_conversion_rates AS
SELECT
    ap.id                        AS agency_profile_id,
    ap.business_name,
    COUNT(l.id)                  AS total_leads,
    COUNT(l.id) FILTER (
        WHERE tt.code = 'converted'
    )                              AS converted_leads,
    ROUND(
        COUNT(l.id) FILTER (WHERE tt.code = 'converted')::NUMERIC
        / NULLIF(COUNT(l.id), 0) * 100, 2
    )                              AS conversion_rate_pct
FROM agency_profiles ap
LEFT JOIN leads l ON l.agency_profile_id = ap.id
LEFT JOIN taxonomy_terms tt ON tt.id = l.status_term_id
GROUP BY ap.id, ap.business_name;

CREATE UNIQUE INDEX idx_mv_agency_conversion ON mv_agency_conversion_rates(agency_profile_id);

-- Refresh strategy (CONCURRENTLY avoids locking reads during refresh;
-- requires the unique index above):
--   REFRESH MATERIALIZED VIEW CONCURRENTLY mv_student_performance_summary;
--   REFRESH MATERIALIZED VIEW CONCURRENTLY mv_agency_conversion_rates;
-- Scheduled via pg_cron, e.g.:
--   SELECT cron.schedule('refresh-analytics', '*/15 * * * *',
--     $$REFRESH MATERIALIZED VIEW CONCURRENTLY mv_student_performance_summary$$);

-- ============================================================================
-- SECTION 6: FULL-TEXT SEARCH
-- GIN indexes over tsvector for fast search on scholarships/offerings,
-- staving off the need for Elasticsearch until the catalog is much larger.
-- ============================================================================

ALTER TABLE scholarships ADD COLUMN search_vector TSVECTOR;
UPDATE scholarships SET search_vector =
    to_tsvector('english', coalesce(title,'') || ' ' || coalesce(provider_name,'') || ' ' || coalesce(summary,''));

CREATE FUNCTION scholarships_search_vector_update() RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english',
        coalesce(NEW.title,'') || ' ' || coalesce(NEW.provider_name,'') || ' ' || coalesce(NEW.summary,''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_scholarships_search_vector
    BEFORE INSERT OR UPDATE ON scholarships
    FOR EACH ROW EXECUTE FUNCTION scholarships_search_vector_update();

CREATE INDEX idx_scholarships_search ON scholarships USING GIN(search_vector);

ALTER TABLE agency_offerings ADD COLUMN search_vector TSVECTOR;
UPDATE agency_offerings SET search_vector =
    to_tsvector('english', coalesce(title,'') || ' ' || coalesce(description,''));

CREATE FUNCTION offerings_search_vector_update() RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', coalesce(NEW.title,'') || ' ' || coalesce(NEW.description,''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_offerings_search_vector
    BEFORE INSERT OR UPDATE ON agency_offerings
    FOR EACH ROW EXECUTE FUNCTION offerings_search_vector_update();

CREATE INDEX idx_offerings_search ON agency_offerings USING GIN(search_vector);

-- Example query:
--   SELECT * FROM scholarships
--   WHERE search_vector @@ plainto_tsquery('english', 'engineering germany')
--   ORDER BY ts_rank(search_vector, plainto_tsquery('english', 'engineering germany')) DESC;

-- ============================================================================
-- SECTION 7: OPTIMISTIC CONCURRENCY CONTROL
-- Prevents lost updates when two sessions (e.g. an agency owner and an
-- agency staff member) edit the same offering at the same time.
-- ============================================================================

ALTER TABLE agency_offerings ADD COLUMN version INT NOT NULL DEFAULT 1;

-- App-layer update pattern (not just an UPDATE by id):
--   UPDATE agency_offerings
--   SET title = $1, description = $2, version = version + 1, updated_at = now()
--   WHERE id = $3 AND version = $4;   -- $4 = version the client last read
-- If the UPDATE affects 0 rows, the client's data was stale -> reject with
-- a 409 Conflict and ask the client to reload and retry.

-- ============================================================================
-- SECTION 8: WORKED TRANSACTION EXAMPLE (ACID)
-- Submitting a test attempt: scoring the answers and updating the attempt
-- must be atomic — either both happen or neither does.
-- ============================================================================

-- BEGIN;
--
-- -- 1. Lock the attempt row to prevent concurrent double-submission
-- SELECT id FROM test_attempts WHERE id = $1 FOR UPDATE;
--
-- -- 2. Score every answer against its question_version's correct options
-- UPDATE test_attempt_answers taa
-- SET is_correct = (taa.selected_option_ids = qv.correct_option_ids)
-- FROM question_versions qv
-- WHERE taa.question_version_id = qv.id
--   AND taa.test_attempt_id = $1;
--
-- -- 3. Compute and store the final score
-- UPDATE test_attempts
-- SET score = (
--       SELECT COUNT(*) FROM test_attempt_answers
--       WHERE test_attempt_id = $1 AND is_correct = TRUE
--     ),
--     max_score = (
--       SELECT COUNT(*) FROM test_attempt_answers WHERE test_attempt_id = $1
--     ),
--     submitted_at = now()
-- WHERE id = $1;
--
-- COMMIT;
--
-- Isolation level: READ COMMITTED (Postgres default) is sufficient here
-- because of the row lock in step 1. Use SERIALIZABLE only for flows with
-- multi-row invariants across tables (e.g. a future seat-limited
-- scholarship slot counter).

-- ============================================================================
-- SECTION 9: CROSS-PORTAL CONVENIENCE VIEWS
-- ============================================================================

CREATE VIEW active_verified_agencies AS
SELECT ap.*
FROM agency_profiles ap
JOIN agency_verification_statuses avs ON avs.id = ap.verification_status_id
WHERE avs.code = 'verified' AND ap.deleted_at IS NULL;

CREATE VIEW student_dashboard_summary AS
SELECT
    sp.id AS student_profile_id,
    sp.full_name,
    (SELECT COUNT(*) FROM test_attempts ta WHERE ta.student_profile_id = sp.id) AS total_test_attempts,
    (SELECT COUNT(*) FROM scholarship_bookmarks sb WHERE sb.student_profile_id = sp.id) AS bookmarked_scholarships,
    (SELECT COUNT(*) FROM leads l WHERE l.student_profile_id = sp.id) AS total_agency_inquiries
FROM student_profiles sp;

-- ============================================================================
-- SECTION 10: COLUMN-LEVEL PRIVACY NOTE
-- Even the app_admin role above is granted table-level access, but
-- `password_hash` should additionally be excluded at the application
-- serialization layer (never returned in any API response, admin or not).
-- For stricter DB-level enforcement, password_hash can be moved to a
-- separate `user_credentials` table that only a dedicated `app_auth` role
-- (used solely by the login/password-reset service) can read.
-- ============================================================================
