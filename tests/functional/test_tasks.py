import pytest
from app.models import db
from app.models.task import Task
from app.models.user import User
from datetime import datetime, timedelta


def test_index_page_requires_login(client):
    """Test that the index page redirects to login when not authenticated."""
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location


def test_index_page_with_login(client, auth):
    """Test that the index page loads correctly when authenticated."""
    auth.login()
    response = client.get('/')
    assert response.status_code == 200
    # Check for title in the page
    assert b'Eisenhower Matrix Task Manager' in response.data
    # Check for quadrant indicators - these might be different from what we expect
    # based on the actual HTML structure
    assert b'quadrant-1' in response.data or b'Quadrant 1' in response.data
    assert b'quadrant-2' in response.data or b'Quadrant 2' in response.data
    assert b'quadrant-3' in response.data or b'Quadrant 3' in response.data
    assert b'quadrant-4' in response.data or b'Quadrant 4' in response.data


def test_create_task(client, auth, app):
    """Test creating a new task."""
    auth.login()
    
    due_date = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = client.post(
        '/tasks/create',
        data={
            'title': 'Test Task',
            'description': 'This is a test task',
            'quadrant': '1',
            'due_date': due_date
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    # Verify the task was created in the database
    with app.app_context():
        task = Task.query.filter_by(title='Test Task').first()
        assert task is not None
        assert task.description == 'This is a test task'
        assert task.quadrant == 1


def test_complete_task(client, auth, app):
    """Test marking a task as complete."""
    auth.login()
    
    # First, create a task
    with app.app_context():
        user_id = User.query.filter_by(username='admin').first().id
        task = Task(
            title='Task to Complete',
            description='This task will be completed',
            quadrant=1,
            user_id=user_id
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id
    
    # Now mark it as complete
    response = client.post(
        f'/tasks/{task_id}/complete',
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    # Verify the task is marked as complete in the database
    with app.app_context():
        task = Task.query.get(task_id)
        assert task.completed is True


def test_delete_task(client, auth, app):
    """Test deleting a task."""
    auth.login()
    
    # First, create a task
    with app.app_context():
        user_id = User.query.filter_by(username='admin').first().id
        task = Task(
            title='Task to Delete',
            description='This task will be deleted',
            quadrant=1,
            user_id=user_id
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id
    
    # Now delete it
    response = client.post(
        f'/tasks/{task_id}/delete',
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    # Verify the task is deleted from the database
    with app.app_context():
        task = Task.query.get(task_id)
        assert task is None


def test_update_task(client, auth, app):
    """Test updating a task."""
    auth.login()
    
    # First, create a task
    with app.app_context():
        user_id = User.query.filter_by(username='admin').first().id
        task = Task(
            title='Original Title',
            description='Original description',
            quadrant=1,
            user_id=user_id
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id
    
    # Now update it
    due_date = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')
    response = client.post(
        f'/tasks/{task_id}/update',
        data={
            'title': 'Updated Title',
            'description': 'Updated description',
            'quadrant': '2',
            'due_date': due_date
        },
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    # Verify the task was updated in the database
    with app.app_context():
        task = Task.query.get(task_id)
        assert task.title == 'Updated Title'
        assert task.description == 'Updated description'
        assert task.quadrant == 2
