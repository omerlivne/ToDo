from app.models import User, Group

def test_admin_permission_escalation(client, db):
    # Create users
    owner = User(username='owner', password='Pass1234')
    user2 = User(username='user2', password='Pass1234')
    db.session.add_all([owner, user2])
    db.session.commit()

    # Create group
    group = Group(name='Test Group')
    db.session.add(group)
    group.add_member(owner.id, role=2)
    db.session.commit()

    # Login as owner
    client.post('/login', data={
        'username': 'owner',
        'password': 'Pass1234'
    })

    # Update permissions using checkbox name format
    response = client.post(f'/group/{group.id}/manage',
        data={'admins': str(user2.id)},  # Send as string
        follow_redirects=True
    )
    assert b'Group permission updated' in response.data

def test_member_permission_restrictions(client, db):
    # Regular member tries to edit group settings
    # Create group
    group = Group(name='Test Group')
    db.session.add(group)
    db.session.commit()

    response = client.post(f'/group/{group.id}/manage', data={'name': 'Hacked'})
    assert b'Permission denied' in response.data