from fastapi import APIRouter

from app.api.v1 import (
    admin,
    agencies,
    attendance,
    auth,
    classes,
    enrollments,
    leads,
    scholarships,
    students,
    users,
    universities,
)

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(students.router, prefix="/student-profiles", tags=["Student Profiles"])
api_router.include_router(agencies.router, prefix="/agencies", tags=["Agencies"])
api_router.include_router(
    scholarships.router, prefix="/scholarships", tags=["Scholarships"]
)
api_router.include_router(
    universities.router, prefix="/universities", tags=["Universities"]
)
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(classes.router, prefix="/classes", tags=["Classes"])
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["Enrollments"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
