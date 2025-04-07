def test_valid_registration(client, db):
    response = client.post('/register',
        data={
            'username': 'testuser',
            'password': 'Pass1234',
            'confirm_password': 'Pass1234'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Account created!' in response.data


def test_duplicate_username(client, db):
    # First registration
    client.post('/register', data={
        'username': 'testuser',
        'password': 'Pass1234',
        'confirm_password': 'Pass1234'
    }, follow_redirects=True)

    # Second attempt
    response = client.post('/register',
        data={
            'username': 'testuser',
            'password': 'Pass1234',
            'confirm_password': 'Pass1234'
        },
        follow_redirects=True  # Follow redirect to see flash message
    )
    assert b'Username unavailable' in response.data