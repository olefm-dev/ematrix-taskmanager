import pytest
from flask import session


def test_login_page(client):
    """Test that the login page loads correctly."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Username' in response.data
    assert b'Password' in response.data


def test_login_success(client, auth):
    """Test successful login."""
    response = auth.login()
    assert response.status_code == 200
    # After successful login, we should be redirected to the index page
    assert b'Eisenhower Matrix' in response.data


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        '/login',
        data={'username': 'wrong', 'password': 'wrong'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data


def test_logout(client, auth):
    """Test logout functionality."""
    # First login
    auth.login()
    
    # Then logout
    response = auth.logout()
    assert response.status_code == 200
    
    # After logout, we should be redirected to the login page
    assert b'Login' in response.data
    
    # Check that the user is no longer in session
    with client:
        client.get('/')
        assert 'user_id' not in session
