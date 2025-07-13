from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort
from flask_login import login_required, current_user
from datetime import datetime

from app.models import db
from app.models.task import Task
from app.models.share_link import ShareLink

share_links_bp = Blueprint('share_links', __name__)

@share_links_bp.route('/share-links', methods=['GET'])
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

@share_links_bp.route('/share-links', methods=['POST'])
@login_required
def create_share_link():
    # Handle both form data and JSON requests
    if request.is_json:
        data = request.get_json()
        name = data.get('name')
    else:
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

@share_links_bp.route('/share-links/<string:link_id>/url', methods=['GET'])
@login_required
def get_share_link_url(link_id):
    link = ShareLink.query.get_or_404(link_id)
    
    # Ensure the link belongs to the current user
    if link.user_id != current_user.id:
        abort(403)
    
    # Generate the absolute URL for the share link
    share_url = url_for('share_links.share_link_page', link_id=link.id, _external=True)
    return jsonify({'url': share_url})

@share_links_bp.route('/share-links/<string:link_id>/toggle', methods=['POST'])
@login_required
def toggle_share_link(link_id):
    link = ShareLink.query.get_or_404(link_id)
    
    # Ensure the link belongs to the current user
    if link.user_id != current_user.id:
        abort(403)
        
    link.active = not link.active
    db.session.commit()
    
    return jsonify({'active': link.active})

@share_links_bp.route('/share-links/<string:link_id>/delete', methods=['POST'])
@login_required
def delete_share_link(link_id):
    link = ShareLink.query.get_or_404(link_id)
    
    # Ensure the link belongs to the current user
    if link.user_id != current_user.id:
        abort(403)
        
    db.session.delete(link)
    db.session.commit()
    
    return jsonify({'success': True})

@share_links_bp.route('/share/<string:link_id>')
def share_link_page(link_id):
    link = ShareLink.query.get_or_404(link_id)
    
    if not link.active:
        abort(404)
    
    return render_template('share.html', link=link, now=datetime.now())

@share_links_bp.route('/share/<string:link_id>/submit', methods=['POST'])
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
