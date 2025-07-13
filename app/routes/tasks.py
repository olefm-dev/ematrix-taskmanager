from flask import Blueprint, render_template, request, redirect, url_for, abort, flash
from flask_login import login_required, current_user
from datetime import datetime

from app.models import db
from app.models.task import Task
from app.models.share_link import ShareLink

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/')
@login_required
def index():
    # Get regular tasks organized by quadrant
    tasks = {
        1: Task.query.filter_by(user_id=current_user.id, quadrant=1, completed=False).all(),
        2: Task.query.filter_by(user_id=current_user.id, quadrant=2, completed=False).all(),
        3: Task.query.filter_by(user_id=current_user.id, quadrant=3, completed=False).all(),
        4: Task.query.filter_by(user_id=current_user.id, quadrant=4, completed=False).all()
    }
    
    # Get requested tasks from share links
    requested_tasks = Task.query.join(ShareLink).filter(
        Task.is_requested == True,
        ShareLink.user_id == current_user.id
    ).all()
    
    return render_template('index.html', tasks=tasks, requested_tasks=requested_tasks, now=datetime.now())

@tasks_bp.route('/tasks/create', methods=['POST'])
@login_required
def create_task():
    title = request.form.get('title')
    description = request.form.get('description')
    quadrant = int(request.form.get('quadrant', 1))
    due_date_str = request.form.get('due_date')
    
    if not title:
        flash('Title is required', 'error')
        return redirect(url_for('tasks.index'))
    
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('tasks.index'))
    
    task = Task(
        title=title,
        description=description,
        quadrant=quadrant,
        due_date=due_date,
        user_id=current_user.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/tasks/<int:task_id>/update', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Ensure the task belongs to the user
    if task.user_id != current_user.id:
        abort(403)
    
    # Check if this is just a quadrant update (from drag and drop)
    if 'quadrant' in request.form and 'title' not in request.form:
        quadrant = int(request.form.get('quadrant', 1))
        task.quadrant = quadrant
        db.session.commit()
        return redirect(url_for('tasks.index'))
    
    # Full task update
    title = request.form.get('title')
    description = request.form.get('description')
    quadrant = int(request.form.get('quadrant', 1))
    due_date_str = request.form.get('due_date')
    
    if not title:
        flash('Title is required', 'error')
        return redirect(url_for('tasks.index'))
    
    task.title = title
    task.description = description
    task.quadrant = quadrant
    
    if due_date_str:
        try:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('tasks.index'))
    else:
        task.due_date = None
    
    db.session.commit()
    
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Ensure the task belongs to the user
    if task.user_id != current_user.id:
        abort(403)
    
    task.completed = True
    db.session.commit()
    
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Check permissions based on task type
    if task.is_requested and task.share_link:
        if task.share_link.user_id != current_user.id:
            abort(403)
    # For regular tasks, check if the task belongs to the user
    elif task.user_id != current_user.id:
        abort(403)
        
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('tasks.index'))

@tasks_bp.route('/completed')
@login_required
def completed_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id, completed=True).order_by(Task.updated_at.desc()).all()
    return render_template('completed.html', tasks=tasks, now=datetime.now())

@tasks_bp.route('/tasks/<int:task_id>/accept', methods=['POST'])
@login_required
def accept_requested_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Ensure the task is from one of the user's share links
    if not task.share_link or task.share_link.user_id != current_user.id:
        abort(403)
        
    task.is_requested = False
    task.quadrant = int(request.form.get('quadrant', 1))
    task.user_id = current_user.id  # Assign the task to the current user
    db.session.commit()
    return redirect(url_for('tasks.index'))
