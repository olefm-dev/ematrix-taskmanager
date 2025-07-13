import pytest
from app.models import db
from app.models.user import User
from app.models.task import Task
from app.models.share_link import ShareLink
from datetime import datetime


def test_user_password_hashing():
    """Test password hashing and verification."""
    user = User(username='test')
    user.set_password('password')
    
    # Password should be hashed, not stored in plaintext
    assert user.password_hash != 'password'
    
    # Verify password checking works
    assert user.check_password('password') is True
    assert user.check_password('wrong') is False


def test_user_admin_default(app):
    """Test that is_admin defaults to False."""
    with app.app_context():
        user = User(username='test')
        db.session.add(user)
        db.session.flush()
        assert user.is_admin is False


def test_task_quadrant_validation(app):
    """Test task quadrant validation."""
    with app.app_context():
        # Valid quadrants are 1-4
        task1 = Task(title='Task 1', quadrant=1)
        task2 = Task(title='Task 2', quadrant=2)
        task3 = Task(title='Task 3', quadrant=3)
        task4 = Task(title='Task 4', quadrant=4)
        
        db.session.add_all([task1, task2, task3, task4])
        db.session.flush()
        
        assert task1.quadrant == 1
        assert task2.quadrant == 2
        assert task3.quadrant == 3
        assert task4.quadrant == 4


def test_task_completed_default(app):
    """Test that completed defaults to False."""
    with app.app_context():
        task = Task(title='Test Task')
        db.session.add(task)
        db.session.flush()
        assert task.completed is False


def test_share_link_token_generation(app):
    """Test that share links have unique tokens."""
    with app.app_context():
        link1 = ShareLink(name='Link 1', user_id=1)
        link2 = ShareLink(name='Link 2', user_id=1)
        
        # Add to session to trigger token generation
        db.session.add_all([link1, link2])
        db.session.flush()
        
        # Each link should have a unique token
        assert link1.token != link2.token
        assert link1.token is not None
        assert link2.token is not None
        
        # Tokens should be of reasonable length
        assert len(link1.token) > 8
