def update_user_tests():
    with open('tests/services/test_user_service.py', 'a') as f:
        f.write('''

@pytest.mark.asyncio
async def test_create_user_success(user_service, user_repo_mock):
    user_data = {"email": "test@test.com", "role": "student"}
    user_repo_mock.get_by_email.return_value = None
    user_repo_mock.create.return_value = User(id=uuid.uuid4(), email="test@test.com")
    
    result = await user_service.create(user_data)
    assert result.email == "test@test.com"

@pytest.mark.asyncio
async def test_duplicate_email_rejected(user_service, user_repo_mock):
    user_data = {"email": "test@test.com", "role": "student"}
    user_repo_mock.get_by_email.return_value = User(id=uuid.uuid4(), email="test@test.com")
    
    with pytest.raises(BusinessRuleViolation, match="Email already exists"):
        await user_service.create(user_data)

@pytest.mark.asyncio
async def test_invalid_role_rejected(user_service, user_repo_mock):
    user_data = {"email": "new@test.com", "role": "invalid"}
    user_repo_mock.get_by_email.return_value = None
    
    with pytest.raises(BusinessRuleViolation, match="Invalid role"):
        await user_service.create(user_data)
''')

def update_student_tests():
    with open('tests/services/test_student_service.py', 'a') as f:
        f.write('''
from app.services.exceptions import BusinessRuleViolation

@pytest.mark.asyncio
async def test_create_student_success(student_service, student_repo_mock):
    user_id = uuid.uuid4()
    student_data = {"user_id": user_id}
    student_repo_mock.get_by_user_id.return_value = None
    student_repo_mock.create.return_value = {"id": uuid.uuid4(), "user_id": user_id}
    
    result = await student_service.create(student_data)
    assert result is not None

@pytest.mark.asyncio
async def test_duplicate_student_prevented(student_service, student_repo_mock):
    user_id = uuid.uuid4()
    student_data = {"user_id": user_id}
    student_repo_mock.get_by_user_id.return_value = {"id": uuid.uuid4(), "user_id": user_id}
    
    with pytest.raises(BusinessRuleViolation, match="already exists"):
        await student_service.create(student_data)

@pytest.mark.asyncio
async def test_missing_related_entity(student_service, student_repo_mock):
    student_data = {"user_id": None}
    
    with pytest.raises(EntityNotFound, match="not found"):
        await student_service.create(student_data)
''')

def update_agency_tests():
    with open('tests/services/test_agency_service.py', 'a') as f:
        f.write('''
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
''')

def update_scholarship_tests():
    with open('tests/services/test_scholarship_service.py', 'a') as f:
        f.write('''
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
''')

def update_lead_tests():
    with open('tests/services/test_lead_service.py', 'a') as f:
        f.write('''
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
''')

def update_transaction_tests():
    # Transaction tests are already in test_transaction.py, let's append our required ones just in case
    with open('tests/services/test_transaction.py', 'a') as f:
        f.write('''
@pytest.mark.asyncio
async def test_multiple_repo_operations_commit(mock_transaction_manager):
    async with mock_transaction_manager.transaction():
        pass
    mock_transaction_manager.session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_exception_triggers_rollback(mock_transaction_manager):
    class CustomException(Exception): pass
    try:
        async with mock_transaction_manager.transaction():
            raise CustomException("test")
    except CustomException:
        pass
    mock_transaction_manager.session.rollback.assert_called_once()
''')

if __name__ == '__main__':
    update_user_tests()
    update_student_tests()
    update_agency_tests()
    update_scholarship_tests()
    update_lead_tests()
    update_transaction_tests()
