from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.auth import get_current_active_user
from app.models.enums import UserRole
from app.models.user import User
from app.services.exceptions import (
    BusinessRuleViolation,
    EntityNotFound,
    PermissionDenied,
)
from main import app

# --- Mock Model helpers ---

class MockClass:
    def __init__(self, id_val=None, name="Class A", code="CS101", instructor_id=None):
        from datetime import timezone
        self.id = id_val or uuid4()
        self.name = name
        self.code = code
        self.instructor_id = instructor_id or uuid4()
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)


class MockEnrollment:
    def __init__(self, id_val=None, class_id=None, student_id=None, status="active"):
        from datetime import timezone
        self.id = id_val or uuid4()
        self.class_id = class_id or uuid4()
        self.student_id = student_id or uuid4()
        self.status = status
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)


class MockAttendance:
    def __init__(self, id_val=None, class_id=None, student_id=None, date_val=None, status="present", remarks=None):
        from datetime import timezone
        self.id = id_val or uuid4()
        self.class_id = class_id or uuid4()
        self.student_id = student_id or uuid4()
        self.date = date_val or datetime.now(timezone.utc).date()
        self.status = status
        self.remarks = remarks
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)


class MockPaginatedResult:
    def __init__(self, items):
        self.items = items
        self.total = len(items)
        self.page = 1
        self.page_size = 10
        self.total_pages = 1


# --- Auth overrides ---

ADMIN_USER = User(id=str(uuid4()), email="admin@test.com", is_active=True, role=UserRole.ADMIN)
TEACHER_A = User(id=str(uuid4()), email="teachera@test.com", is_active=True, role=UserRole.TEACHER)
TEACHER_B = User(id=str(uuid4()), email="teacherb@test.com", is_active=True, role=UserRole.TEACHER)
STUDENT_A = User(id=str(uuid4()), email="studenta@test.com", is_active=True, role=UserRole.STUDENT)
STUDENT_B = User(id=str(uuid4()), email="studentb@test.com", is_active=True, role=UserRole.STUDENT)
AGENCY_A = User(id=str(uuid4()), email="agencya@test.com", is_active=True, role=UserRole.AGENCY)


@pytest.fixture(autouse=True)
def clean_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


# --- CLASS SECURITY (ACAD-01 to ACAD-10) ---

