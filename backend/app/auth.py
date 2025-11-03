from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, ConfirmationToken, ResetPasswordRequest
from app.email import send_email
import re
import uuid
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__)

# 密码强度检测
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

def validate_password(password):
    return PASSWORD_REGEX.match(password) is not None

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        # 验证表单数据
        if not username or not email or not password or not confirm_password:
            flash('请填写所有必填字段', 'danger')
            return redirect(url_for('auth.register'))
            
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('auth.register'))
            
        if not validate_password(password):
            flash('密码必须包含至少8个字符，包括大写字母、小写字母、数字和特殊字符', 'danger')
            return redirect(url_for('auth.register'))
            
        # 检查用户是否已存在
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('该邮箱已被注册', 'danger')
            return redirect(url_for('auth.register'))
            
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('该用户名已被使用', 'danger')
            return redirect(url_for('auth.register'))
            
        # 创建新用户
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # 创建确认令牌
        token = uuid.uuid4().hex
        confirmation_token = ConfirmationToken(user_id=new_user.id, token=token)
        db.session.add(confirmation_token)
        db.session.commit()
        
        # 发送确认邮件
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        send_email(
            subject='请确认您的邮箱',
            recipients=[new_user.email],
            template='email/confirm',
            user=new_user,
            confirm_url=confirm_url
        )
        
        flash('注册成功！请检查您的邮箱以确认账户', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@bp.route('/confirm/<token>')
def confirm_email(token):
    confirmation_token = ConfirmationToken.query.filter_by(token=token).first()
    
    if not confirmation_token:
        flash('确认链接无效或已过期', 'danger')
        return redirect(url_for('auth.login'))
        
    # 检查令牌是否过期（24小时内有效）
    if datetime.utcnow() - confirmation_token.created_at > timedelta(days=1):
        flash('确认链接已过期', 'danger')
        return redirect(url_for('auth.login'))
        
    user = confirmation_token.user
    if user.confirmed:
        flash('该账户已被确认', 'info')
        return redirect(url_for('main.index'))
        
    user.confirmed = True
    user.confirmed_on = datetime.utcnow()
    db.session.commit()
    
    flash('邮箱确认成功！您现在可以登录了', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')
        remember = data.get('remember') == 'on'
        
        if not email or not password:
            flash('请填写所有必填字段', 'danger')
            return redirect(url_for('auth.login'))
            
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('无效的邮箱或密码', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.confirmed:
            flash('您的邮箱尚未确认，请检查您的邮箱', 'warning')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=remember)
        return redirect(url_for('main.index'))
        
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功登出', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        
        if not email:
            flash('请输入您的邮箱', 'danger')
            return redirect(url_for('auth.reset_password_request'))
            
        user = User.query.filter_by(email=email).first()
        if user:
            # 创建重置令牌
            token = uuid.uuid4().hex
            reset_request = ResetPasswordRequest(user_id=user.id, token=token)
            db.session.add(reset_request)
            db.session.commit()
            
            # 发送重置邮件
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_email(
                subject='重置您的密码',
                recipients=[user.email],
                template='email/reset_password',
                user=user,
                reset_url=reset_url
            )
            
        flash('如果您的邮箱已注册，我们已发送了一封重置密码的邮件', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password_request.html')

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    reset_request = ResetPasswordRequest.query.filter_by(token=token).first()
    
    if not reset_request:
        flash('重置链接无效或已过期', 'danger')
        return redirect(url_for('auth.login'))
        
    # 检查令牌是否过期（1小时内有效）
    if datetime.utcnow() - reset_request.created_at > timedelta(hours=1):
        flash('重置链接已过期', 'danger')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        data = request.form
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not password or not confirm_password:
            flash('请填写所有必填字段', 'danger')
            return redirect(url_for('auth.reset_password', token=token))
            
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('auth.reset_password', token=token))
            
        if not validate_password(password):
            flash('密码必须包含至少8个字符，包括大写字母、小写字母、数字和特殊字符', 'danger')
            return redirect(url_for('auth.reset_password', token=token))
            
        user = reset_request.user
        user.set_password(password)
        db.session.commit()
        
        flash('您的密码已成功重置', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', token=token)
