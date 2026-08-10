from fastapi import APIRouter

from app.api.v1 import agencies, auth, leads, scholarships, students, users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(students.router, prefix="/student-profiles", tags=["Student Profiles"])
api_router.include_router(agencies.router, prefix="/agencies", tags=["Agencies"])
api_router.include_router(
    scholarships.router, prefix="/scholarships", tags=["Scholarships"]
)
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
