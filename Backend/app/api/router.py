from fastapi import APIRouter

# Import sub-routers here when they are implemented
# from app.api.v1 import users, agencies, admin

api_router = APIRouter()

# Example router registration (commented out until modules are created)
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(agencies.router, prefix="/agencies", tags=["agencies"])
# api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
