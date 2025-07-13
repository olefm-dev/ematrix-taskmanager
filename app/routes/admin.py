from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app.models import db
from app.models.user import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def check_admin():
    """Ensure that only admin users can access admin routes"""
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)  # Forbidden

@admin_bp.route('/')
@login_required
def index():
    """Admin dashboard"""
    users = User.query.all()
    return render_template('admin/index.html', users=users)

@admin_bp.route('/users')
@login_required
def list_users():
    """List all users"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """Create a new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('admin.create_user'))
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('admin.create_user'))
        
        # Create new user
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            is_admin=is_admin
        )
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {username} created successfully', 'success')
        return redirect(url_for('admin.list_users'))
    
    return render_template('admin/create_user.html')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit an existing user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form
        
        if not username:
            flash('Username is required', 'error')
            return redirect(url_for('admin.edit_user', user_id=user.id))
        
        # Check if username is taken by another user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user.id:
            flash('Username already exists', 'error')
            return redirect(url_for('admin.edit_user', user_id=user.id))
        
        user.username = username
        user.is_admin = is_admin
        
        # Only update password if provided
        if password:
            user.password_hash = generate_password_hash(password)
        
        db.session.commit()
        flash(f'User {username} updated successfully', 'success')
        return redirect(url_for('admin.list_users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'error')
        return redirect(url_for('admin.list_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} deleted successfully', 'success')
    return redirect(url_for('admin.list_users'))
