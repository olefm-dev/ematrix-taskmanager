import pytest
from app.models.user import User
from app.models import db


def test_admin_access(client, auth):
    """Test that admin users can access the admin panel."""
    auth.login(username='admin', password='password')
    response = client.get('/admin/')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data


def test_non_admin_access_denied(client, auth):
    """Test that non-admin users cannot access the admin panel."""
    auth.login(username='user', password='password')
    response = client.get('/admin/')
    assert response.status_code == 403  # Forbidden


def test_user_listing(client, auth):
    """Test that admin users can see the user listing."""
    auth.login(username='admin', password='password')
    response = client.get('/admin/users')
    assert response.status_code == 200
    assert b'User Management' in response.data
    assert b'admin' in response.data
    assert b'user' in response.data


def test_create_user(client, auth, app):
    """Test creating a new user through the admin panel."""
    auth.login(username='admin', password='password')
    
    # Omit is_admin field entirely to test non-admin creation
    response = client.post(
        '/admin/users/create',
        data={
            'username': 'newuser',
            'password': 'newpassword'
            # is_admin field omitted = not an admin
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    # Verify the user was created in the database
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.is_admin is False


def test_edit_user(client, auth, app):
    """Test editing a user through the admin panel."""
    auth.login(username='admin', password='password')
    
    # First, get the user ID
    with app.app_context():
        user = User.query.filter_by(username='user').first()
        user_id = user.id
    
    response = client.post(
        f'/admin/users/{user_id}/edit',
        data={
            'username': 'updateduser',
            'password': 'newpassword',
            'is_admin': 'on'  # Make them an admin
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    # Verify the user was updated in the database
    with app.app_context():
        user = User.query.get(user_id)
        assert user.username == 'updateduser'
        assert user.is_admin is True


def test_delete_user(client, auth, app):
    """Test deleting a user through the admin panel."""
    auth.login(username='admin', password='password')
    
    # First, create a user to delete
    with app.app_context():
        user_to_delete = User(username='deleteme', is_admin=False)
        user_to_delete.set_password('password')
        db.session.add(user_to_delete)
        db.session.commit()
        user_id = user_to_delete.id
    
    response = client.post(
        f'/admin/users/{user_id}/delete',
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    # Verify the user was deleted from the database
    with app.app_context():
        user = User.query.get(user_id)
        assert user is None
