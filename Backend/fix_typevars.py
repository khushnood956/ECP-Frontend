import os

files = [
    'app/services/interfaces.py',
    'app/services/base.py',
    'app/services/agency_service.py',
    'app/services/lead_service.py',
    'app/services/scholarship_service.py',
    'app/services/student_service.py',
    'app/services/user_service.py'
]

for filepath in files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace('ModelType', 'ModelType_co')
        content = content.replace('CreateSchemaType', 'CreateSchemaType_contra')
        content = content.replace('UpdateSchemaType', 'UpdateSchemaType_contra')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
