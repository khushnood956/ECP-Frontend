import uuid
from unittest.mock import AsyncMock

import pytest

from app.models.agency import Agency
from app.models.enums import AgencyVerificationStatus
from app.services.agency_service import AgencyService
from app.services.exceptions import BusinessRuleViolation


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
    agency_repo_mock.get_by_registration_number.return_value = None
    agency_repo_mock.create.return_value = Agency(id=uuid.uuid4())
    
    result = await agency_service.create(agency_data)
    assert result is not None

@pytest.mark.asyncio
async def test_duplicate_agency_handling(agency_service, agency_repo_mock):
    agency_data = {"registration_number": "123"}
    agency_repo_mock.get_by_registration_number.return_value = Agency(id=uuid.uuid4())
    
    with pytest.raises(BusinessRuleViolation, match="already exists"):
        await agency_service.create(agency_data)
