import uuid
from unittest.mock import AsyncMock

import pytest

from app.models.scholarship import Scholarship
from app.services.exceptions import BusinessRuleViolation
from app.services.scholarship_service import ScholarshipService


@pytest.fixture
def scholarship_repo_mock():
    return AsyncMock()


@pytest.fixture
def scholarship_service(scholarship_repo_mock, mock_transaction_manager):
    return ScholarshipService(
        repository=scholarship_repo_mock, transaction_manager=mock_transaction_manager
    )


@pytest.mark.asyncio
async def test_publish_twice_fails(scholarship_service, scholarship_repo_mock):
    sch_id = uuid.uuid4()
    mock_sch = Scholarship(id=sch_id, is_active=True)
    scholarship_repo_mock.get_by_id.return_value = mock_sch

    with pytest.raises(BusinessRuleViolation, match="already published"):
        await scholarship_service.publish(sch_id)


@pytest.mark.asyncio
async def test_unpublish_twice_fails(scholarship_service, scholarship_repo_mock):
    sch_id = uuid.uuid4()
    mock_sch = Scholarship(id=sch_id, is_active=False)
    scholarship_repo_mock.get_by_id.return_value = mock_sch

    with pytest.raises(BusinessRuleViolation, match="already unpublished"):
        await scholarship_service.unpublish(sch_id)

import datetime


@pytest.mark.asyncio
async def test_create_scholarship(scholarship_service, scholarship_repo_mock):
    sch_data = {"agency_id": uuid.uuid4(), "deadline": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10)}
    scholarship_repo_mock.create.return_value = Scholarship(id=uuid.uuid4())
    
    result = await scholarship_service.create(sch_data)
    assert result is not None

@pytest.mark.asyncio
async def test_expired_scholarship_validation(scholarship_service, scholarship_repo_mock):
    sch_data = {"agency_id": uuid.uuid4(), "deadline": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=10)}
    
    with pytest.raises(BusinessRuleViolation, match="cannot be in the past"):
        await scholarship_service.create(sch_data)

@pytest.mark.asyncio
async def test_invalid_agency_validation(scholarship_service, scholarship_repo_mock):
    sch_data = {"agency_id": None, "deadline": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10)}
    
    with pytest.raises(BusinessRuleViolation, match="Invalid agency"):
        await scholarship_service.create(sch_data)
