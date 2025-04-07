from app.models import Group, User, UserGroup


def test_task_creation_with_valid_due_date(client, db):
    user = User(username='testuser', password='Pass1234')
    group = Group(name='Test Group')

    # Add member correctly
    membership = UserGroup(
        user_id=user.id,
        group_id=group.id,  # Provide both IDs
        role=2
    )
    db.session.add(membership)
    db.session.commit()

def test_past_due_date_validation(client, db):
    # Create group
    group = Group(name='Test Group')
    db.session.add(group)
    db.session.commit()

    response = client.post(f'/group/{group.id}/tasks', data={
        'due_date': '2020-01-01T00:00'
    })
    assert b'cannot be in the past' in response.data

def test_task_deletion_permissions(client, db):
    # Create task as user1
    # Login as user2 (non-admin)
    # Create group
    group = Group(name='Test Group')
    db.session.add(group)
    db.session.commit()

    response = client.post(f'/group/{group.id}/tasks',
        data={'delete_task': 1})
    assert b'Unauthorized' in response.data