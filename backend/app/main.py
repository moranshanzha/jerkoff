from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Journal, Resource
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    # 获取用户的最新日志和资源
    latest_journals = Journal.query.filter_by(user_id=current_user.id).order_by(Journal.created_at.desc()).limit(5).all()
    latest_resources = Resource.query.filter_by(user_id=current_user.id).order_by(Resource.uploaded_at.desc()).limit(5).all()
    
    return render_template('main/dashboard.html', latest_journals=latest_journals, latest_resources=latest_resources)

@bp.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html')

@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    data = request.form
    username = data.get('username')
    email = data.get('email')
    
    if not username or not email:
        flash('请填写所有必填字段', 'danger')
        return redirect(url_for('main.profile'))
        
    # 检查用户名是否已被使用
    existing_user = User.query.filter_by(username=username).first()
    if existing_user and existing_user.id != current_user.id:
        flash('该用户名已被使用', 'danger')
        return redirect(url_for('main.profile'))
        
    # 检查邮箱是否已被使用
    existing_email = User.query.filter_by(email=email).first()
    if existing_email and existing_email.id != current_user.id:
        flash('该邮箱已被注册', 'danger')
        return redirect(url_for('main.profile'))
        
    current_user.username = username
    current_user.email = email
    db.session.commit()
    
    flash('个人资料已更新', 'success')
    return redirect(url_for('main.profile'))
