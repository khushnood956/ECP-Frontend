import pytest
import uuid
from unittest.mock import AsyncMock
from app.models.scholarship import Scholarship
from app.services.scholarship_service import ScholarshipService
from app.services.exceptions import BusinessRuleViolation

@pytest.fixture
def scholarship_repo_mock():
    return AsyncMock()

@pytest.fixture
def scholarship_service(scholarship_repo_mock, mock_transaction_manager):
    return ScholarshipService(repository=scholarship_repo_mock, transaction_manager=mock_transaction_manager)

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
