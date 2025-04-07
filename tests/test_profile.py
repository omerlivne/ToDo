def test_username_update(client, db):
    # Register and login
    client.post('/register', data={
        'username': 'testuser',
        'password': 'Pass1234',
        'confirm_password': 'Pass1234'
    }
                )

    # Update profile
    response = client.post('/profile', data={
        'username': 'newusername'
    }, follow_redirects=True
                           )

    assert b'Profile updated' in response.data


def test_password_update(client, db):
    # Login
    client.post('/profile', data={
        'password': 'NewPass1234',
        'confirm_password': 'NewPass1234'
    })
    # Verify new password works
    client.get('/logout')
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'NewPass1234'
    })
    assert response.status_code == 302