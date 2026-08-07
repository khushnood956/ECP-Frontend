import uuid
from unittest.mock import AsyncMock

import pytest

from app.models.agency import Agency
from app.models.enums import AgencyVerificationStatus
from app.services.agency_service import AgencyService
from app.services.exceptions import BusinessRuleViolation, EntityAlreadyExists


@pytest.fixture
def agency_repo_mock():
    return AsyncMock()


@pytest.fixture
def agency_service(agency_repo_mock, mock_transaction_manager):
    return AgencyService(
        repository=agency_repo_mock, transaction_manager=mock_transaction_manager
    )


@pytest.mark.asyncio
async def test_verify_agency_twice_fails(agency_service, agency_repo_mock):
    agency_id = uuid.uuid4()
    mock_agency = Agency(
        id=agency_id, verification_status=AgencyVerificationStatus.VERIFIED
    )
    agency_repo_mock.get_by_id.return_value = mock_agency

    with pytest.raises(BusinessRuleViolation, match="already verified"):
        await agency_service.verify_agency(agency_id)


@pytest.mark.asyncio
async def test_suspend_agency_twice_fails(agency_service, agency_repo_mock):
    agency_id = uuid.uuid4()
    mock_agency = Agency(
        id=agency_id, verification_status=AgencyVerificationStatus.REJECTED
    )
    agency_repo_mock.get_by_id.return_value = mock_agency

    with pytest.raises(BusinessRuleViolation, match="already suspended"):
        await agency_service.suspend_agency(agency_id)

@pytest.mark.asyncio
async def test_agency_creation(agency_service, agency_repo_mock):
    agency_data = {"registration_number": "123"}
    mock_user = AsyncMock()
    mock_user.id = uuid.uuid4()
    mock_user.role = "agency"

    agency_repo_mock.get_by_user_id.return_value = None
    agency_repo_mock.get_by_registration_number.return_value = None
    agency_repo_mock.create.return_value = Agency(id=uuid.uuid4())
    
    result = await agency_service.create(agency_data, mock_user)
    assert result is not None


@pytest.mark.asyncio
async def test_duplicate_agency_handling(agency_service, agency_repo_mock):
    agency_data = {"registration_number": "123"}
    mock_user = AsyncMock()
    mock_user.id = uuid.uuid4()
    mock_user.role = "agency"

    agency_repo_mock.get_by_user_id.return_value = None
    agency_repo_mock.get_by_registration_number.return_value = Agency(id=uuid.uuid4())
    
    with pytest.raises(EntityAlreadyExists, match="already exists"):
        await agency_service.create(agency_data, mock_user)


@pytest.mark.asyncio
async def test_creation_fails_non_agency_role(agency_service, agency_repo_mock):
    agency_data = {"registration_number": "123"}
    mock_user = AsyncMock()
    mock_user.id = uuid.uuid4()
    mock_user.role = "student"

    from app.services.exceptions import PermissionDenied
    with pytest.raises(PermissionDenied, match="Only agency users can create agency profiles"):
        await agency_service.create(agency_data, mock_user)


@pytest.mark.asyncio
async def test_creation_fails_duplicate_user_profile(agency_service, agency_repo_mock):
    agency_data = {"registration_number": "123"}
    mock_user = AsyncMock()
    mock_user.id = uuid.uuid4()
    mock_user.role = "agency"

    agency_repo_mock.get_by_user_id.return_value = Agency(id=uuid.uuid4())

    with pytest.raises(EntityAlreadyExists, match="This user already has an agency profile"):
        await agency_service.create(agency_data, mock_user)

