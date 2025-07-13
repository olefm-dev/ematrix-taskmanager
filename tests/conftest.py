import os
import sys
import tempfile
import pytest

# Add the parent directory to sys.path to make app importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

from app import create_app, db
from app.models.user import User


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF protection for testing
    })

    # Create the database and the database tables
    with app.app_context():
        db.create_all()
        
        # Create a test admin user
        admin_user = User(username='admin', is_admin=True)
        admin_user.set_password('password')
        db.session.add(admin_user)
        
        # Create a regular test user
        regular_user = User(username='user', is_admin=False)
        regular_user.set_password('password')
        db.session.add(regular_user)
        
        db.session.commit()

    yield app

    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def auth(client):
    """Authentication helper for tests."""
    class AuthActions:
        def login(self, username='admin', password='password'):
            return client.post(
                '/login',
                data={'username': username, 'password': password},
                follow_redirects=True
            )
            
        def logout(self):
            return client.get('/logout', follow_redirects=True)
    
    return AuthActions()
