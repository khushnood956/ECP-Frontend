import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_transaction_manager
from app.dependencies.repositories import (
    get_user_repository,
    get_lead_repository,
    get_agency_repository
)
from app.dependencies.services import get_user_service, get_lead_service

def test_dependency_providers_return_correct_services_and_share_session():
    # Verify repository providers receive same AsyncSession
    mock_session = AsyncMock(spec=AsyncSession)
    
    user_repo = get_user_repository(mock_session)
    lead_repo = get_lead_repository(mock_session)
    agency_repo = get_agency_repository(mock_session)
    
    assert user_repo.session is mock_session
    assert lead_repo.session is mock_session
    assert agency_repo.session is mock_session
    
    # Verify TransactionManager shares request session
    tm = get_transaction_manager(mock_session)
    assert tm.session is mock_session
    
    # Verify dependency providers return correct services
    user_service = get_user_service(repository=user_repo, transaction_manager=tm)
    assert user_service.repository is user_repo
    assert user_service.transaction_manager is tm
    
    # Verify LeadService receives both repositories correctly
    lead_service = get_lead_service(
        repository=lead_repo,
        agency_repository=agency_repo,
        transaction_manager=tm
    )
    assert lead_service.repository is lead_repo
    assert lead_service.agency_repository is agency_repo
    assert lead_service.transaction_manager is tm
