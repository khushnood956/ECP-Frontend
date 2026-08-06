import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from app.models.enums import LeadStatus
from app.models.lead import Lead
from app.services.exceptions import BusinessRuleViolation, EntityNotFound
from app.services.lead_service import LeadService


@pytest.fixture
def lead_repo_mock():
    return AsyncMock()


@pytest.fixture
def agency_repo_mock():
    return AsyncMock()


@pytest.fixture
def lead_service(lead_repo_mock, agency_repo_mock, mock_transaction_manager):
    return LeadService(
        repository=lead_repo_mock,
        agency_repository=agency_repo_mock,
        transaction_manager=mock_transaction_manager,
    )


@pytest.mark.asyncio
async def test_assign_nonexistent_agency(
    lead_service, lead_repo_mock, agency_repo_mock
):
    lead_id = uuid.uuid4()
    agency_id = uuid.uuid4()
    lead_repo_mock.get_by_id.return_value = Lead(id=lead_id)
    agency_repo_mock.get_by_id.return_value = None

    with pytest.raises(EntityNotFound, match="does not exist"):
        await lead_service.assign_agency(lead_id, agency_id)


@pytest.mark.asyncio
async def test_follow_up_date_in_past(lead_service, lead_repo_mock):
    lead_id = uuid.uuid4()
    past_date = datetime.now(timezone.utc) - timedelta(days=1)

    with pytest.raises(BusinessRuleViolation, match="in the past"):
        await lead_service.schedule_follow_up(lead_id, past_date)


@pytest.mark.asyncio
async def test_duplicate_status_transition(lead_service, lead_repo_mock):
    lead_id = uuid.uuid4()
    mock_lead = Lead(id=lead_id, status=LeadStatus.CONTACTED)
    lead_repo_mock.get_by_id.return_value = mock_lead

    with pytest.raises(BusinessRuleViolation, match="already in status"):
        await lead_service.update_status(lead_id, LeadStatus.CONTACTED)

@pytest.mark.asyncio
async def test_lead_creation(lead_service, lead_repo_mock):
    lead_data = {"student_id": uuid.uuid4(), "scholarship_id": uuid.uuid4()}
    lead_repo_mock.list.return_value = []
    lead_repo_mock.create.return_value = Lead(id=uuid.uuid4())
    
    result = await lead_service.create(lead_data)
    assert result is not None

@pytest.mark.asyncio
async def test_duplicate_lead_detection(lead_service, lead_repo_mock):
    lead_data = {"student_id": uuid.uuid4(), "scholarship_id": uuid.uuid4()}
    lead_repo_mock.list.return_value = [Lead(id=uuid.uuid4())]
    
    with pytest.raises(BusinessRuleViolation, match="Lead already exists"):
        await lead_service.create(lead_data)