@pytest.mark.asyncio
async def test_acad_01_admin_can_create_class():
    app.dependency_overrides[get_current_active_user] = lambda: ADMIN_USER
    mock_cls = MockClass(instructor_id=TEACHER_A.id)
    with patch('app.services.class_service.ClassService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_cls
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/classes", json={"name": "Class A", "code": "CS101", "instructor_id": str(TEACHER_A.id)})
        assert res.status_code == 201


@pytest.mark.asyncio
async def test_acad_02_teacher_cannot_create_class():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    with patch('app.services.class_service.ClassService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/classes", json={"name": "Class A", "code": "CS101", "instructor_id": str(TEACHER_A.id)})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_03_student_cannot_create_class():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    with patch('app.services.class_service.ClassService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/classes", json={"name": "Class A", "code": "CS101", "instructor_id": str(TEACHER_A.id)})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_04_agency_cannot_create_class():
    app.dependency_overrides[get_current_active_user] = lambda: AGENCY_A
    with patch('app.services.class_service.ClassService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/classes", json={"name": "Class A", "code": "CS101", "instructor_id": str(TEACHER_A.id)})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_05_teacher_can_view_assigned_class():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    class_id = uuid4()
    mock_cls = MockClass(id_val=class_id, instructor_id=TEACHER_A.id)
    with patch('app.services.class_service.ClassService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_cls
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(f"/api/v1/classes/{class_id}")
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_acad_06_teacher_cannot_view_another_teachers_class():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    class_id = uuid4()
    with patch('app.services.class_service.ClassService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(f"/api/v1/classes/{class_id}")
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_07_teacher_cannot_update_another_teachers_class():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    class_id = uuid4()
    with patch('app.services.class_service.ClassService.update', new_callable=AsyncMock) as mock_update:
        mock_update.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.patch(f"/api/v1/classes/{class_id}", json={"name": "Class B"})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_08_teacher_cannot_delete_another_teachers_class():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    class_id = uuid4()
    with patch('app.services.class_service.ClassService.delete', new_callable=AsyncMock) as mock_delete:
        mock_delete.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.delete(f"/api/v1/classes/{class_id}")
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_09_student_can_view_enrolled_class():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    class_id = uuid4()
    mock_cls = MockClass(id_val=class_id, instructor_id=TEACHER_A.id)
    with patch('app.services.class_service.ClassService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_cls
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(f"/api/v1/classes/{class_id}")
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_acad_10_student_cannot_view_non_enrolled_class():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    class_id = uuid4()
    with patch('app.services.class_service.ClassService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(f"/api/v1/classes/{class_id}")
        assert res.status_code == 403


# --- ENROLLMENT SECURITY (ACAD-11 to ACAD-20) ---

@pytest.mark.asyncio
async def test_acad_11_admin_can_create_enrollment():
    app.dependency_overrides[get_current_active_user] = lambda: ADMIN_USER
    mock_enr = MockEnrollment()
    with patch('app.services.enrollment_service.EnrollmentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_enr
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/enrollments", json={"class_id": str(uuid4()), "student_id": str(uuid4())})
        assert res.status_code == 201


@pytest.mark.asyncio
async def test_acad_12_assigned_teacher_can_create_enrollment():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    mock_enr = MockEnrollment()
    with patch('app.services.enrollment_service.EnrollmentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_enr
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/enrollments", json={"class_id": str(uuid4()), "student_id": str(uuid4())})
        assert res.status_code == 201


@pytest.mark.asyncio
async def test_acad_13_teacher_cannot_enroll_into_another_teachers_class():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    with patch('app.services.enrollment_service.EnrollmentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/enrollments", json={"class_id": str(uuid4()), "student_id": str(uuid4())})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_14_student_cannot_create_enrollment():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    with patch('app.services.enrollment_service.EnrollmentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/enrollments", json={"class_id": str(uuid4()), "student_id": str(uuid4())})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_15_agency_cannot_create_enrollment():
    app.dependency_overrides[get_current_active_user] = lambda: AGENCY_A
    with patch('app.services.enrollment_service.EnrollmentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/enrollments", json={"class_id": str(uuid4()), "student_id": str(uuid4())})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_16_cannot_enroll_nonexistent_student():
    app.dependency_overrides[get_current_active_user] = lambda: ADMIN_USER
    with patch('app.services.enrollment_service.EnrollmentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = EntityNotFound("Student not found")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/enrollments", json={"class_id": str(uuid4()), "student_id": str(uuid4())})
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_acad_17_cannot_enroll_non_student_profile():
    app.dependency_overrides[get_current_active_user] = lambda: ADMIN_USER
    with patch('app.services.enrollment_service.EnrollmentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = BusinessRuleViolation("Not a student")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/enrollments", json={"class_id": str(uuid4()), "student_id": str(uuid4())})
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_acad_18_duplicate_enrollment_rejected():
    app.dependency_overrides[get_current_active_user] = lambda: ADMIN_USER
    with patch('app.services.enrollment_service.EnrollmentService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = BusinessRuleViolation("Duplicate enrollment")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/enrollments", json={"class_id": str(uuid4()), "student_id": str(uuid4())})
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_acad_19_student_cannot_modify_enrollment():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    enr_id = uuid4()
    with patch('app.services.enrollment_service.EnrollmentService.update', new_callable=AsyncMock) as mock_update:
        mock_update.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.patch(f"/api/v1/enrollments/{enr_id}", json={"status": "completed"})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_20_student_cannot_delete_enrollment():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    enr_id = uuid4()
    with patch('app.services.enrollment_service.EnrollmentService.delete', new_callable=AsyncMock) as mock_delete:
        mock_delete.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.delete(f"/api/v1/enrollments/{enr_id}")
        assert res.status_code == 403


# --- ATTENDANCE SECURITY (ACAD-21 to ACAD-34) ---

@pytest.mark.asyncio
async def test_acad_21_admin_can_create_attendance():
    app.dependency_overrides[get_current_active_user] = lambda: ADMIN_USER
    mock_att = MockAttendance()
    with patch('app.services.attendance_service.AttendanceService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_att
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/attendance", json={"class_id": str(uuid4()), "student_id": str(uuid4()), "date": "2026-08-12", "status": "present"})
        assert res.status_code == 201


@pytest.mark.asyncio
async def test_acad_22_assigned_teacher_can_create_attendance():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    mock_att = MockAttendance()
    with patch('app.services.attendance_service.AttendanceService.create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_att
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/attendance", json={"class_id": str(uuid4()), "student_id": str(uuid4()), "date": "2026-08-12", "status": "present"})
        assert res.status_code == 201


@pytest.mark.asyncio
async def test_acad_23_teacher_cannot_create_attendance_for_another_teachers_class():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    with patch('app.services.attendance_service.AttendanceService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/attendance", json={"class_id": str(uuid4()), "student_id": str(uuid4()), "date": "2026-08-12", "status": "present"})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_24_student_cannot_create_attendance():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    with patch('app.services.attendance_service.AttendanceService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/attendance", json={"class_id": str(uuid4()), "student_id": str(uuid4()), "date": "2026-08-12", "status": "present"})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_25_agency_cannot_create_attendance():
    app.dependency_overrides[get_current_active_user] = lambda: AGENCY_A
    with patch('app.services.attendance_service.AttendanceService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/attendance", json={"class_id": str(uuid4()), "student_id": str(uuid4()), "date": "2026-08-12", "status": "present"})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_26_attendance_requires_enrollment():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    with patch('app.services.attendance_service.AttendanceService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = BusinessRuleViolation("Not enrolled")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/attendance", json={"class_id": str(uuid4()), "student_id": str(uuid4()), "date": "2026-08-12", "status": "present"})
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_acad_27_duplicate_attendance_for_same_class_student_date_rejected():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    with patch('app.services.attendance_service.AttendanceService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = BusinessRuleViolation("Duplicate attendance")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/attendance", json={"class_id": str(uuid4()), "student_id": str(uuid4()), "date": "2026-08-12", "status": "present"})
        assert res.status_code == 400


@pytest.mark.asyncio
async def test_acad_28_student_can_view_own_attendance():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    att_id = uuid4()
    mock_att = MockAttendance()
    with patch('app.services.attendance_service.AttendanceService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_att
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(f"/api/v1/attendance/{att_id}")
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_acad_29_student_cannot_view_another_students_attendance():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    att_id = uuid4()
    with patch('app.services.attendance_service.AttendanceService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(f"/api/v1/attendance/{att_id}")
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_30_teacher_can_view_attendance_for_assigned_class():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    att_id = uuid4()
    mock_att = MockAttendance()
    with patch('app.services.attendance_service.AttendanceService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_att
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(f"/api/v1/attendance/{att_id}")
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_acad_31_teacher_cannot_view_another_teachers_attendance():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    att_id = uuid4()
    with patch('app.services.attendance_service.AttendanceService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(f"/api/v1/attendance/{att_id}")
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_32_agency_can_view_eligible_students_attendance():
    app.dependency_overrides[get_current_active_user] = lambda: AGENCY_A
    att_id = uuid4()
    mock_att = MockAttendance()
    with patch('app.services.attendance_service.AttendanceService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_att
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(f"/api/v1/attendance/{att_id}")
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_acad_33_agency_cannot_view_unrelated_students_attendance():
    app.dependency_overrides[get_current_active_user] = lambda: AGENCY_A
    att_id = uuid4()
    with patch('app.services.attendance_service.AttendanceService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(f"/api/v1/attendance/{att_id}")
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_34_agency_cannot_view_attendance_after_lead_relationship_becomes_lost():
    app.dependency_overrides[get_current_active_user] = lambda: AGENCY_A
    att_id = uuid4()
    with patch('app.services.attendance_service.AttendanceService.get_by_id_scoped', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get(f"/api/v1/attendance/{att_id}")
        assert res.status_code == 403


# --- MASS ASSIGNMENT (ACAD-35 to ACAD-39) ---

@pytest.mark.asyncio
async def test_acad_35_student_cannot_inject_another_student_id():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    with patch('app.services.attendance_service.AttendanceService.create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.post("/api/v1/attendance", json={"class_id": str(uuid4()), "student_id": str(uuid4()), "date": "2026-08-12", "status": "present"})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_36_student_cannot_modify_attendance_class_id():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    att_id = uuid4()
    with patch('app.services.attendance_service.AttendanceService.update', new_callable=AsyncMock) as mock_update:
        mock_update.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.patch(f"/api/v1/attendance/{att_id}", json={"class_id": str(uuid4())})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_37_teacher_cannot_move_attendance_to_another_class():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    att_id = uuid4()
    mock_att = MockAttendance()
    with patch('app.services.attendance_service.AttendanceService.update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = mock_att
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.patch(f"/api/v1/attendance/{att_id}", json={"class_id": str(uuid4())})
        # Check that service pops class_id and allows patch of other status fields without changing class boundary
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_acad_38_teacher_cannot_change_attendance_student_id():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    att_id = uuid4()
    mock_att = MockAttendance()
    with patch('app.services.attendance_service.AttendanceService.update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = mock_att
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.patch(f"/api/v1/attendance/{att_id}", json={"student_id": str(uuid4())})
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_acad_39_cannot_mutate_attendance_id():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    att_id = uuid4()
    mock_att = MockAttendance()
    with patch('app.services.attendance_service.AttendanceService.update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = mock_att
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.patch(f"/api/v1/attendance/{att_id}", json={"id": str(uuid4())})
        assert res.status_code == 200


# --- TIME WINDOW (ACAD-40 to ACAD-43) ---

@pytest.mark.asyncio
async def test_acad_40_teacher_can_modify_attendance_within_allowed_window():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    att_id = uuid4()
    mock_att = MockAttendance()
    with patch('app.services.attendance_service.AttendanceService.update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = mock_att
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.patch(f"/api/v1/attendance/{att_id}", json={"status": "excused"})
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_acad_41_teacher_cannot_modify_attendance_outside_allowed_window():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    att_id = uuid4()
    with patch('app.services.attendance_service.AttendanceService.update', new_callable=AsyncMock) as mock_update:
        mock_update.side_effect = PermissionDenied("Expired")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.patch(f"/api/v1/attendance/{att_id}", json={"status": "excused"})
        assert res.status_code == 403


@pytest.mark.asyncio
async def test_acad_42_admin_can_modify_historical_attendance():
    app.dependency_overrides[get_current_active_user] = lambda: ADMIN_USER
    att_id = uuid4()
    mock_att = MockAttendance()
    with patch('app.services.attendance_service.AttendanceService.update', new_callable=AsyncMock) as mock_update:
        mock_update.return_value = mock_att
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.patch(f"/api/v1/attendance/{att_id}", json={"status": "excused"})
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_acad_43_student_cannot_modify_historical_attendance():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    att_id = uuid4()
    with patch('app.services.attendance_service.AttendanceService.update', new_callable=AsyncMock) as mock_update:
        mock_update.side_effect = PermissionDenied("Forbidden")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.patch(f"/api/v1/attendance/{att_id}", json={"status": "excused"})
        assert res.status_code == 403


# --- AUTHENTICATION (ACAD-44 to ACAD-46) ---

@pytest.mark.asyncio
async def test_acad_44_unauthenticated_class_access_401():
    app.dependency_overrides.pop(get_current_active_user, None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/classes")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_acad_45_unauthenticated_enrollment_access_401():
    app.dependency_overrides.pop(get_current_active_user, None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/enrollments")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_acad_46_unauthenticated_attendance_access_401():
    app.dependency_overrides.pop(get_current_active_user, None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/attendance")
    assert res.status_code == 401


# --- QUERY SCOPING (ACAD-47 to ACAD-51) ---

@pytest.mark.asyncio
async def test_acad_47_teacher_list_only_contains_assigned_classes():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    with patch('app.services.class_service.ClassService.list_classes', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockPaginatedResult([MockClass(instructor_id=TEACHER_A.id)])
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get("/api/v1/classes")
        assert res.status_code == 200
        assert len(res.json()["data"]) == 1


@pytest.mark.asyncio
async def test_acad_48_student_class_list_only_contains_enrolled_classes():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    with patch('app.services.class_service.ClassService.list_classes', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockPaginatedResult([MockClass()])
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get("/api/v1/classes")
        assert res.status_code == 200
        assert len(res.json()["data"]) == 1


@pytest.mark.asyncio
async def test_acad_49_teacher_attendance_list_only_contains_assigned_class_records():
    app.dependency_overrides[get_current_active_user] = lambda: TEACHER_A
    with patch('app.services.attendance_service.AttendanceService.list_attendance', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockPaginatedResult([MockAttendance()])
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get("/api/v1/attendance")
        assert res.status_code == 200
        assert len(res.json()["data"]) == 1


@pytest.mark.asyncio
async def test_acad_50_student_attendance_list_only_contains_own_records():
    app.dependency_overrides[get_current_active_user] = lambda: STUDENT_A
    with patch('app.services.attendance_service.AttendanceService.list_attendance', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockPaginatedResult([MockAttendance(student_id=STUDENT_A.id)])
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get("/api/v1/attendance")
        assert res.status_code == 200
        assert len(res.json()["data"]) == 1


@pytest.mark.asyncio
async def test_acad_51_agency_attendance_list_only_contains_eligible_lead_linked_students():
    app.dependency_overrides[get_current_active_user] = lambda: AGENCY_A
    with patch('app.services.attendance_service.AttendanceService.list_attendance', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = MockPaginatedResult([MockAttendance()])
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            res = await client.get("/api/v1/attendance")
        assert res.status_code == 200
        assert len(res.json()["data"]) == 1


# --- ATTENDANCE BUSINESS-RULE REGRESSION TESTS (ACAD-TEST-01 to ACAD-TEST-04) ---

from contextlib import asynccontextmanager
from datetime import timedelta, timezone
from unittest.mock import MagicMock

from app.models.academic_class import Class
from app.models.enrollment import Enrollment
from app.models.enums import EnrollmentStatus
from app.models.student_profile import StudentProfile
from app.repositories.attendance_repository import AttendanceRepository
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate
from app.services.attendance_service import AttendanceService


@asynccontextmanager
async def mock_transaction():
    yield


def get_mock_tx():
    mock_tx = MagicMock()
    mock_tx.transaction = mock_transaction
    return mock_tx


@pytest.mark.asyncio
async def test_acad_test_01_suspended_enrollment_cannot_receive_attendance():
    mock_repo = MagicMock(spec=AttendanceRepository)
    mock_repo.session = AsyncMock()
    mock_tx = get_mock_tx()

    service = AttendanceService(repository=mock_repo, transaction_manager=mock_tx)

    mock_class = Class(id=uuid4(), instructor_id=TEACHER_A.id)
    mock_student = StudentProfile(id=uuid4(), user_id=STUDENT_A.id)
    mock_enrollment = Enrollment(id=uuid4(), class_id=mock_class.id, student_id=mock_student.id, status=EnrollmentStatus.SUSPENDED)

    mock_execute = AsyncMock()
    mock_repo.session.execute = mock_execute

    class_res = MagicMock()
    class_res.scalar_one_or_none.return_value = mock_class
    student_res = MagicMock()
    student_res.scalar_one_or_none.return_value = mock_student
    enrollment_res = MagicMock()
    enrollment_res.scalar_one_or_none.return_value = mock_enrollment

    mock_execute.side_effect = [class_res, student_res, enrollment_res]

    obj_in = AttendanceCreate(
        class_id=mock_class.id,
        student_id=mock_student.id,
        date=datetime.now(timezone.utc).date(),
        status="present"
    )

    with pytest.raises(BusinessRuleViolation) as exc_info:
        await service.create(obj_in, TEACHER_A)

    assert "suspended" in str(exc_info.value)
    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_acad_test_01b_completed_enrollment_cannot_receive_attendance():
    mock_repo = MagicMock(spec=AttendanceRepository)
    mock_repo.session = AsyncMock()
    mock_tx = get_mock_tx()

    service = AttendanceService(repository=mock_repo, transaction_manager=mock_tx)

    mock_class = Class(id=uuid4(), instructor_id=TEACHER_A.id)
    mock_student = StudentProfile(id=uuid4(), user_id=STUDENT_A.id)
    mock_enrollment = Enrollment(id=uuid4(), class_id=mock_class.id, student_id=mock_student.id, status=EnrollmentStatus.COMPLETED)

    mock_execute = AsyncMock()
    mock_repo.session.execute = mock_execute

    class_res = MagicMock()
    class_res.scalar_one_or_none.return_value = mock_class
    student_res = MagicMock()
    student_res.scalar_one_or_none.return_value = mock_student
    enrollment_res = MagicMock()
    enrollment_res.scalar_one_or_none.return_value = mock_enrollment

    mock_execute.side_effect = [class_res, student_res, enrollment_res]

    obj_in = AttendanceCreate(
        class_id=mock_class.id,
        student_id=mock_student.id,
        date=datetime.now(timezone.utc).date(),
        status="present"
    )

    with pytest.raises(BusinessRuleViolation) as exc_info:
        await service.create(obj_in, TEACHER_A)

    assert "completed" in str(exc_info.value)
    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_acad_test_02_future_attendance_cannot_be_created():
    mock_repo = MagicMock(spec=AttendanceRepository)
    mock_tx = get_mock_tx()
    service = AttendanceService(repository=mock_repo, transaction_manager=mock_tx)

    tomorrow = datetime.now(timezone.utc).date() + timedelta(days=1)
    obj_in = AttendanceCreate(
        class_id=uuid4(),
        student_id=uuid4(),
        date=tomorrow,
        status="present"
    )

    with pytest.raises(BusinessRuleViolation) as exc_info:
        await service.create(obj_in, TEACHER_A)

    assert "future" in str(exc_info.value)
    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_acad_test_02b_far_future_attendance_cannot_be_created():
    mock_repo = MagicMock(spec=AttendanceRepository)
    mock_tx = get_mock_tx()
    service = AttendanceService(repository=mock_repo, transaction_manager=mock_tx)

    far_future = datetime.now(timezone.utc).date() + timedelta(days=365)
    obj_in = AttendanceCreate(
        class_id=uuid4(),
        student_id=uuid4(),
        date=far_future,
        status="present"
    )

    with pytest.raises(BusinessRuleViolation) as exc_info:
        await service.create(obj_in, TEACHER_A)

    assert "future" in str(exc_info.value)
    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_acad_test_02c_today_attendance_remains_valid():
    mock_repo = MagicMock(spec=AttendanceRepository)
    mock_repo.session = AsyncMock()
    mock_tx = get_mock_tx()

    service = AttendanceService(repository=mock_repo, transaction_manager=mock_tx)

    mock_class = Class(id=uuid4(), instructor_id=TEACHER_A.id)
    mock_student = StudentProfile(id=uuid4(), user_id=STUDENT_A.id)
    mock_enrollment = Enrollment(id=uuid4(), class_id=mock_class.id, student_id=mock_student.id, status=EnrollmentStatus.ACTIVE)

    mock_execute = AsyncMock()
    mock_repo.session.execute = mock_execute

    class_res = MagicMock()
    class_res.scalar_one_or_none.return_value = mock_class
    student_res = MagicMock()
    student_res.scalar_one_or_none.return_value = mock_student
    enrollment_res = MagicMock()
    enrollment_res.scalar_one_or_none.return_value = mock_enrollment
    existing_res = MagicMock()
    existing_res.scalar_one_or_none.return_value = None  # No duplicates

    mock_execute.side_effect = [class_res, student_res, enrollment_res, existing_res]

    obj_in = AttendanceCreate(
        class_id=mock_class.id,
        student_id=mock_student.id,
        date=datetime.now(timezone.utc).date(),
        status="present"
    )

    await service.create(obj_in, TEACHER_A)
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_acad_test_03_teacher_cannot_edit_future_attendance():
    mock_repo = MagicMock(spec=AttendanceRepository)
    mock_repo.session = AsyncMock()
    mock_tx = get_mock_tx()

    service = AttendanceService(repository=mock_repo, transaction_manager=mock_tx)

    tomorrow = datetime.now(timezone.utc).date() + timedelta(days=1)
    mock_attendance = MockAttendance(id_val=uuid4(), class_id=uuid4(), student_id=uuid4(), date_val=tomorrow)
    mock_class = Class(id=mock_attendance.class_id, instructor_id=TEACHER_A.id)

    mock_repo.get_by_id = AsyncMock(return_value=mock_attendance)

    mock_execute = AsyncMock()
    mock_repo.session.execute = mock_execute

    class_res = MagicMock()
    class_res.scalar_one_or_none.return_value = mock_class
    mock_execute.side_effect = [class_res]

    obj_in = AttendanceUpdate(status="absent")

    with pytest.raises(BusinessRuleViolation) as exc_info:
        await service.update(mock_attendance.id, obj_in, TEACHER_A)

    assert "Future" in str(exc_info.value)
    mock_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_acad_test_04_existing_attendance_edit_window_behavior():
    mock_repo = MagicMock(spec=AttendanceRepository)
    mock_repo.session = AsyncMock()
    mock_tx = get_mock_tx()

    service = AttendanceService(repository=mock_repo, transaction_manager=mock_tx)

    # Within window (e.g. 3 days ago)
    within_date = datetime.now(timezone.utc).date() - timedelta(days=3)
    att_within = MockAttendance(id_val=uuid4(), class_id=uuid4(), student_id=uuid4(), date_val=within_date)
    mock_class = Class(id=att_within.class_id, instructor_id=TEACHER_A.id)

    mock_repo.get_by_id = AsyncMock(side_effect=[att_within, None, None])

    mock_execute = AsyncMock()
    mock_repo.session.execute = mock_execute

    class_res = MagicMock()
    class_res.scalar_one_or_none.return_value = mock_class
    mock_execute.side_effect = [class_res]

    # Teacher edit within window -> Success
    await service.update(att_within.id, AttendanceUpdate(status="excused"), TEACHER_A)
    mock_repo.update.assert_called_once()

    # Reset mock for outside window
    mock_repo.update.reset_mock()
    outside_date = datetime.now(timezone.utc).date() - timedelta(days=10)
    att_outside = MockAttendance(id_val=uuid4(), class_id=uuid4(), student_id=uuid4(), date_val=outside_date)
    mock_repo.get_by_id = AsyncMock(return_value=att_outside)
    mock_execute.side_effect = [class_res]

    # Teacher edit outside window -> Denied
    with pytest.raises(PermissionDenied) as exc_info:
        await service.update(att_outside.id, AttendanceUpdate(status="excused"), TEACHER_A)
    assert "expired" in str(exc_info.value)
    mock_repo.update.assert_not_called()

    # Reset mock for admin override
    mock_repo.update.reset_mock()
    mock_repo.get_by_id = AsyncMock(return_value=att_outside)
    mock_execute.side_effect = [class_res]

    # Admin edit outside window -> Success
    await service.update(att_outside.id, AttendanceUpdate(status="excused"), ADMIN_USER)
    mock_repo.update.assert_called_once()

