
# fix app/api/v1/users.py
with open('app/api/v1/users.py', 'r') as f:
    content = f.read()

content = content.replace('await service.get(id)', 'await service.get_by_id(id)')
with open('app/api/v1/users.py', 'w') as f:
    f.write(content)

# fix tests/api/test_users.py
with open('tests/api/test_users.py', 'r') as f:
    test_content = f.read()

test_content = test_content.replace('app.services.base.BaseService.get', 'app.services.base.BaseService.get_by_id')

with open('tests/api/test_users.py', 'w') as f:
    f.write(test_content)
