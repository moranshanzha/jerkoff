from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, mail
from app.models import User
from app.auth.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from flask_mail import Message
import secrets
import string
from datetime import datetime, timedelta


bp = Blueprint('auth', __name__)

def generate_token(length=32):
    """生成随机令牌"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

def send_verification_email(user):
    """发送验证邮件"""
    token = generate_token()
    user.verification_token = token
    db.session.commit()
    
    msg = Message('验证您的邮箱',
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f'''请点击以下链接验证您的邮箱：
{url_for('auth.verify_email', token=token, _external=True)}

如果您没有创建账号，请忽略此邮件。
'''    
    mail.send(msg)

def send_reset_email(user):
    """发送密码重置邮件"""
    token = generate_token()
    user.reset_token = token
    user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()
    
    msg = Message('重置您的密码',
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f'''请点击以下链接重置您的密码：
{url_for('auth.reset_password', token=token, _external=True)}

如果您没有请求重置密码，请忽略此邮件。
'''    
    mail.send(msg)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_verification_email(user)
        flash('注册成功！请检查您的邮箱以验证账号。', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='注册', form=form)


@bp.route('/verify/<token>')
def verify_email(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.query.filter_by(verification_token=token).first()
    if user is None:
        flash('无效或已过期的验证令牌', 'danger')
        return redirect(url_for('auth.login'))
    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    flash('您的邮箱已验证成功！现在可以登录了。', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('无效的邮箱或密码', 'danger')
            return redirect(url_for('auth.login'))
        if not user.is_verified:
            flash('您的邮箱尚未验证，请检查您的邮箱', 'warning')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.index'))
    return render_template('auth/login.html', title='登录', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash('如果您的邮箱已注册，您将收到密码重置链接', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html', title='重置密码', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.query.filter_by(reset_token=token).first()
    if user is None or user.reset_token_expiration < datetime.utcnow():
        flash('无效或已过期的重置令牌', 'danger')
        return redirect(url_for('auth.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()
        flash('您的密码已重置成功！现在可以登录了。', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', title='重置密码', form=form)
