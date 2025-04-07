from app.models import User, Group, Task

def test_user_password_hashing():
    user = User(username='test', password='Pass1234')
    assert user.check_password('Pass1234') is True

def test_group_relationships():
    user = User(username='testuser', password='Pass1234')  # Add password
    group = Group(name='Test Group')
    group.add_member(user.id)
    assert user in group.members

def test_task_status_flow():
    task = Task(...)
    task.status = 'In Progress'
    assert task.status == 'In Progress'