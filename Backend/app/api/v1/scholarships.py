from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.common.schemas.responses import SuccessResponse
from app.common.utils.responses import success_response
from app.dependencies.services import get_scholarship_service
from app.models.enums import DegreeLevel, FundingType
from app.schemas.scholarship import (
    ScholarshipCreate,
    ScholarshipResponse,
    ScholarshipUpdate,
)
from app.services.scholarship_service import ScholarshipService

router = APIRouter()


@router.post(
    "",
    response_model=SuccessResponse[ScholarshipResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a scholarship",
)
async def create_scholarship(
    scholarship_in: ScholarshipCreate,
    service: ScholarshipService = Depends(get_scholarship_service),
):
    scholarship = await service.create(scholarship_in)
    return success_response(
        data=ScholarshipResponse.model_validate(scholarship),
        message="Scholarship created successfully",
        status_code=201,
    )


@router.get(
    "/active",
    response_model=SuccessResponse[list[ScholarshipResponse]],
    summary="Get active scholarships",
)
async def get_active_scholarships(
    service: ScholarshipService = Depends(get_scholarship_service),
):
    scholarships = await service.get_active_scholarships()
    data = [ScholarshipResponse.model_validate(s) for s in scholarships]
    return success_response(
        data=data, message="Active scholarships retrieved successfully"
    )


@router.get(
    "/search",
    response_model=SuccessResponse[list[ScholarshipResponse]],
    summary="Search scholarships",
)
async def search_scholarships(
    country: str | None = None,
    degree_level: DegreeLevel | None = None,
    funding_type: FundingType | None = None,
    service: ScholarshipService = Depends(get_scholarship_service),
):
    scholarships = await service.search_scholarships(
        country=country,
        degree_level=degree_level.value if degree_level else None,
        funding_type=funding_type.value if funding_type else None,
    )
    data = [ScholarshipResponse.model_validate(s) for s in scholarships]
    return success_response(data=data, message="Scholarships retrieved successfully")


@router.get(
    "/{id}",
    response_model=SuccessResponse[ScholarshipResponse],
    summary="Get a scholarship by ID",
)
async def get_scholarship(
    id: UUID, service: ScholarshipService = Depends(get_scholarship_service)
):
    scholarship = await service.get(id)
    return success_response(
        data=ScholarshipResponse.model_validate(scholarship),
        message="Scholarship retrieved successfully",
    )


@router.get(
    "",
    response_model=SuccessResponse[list[ScholarshipResponse]],
    summary="Get all scholarships",
)
async def get_scholarships(
    skip: int = 0,
    limit: int = 100,
    service: ScholarshipService = Depends(get_scholarship_service),
):
    scholarships, total = await service.get_all(skip=skip, limit=limit)
    data = [ScholarshipResponse.model_validate(s) for s in scholarships]
    return success_response(data=data, message="Scholarships retrieved successfully")


@router.patch(
    "/{id}",
    response_model=SuccessResponse[ScholarshipResponse],
    summary="Update a scholarship",
)
async def update_scholarship(
    id: UUID,
    scholarship_in: ScholarshipUpdate,
    service: ScholarshipService = Depends(get_scholarship_service),
):
    scholarship = await service.update(id, scholarship_in)
    return success_response(
        data=ScholarshipResponse.model_validate(scholarship),
        message="Scholarship updated successfully",
    )


@router.delete("/{id}", response_model=SuccessResponse, summary="Delete a scholarship")
async def delete_scholarship(
    id: UUID, service: ScholarshipService = Depends(get_scholarship_service)
):
    await service.delete(id)
    return success_response(message="Scholarship deleted successfully")


@router.post(
    "/{id}/publish",
    response_model=SuccessResponse[ScholarshipResponse],
    summary="Publish a scholarship",
)
async def publish_scholarship(
    id: UUID, service: ScholarshipService = Depends(get_scholarship_service)
):
    scholarship = await service.publish(id)
    return success_response(
        data=ScholarshipResponse.model_validate(scholarship),
        message="Scholarship published successfully",
    )


@router.post(
    "/{id}/unpublish",
    response_model=SuccessResponse[ScholarshipResponse],
    summary="Unpublish a scholarship",
)
async def unpublish_scholarship(
    id: UUID, service: ScholarshipService = Depends(get_scholarship_service)
):
    scholarship = await service.unpublish(id)
    return success_response(
        data=ScholarshipResponse.model_validate(scholarship),
        message="Scholarship unpublished successfully",
    )
