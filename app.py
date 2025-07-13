from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
from flask_talisman import Talisman
import os
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())
db = SQLAlchemy(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

talisman = Talisman(app, content_security_policy={
    'default-src': "'self'",
    'script-src': ["'self'", 'https://cdn.tailwindcss.com', "'unsafe-inline'"],  # Allow inline for your script.js if needed
    'style-src': ["'self'", 'https://cdn.tailwindcss.com', "'unsafe-inline'"],
}, force_https=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='user', lazy=True)
    share_links = db.relationship('ShareLink', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    quadrant = db.Column(db.Integer, default=1)
    completed = db.Column(db.Boolean, default=False)
    is_requested = db.Column(db.Boolean, default=False)
    share_link_id = db.Column(db.String(36), db.ForeignKey('share_link.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class ShareLink(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    tasks = db.relationship('Task', backref='share_link', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create database tables
with app.app_context():
    # Create all tables if they don't exist
    db.create_all()

# Function to check if this is first run (no users exist)
def is_first_run():
    with app.app_context():
        return User.query.count() == 0

# First run setup route
@app.route('/setup', methods=['GET', 'POST'])
def setup():
    # Only allow access if we're in first run mode
    if not is_first_run():
        return redirect(url_for('index'))
    
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
        
        # Create the first user
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # First run complete
        session.pop('first_run', None)
        
        # Log the user in
        login_user(user)
        flash('Account created successfully! Welcome to Eisenhower Matrix Task Manager.', 'success')
        return redirect(url_for('index'))
    
    return render_template('setup.html', now=datetime.now())


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # If we're in first run mode, redirect to setup
    if is_first_run():
        return redirect(url_for('setup'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', now=datetime.now())


# Logout route
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# Main route with both regular and requested tasks
@app.route('/')
def index():
    # If we're in first run mode, redirect to setup
    if is_first_run():
        return redirect(url_for('setup'))
    
    # If user is not logged in, redirect to login
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    tasks = {
        1: Task.query.filter_by(user_id=current_user.id, quadrant=1, completed=False, is_requested=False).all(),
        2: Task.query.filter_by(user_id=current_user.id, quadrant=2, completed=False, is_requested=False).all(),
        3: Task.query.filter_by(user_id=current_user.id, quadrant=3, completed=False, is_requested=False).all(),
        4: Task.query.filter_by(user_id=current_user.id, quadrant=4, completed=False, is_requested=False).all(),
    }
    
    # Get requested tasks from the user's share links
    share_links = ShareLink.query.filter_by(user_id=current_user.id).all()
    share_link_ids = [link.id for link in share_links]
    requested_tasks = Task.query.filter(Task.share_link_id.in_(share_link_ids), Task.is_requested==True, Task.completed==False).order_by(Task.created_at.desc()).all() if share_link_ids else []
    
    return render_template('index.html', tasks=tasks, requested_tasks=requested_tasks, now=datetime.now())


@app.route('/tasks', methods=['POST'])
@login_required
def create_task():
    title = request.form.get('title')
    description = request.form.get('description')
    quadrant = int(request.form.get('quadrant', 1))
    due_date_str = request.form.get('due_date')
    
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            pass
    
    task = Task(
        title=title,
        description=description,
        quadrant=quadrant,
        due_date=due_date,
        user_id=current_user.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/update', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Ensure the task belongs to the current user
    if task.user_id != current_user.id and not task.is_requested:
        abort(403)
    
    # Check if this is a drag-and-drop quadrant update (only quadrant field provided)
    if 'quadrant' in request.form and len(request.form) == 1:
        task.quadrant = int(request.form.get('quadrant'))
        db.session.commit()
        return redirect(url_for('index'))
    
    # Regular form update with all fields
    task.title = request.form.get('title', task.title)
    task.description = request.form.get('description', task.description)
    task.quadrant = int(request.form.get('quadrant', task.quadrant))
    
    due_date_str = request.form.get('due_date')
    if due_date_str:
        try:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            pass
    
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Ensure the task belongs to the current user
    if task.user_id != current_user.id:
        abort(403)
        
    task.completed = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # For requested tasks, check if the task belongs to one of the user's share links
    if task.is_requested and task.share_link:
        if task.share_link.user_id != current_user.id:
            abort(403)
    # For regular tasks, check if the task belongs to the user
    elif task.user_id != current_user.id:
        abort(403)
        
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/completed')
@login_required
def completed_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id, completed=True).order_by(Task.updated_at.desc()).all()
    return render_template('completed.html', tasks=tasks, now=datetime.now())

# Share link management endpoints
@app.route('/share-links', methods=['GET'])
@login_required
def get_share_links():
    links = ShareLink.query.filter_by(user_id=current_user.id).order_by(ShareLink.created_at.desc()).all()
    return jsonify([{
        'id': link.id,
        'name': link.name,
        'created_at': link.created_at.strftime('%Y-%m-%d %H:%M'),
        'active': link.active,
        'task_count': len(link.tasks)
    } for link in links])

@app.route('/share-links', methods=['POST'])
@login_required
def create_share_link():
    name = request.form.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    link = ShareLink(name=name, user_id=current_user.id)
    db.session.add(link)
    db.session.commit()
    
    return jsonify({
        'id': link.id,
        'name': link.name,
        'created_at': link.created_at.strftime('%Y-%m-%d %H:%M'),
        'active': link.active,
        'task_count': 0
    })

@app.route('/share-links/<string:link_id>/toggle', methods=['POST'])
@login_required
def toggle_share_link(link_id):
    link = ShareLink.query.get_or_404(link_id)
    
    # Ensure the link belongs to the current user
    if link.user_id != current_user.id:
        abort(403)
        
    link.active = not link.active
    db.session.commit()
    
    return jsonify({'active': link.active})

@app.route('/share-links/<string:link_id>/delete', methods=['POST'])
@login_required
def delete_share_link(link_id):
    link = ShareLink.query.get_or_404(link_id)
    
    # Ensure the link belongs to the current user
    if link.user_id != current_user.id:
        abort(403)
        
    db.session.delete(link)
    db.session.commit()
    
    return jsonify({'success': True})

# Public share link page
@app.route('/share/<string:link_id>')
def share_link_page(link_id):
    link = ShareLink.query.get_or_404(link_id)
    
    if not link.active:
        abort(404)
    
    return render_template('share.html', link=link, now=datetime.now())

# Submit task via share link
@app.route('/share/<string:link_id>/submit', methods=['POST'])
def submit_shared_task(link_id):
    link = ShareLink.query.get_or_404(link_id)
    
    if not link.active:
        abort(404)
    
    title = request.form.get('title')
    description = request.form.get('description')
    due_date_str = request.form.get('due_date')
    
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        except ValueError:
            pass
    
    task = Task(
        title=title,
        description=description,
        due_date=due_date,
        is_requested=True,
        share_link_id=link.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    return render_template('share_success.html', link=link, now=datetime.now())

# Add route to accept a requested task
@app.route('/tasks/<int:task_id>/accept', methods=['POST'])
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
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
