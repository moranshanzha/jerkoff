from flask import render_template, Blueprint
from flask_login import current_user, login_required

from app.main import bp


@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return render_template('main/dashboard.html', title='仪表板')
    return render_template('main/index.html', title='首页')


@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('main/dashboard.html', title='仪表板')
