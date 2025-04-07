from app.models import User, Group

def test_group_creation(client, db):
    # Register and login
    client.post('/register', data={
        'username': 'testuser',
        'password': 'Pass1234',
        'confirm_password': 'Pass1234'
    }
                )

    # Create group
    response = client.post('/groups', data={
        'name': 'Test Group',
        'description': 'Test Description'
    }, follow_redirects=True
                           )

    assert b'Group created' in response.data

def test_group_deletion_permissions(client, db):
    # Create group with owner
    client.post('/groups',
        data={
            'name': 'Test Group',
            'description': 'Test Description'
        }
    )

    client.post('/groups', data={...})
    # Login as non-owner
    client.post('/register',
                data={
                    'username': 'user2',
                    'password': 'Pass1234',
                    'confirm_password': 'Pass1234'
                }
                )
    response = client.post('/groups', data={'remove_group': 1})
    assert b'Permission denied' in response.data


def test_member_management(client, db):
    # Create group
    group = Group(name='Test Group')
    db.session.add(group)
    db.session.commit()

    # Use group.id in URL
    response = client.post(f'/group/{group.id}/manage',
                           data={'new_member_username': 'user2'}
                           )
    assert b'Added user2' in response.data

    # Remove member
    response = client.post(f'/group/{group.id}/manage',
                           data={'remove_member_username': 'user2'}
                           )
    assert b'Removed user2' in response.data