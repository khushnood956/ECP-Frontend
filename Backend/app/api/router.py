from fastapi import APIRouter

from app.api.v1 import auth, agencies, leads, scholarships, students, users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(agencies.router, prefix="/agencies", tags=["Agencies"])
api_router.include_router(
    scholarships.router, prefix="/scholarships", tags=["Scholarships"]
)
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
