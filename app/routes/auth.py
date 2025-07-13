from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from app.models import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

def is_first_run():
    """Check if this is first run (no users exist)"""
    return User.query.count() == 0

@auth_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    # Only allow access if we're in first run mode
    if not is_first_run():
        return redirect(url_for('tasks.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('setup.html', now=datetime.now())
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('setup.html', now=datetime.now())
            
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('setup.html', now=datetime.now())
            
        # Create the user
        user = User(username=username)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log the user in
        login_user(user)
        
        flash('Setup complete! Welcome to Eisenhower Matrix Task Manager', 'success')
        return redirect(url_for('tasks.index'))
    
    return render_template('setup.html', now=datetime.now())

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If this is first run, redirect to setup
    if is_first_run():
        return redirect(url_for('auth.setup'))
        
    # If user is already logged in, redirect to index
    if current_user.is_authenticated:
        return redirect(url_for('tasks.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html', now=datetime.now())
            
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return render_template('login.html', now=datetime.now())
            
        login_user(user, remember=remember)
        return redirect(url_for('tasks.index'))
    
    return render_template('login.html', now=datetime.now())

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
