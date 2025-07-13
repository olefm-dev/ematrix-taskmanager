from flask import Flask
from flask_login import LoginManager
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix

from app.models import db
from app.models.user import User
from app.config import config

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Apply security middleware
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize Talisman for security headers
    talisman = Talisman(app, content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", 'https://cdn.tailwindcss.com', "'unsafe-inline'"],
        'style-src': ["'self'", 'https://cdn.tailwindcss.com', "'unsafe-inline'"],
    }, force_https=True)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.tasks import tasks_bp
    from app.routes.share_links import share_links_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(share_links_bp)
    
    return app