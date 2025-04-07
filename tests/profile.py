from app.models.user import User


def test_profile_update(client, auth, db_session):
    auth.register()
    auth.login()

    # Update username and password
    response = client.post('/profile', data={
        'username': 'updated_user',
        'password': 'NewPass123',
        'confirm_password': 'NewPass123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Profile updated' in response.data

    user = db_session.query(User).filter_by(username='updated_user').first()
    assert user is not None
    assert user.check_password('NewPass123')


def test_invalid_profile_update(client, auth):
    auth.register()
    auth.login()

    # Passwords don't match
    response = client.post('/profile', data={
        'username': 'user',
        'password': 'Pass123',
        'confirm_password': 'Wrong123'
    })

    assert response.status_code == 200
    assert b'Passwords must match' in response.data


def test_duplicate_username_update(client, auth, db_session):
    # Create first user
    auth.register(username='user1')
    auth.logout()

    # Create second user and try to update username to 'user1'
    auth.register(username='user2')
    response = client.post('/profile', data={
        'username': 'user1',  # Already taken
        'password': '',
        'confirm_password': ''
    })

    assert response.status_code == 200
    assert b'Username already taken' in response.data

    # Ensure user2's username didn't change
    user2 = db_session.query(User).filter_by(username='user2').first()
    assert user2 is not None


def test_password_update(client, db):
    # Submit password change
    client.post('/profile',
                data={
                    'password': 'NewPass1234',
                    'confirm_password': 'NewPass1234'
                },
                follow_redirects=True
                )

    # Login with new password
    response = client.post('/login',
                           data={
                               'username': 'testuser',
                               'password': 'NewPass1234'
                           },
                           follow_redirects=True
                           )
    assert b'Welcome' in response.data  # Verify successful login
