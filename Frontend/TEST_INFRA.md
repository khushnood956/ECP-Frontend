# E2E Test Infra: EduConsultant Student Portal Prototype

## Test Philosophy
- **Opaque-box, requirement-driven**: All test scenarios are written from the perspective of an end-user interacting with the UI. The tests have no dependency on the internal React component hierarchy, state implementation, or styling classes other than standard roles, placeholder texts, and input names.
- **Methodology**: The test suite covers Feature Coverage (Tier 1), Boundary Value Analysis & Error Handling (Tier 2), Cross-Feature Combinations (Tier 3), and Real-World Application Workloads (Tier 4).

## Feature Inventory
| # | Feature | Source (requirement) | Tier 1 | Tier 2 | Tier 3 |
|---|---------|---------------------|:------:|:------:|:------:|
| 1 | Authentication & Session | ORIGINAL_REQUEST §R1 | 5      | 5      | ✓      |
| 2 | Profile Management | ORIGINAL_REQUEST §R1 | 5      | 5      | ✓      |
| 3 | Scholarship Discovery | ORIGINAL_REQUEST §R2 | 5      | 5      | ✓      |
| 4 | University Discovery | ORIGINAL_REQUEST §R2 | 5      | 5      | ✓      |
| 5 | Application & Timeline | ORIGINAL_REQUEST §R3 | 5      | 5      | ✓      |
| 6 | Document Manager | ORIGINAL_REQUEST §R3 | 5      | 5      | ✓      |
| 7 | Dashboard & Layout | ORIGINAL_REQUEST §R4 | 5      | 5      | ✓      |

## Test Architecture
- **Test Runner**: Playwright
- **Invocation Command**: `npm run test:e2e`
- **Pass/Fail Semantics**: The test runner runs in parallel across multiple virtual browsers (Chromium, Firefox, WebKit). A test run is successful (exit code 0) only if all assertions across all 82 test cases pass.
- **Directory Layout**:
  - `playwright.config.js` - Configuration file at the root.
  - `tests/` - Directory containing E2E test suites.
    - `auth.spec.js` - Tests covering registration, login, logout, and profile management.
    - `discovery.spec.js` - Tests covering scholarships/universities list, search, filter, and detail views.
    - `applications.spec.js` - Tests covering application submission, timeline status, and document upload/delete.
    - `dashboard.spec.js` - Tests covering dashboard stats widgets, widgets content, navigation links, and mobile responsiveness.
    - `scenarios.spec.js` - Tests covering cross-feature integrations and complex real-world workflows.

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | Full Student Onboarding & Discovery Journey | Register, Update Profile, Search/Filter Universities, View Details, Save Scholarship, Verify Dashboard | High |
| 2 | End-to-End Application & Document Lifecycle | Upload Document, Apply for Scholarship, Attach Document, Submit, Track in Tracker, Verify Dashboard Stats | High |
| 3 | Application Tracking and Status Progression | Check Application, View Timeline, Simulate Status Transition (Submitted -> In Review -> Accepted), Verify Congratulations Card | Medium |
| 4 | Comprehensive Data Filtering & Decision Flow | Search/Filter Scholarships, Bookmark Multiple, Compare in Dashboard, Remove Bookmark, Apply, Verify Stats | High |
| 5 | Multi-User Academic Profile Isolation | User A logs in (Doctorate), saves details -> Logout -> User B logs in (Undergraduate) -> Check isolation -> Logout -> User A logs back in -> Verify state persistence | High |

## Coverage Thresholds
- **Tier 1 (Feature Coverage)**: ≥5 tests per feature. Total 25 tests implemented.
- **Tier 2 (Boundary & Corner Cases)**: ≥5 tests per feature covering boundary inputs and error handling. Total 35 tests implemented.
- **Tier 3 (Cross-Feature Combinations)**: Pairwise coverage of feature interactions (e.g. Auth + Profile + Dashboard). Total 7 tests implemented.
- **Tier 4 (Real-World Workloads)**: ≥5 realistic scenarios exercising multiple features together. Total 5 tests implemented.
- **Total Suite Size**: 82 test cases.
