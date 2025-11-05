from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import current_user, login_required
from app import db
from app.models import Log
from app.logs.forms import LogForm, SearchForm
from datetime import datetime


bp = Blueprint('logs', __name__)


@bp.route('/logs')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    logs = Log.query.filter_by(user_id=current_user.id)
        .order_by(Log.updated_at.desc())
        .paginate(page=page, per_page=10)
    return render_template('logs/index.html', title='日志列表', logs=logs)


@bp.route('/logs/new', methods=['GET', 'POST'])
@login_required
def create_log():
    form = LogForm()
    if form.validate_on_submit():
        log = Log(title=form.title.data, 
                  content=form.content.data, 
                  tags=form.tags.data,
                  author=current_user)
        db.session.add(log)
        db.session.commit()
        flash('日志创建成功！', 'success')
        return redirect(url_for('logs.index'))
    return render_template('logs/create.html', title='创建日志', form=form)


@bp.route('/logs/<int:log_id>')
@login_required
def view_log(log_id):
    log = Log.query.get_or_404(log_id)
    if log.author != current_user:
        flash('您无权查看此日志', 'danger')
        return redirect(url_for('logs.index'))
    return render_template('logs/view.html', title='查看日志', log=log)


@bp.route('/logs/<int:log_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_log(log_id):
    log = Log.query.get_or_404(log_id)
    if log.author != current_user:
        flash('您无权编辑此日志', 'danger')
        return redirect(url_for('logs.index'))
    form = LogForm()
    if form.validate_on_submit():
        log.title = form.title.data
        log.content = form.content.data
        log.tags = form.tags.data
        log.updated_at = datetime.utcnow()
        db.session.commit()
        flash('日志更新成功！', 'success')
        return redirect(url_for('logs.view_log', log_id=log.id))
    elif request.method == 'GET':
        form.title.data = log.title
        form.content.data = log.content
        form.tags.data = log.tags
    return render_template('logs/edit.html', title='编辑日志', form=form)


@bp.route('/logs/<int:log_id>/delete', methods=['POST'])
@login_required
def delete_log(log_id):
    log = Log.query.get_or_404(log_id)
    if log.author != current_user:
        flash('您无权删除此日志', 'danger')
        return redirect(url_for('logs.index'))
    db.session.delete(log)
    db.session.commit()
    flash('日志删除成功！', 'success')
    return redirect(url_for('logs.index'))


@bp.route('/logs/search')
@login_required
def search_logs():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    
    logs = Log.query.filter_by(user_id=current_user.id)
    if query:
        logs = logs.filter(Log.title.contains(query) | Log.content.contains(query) | Log.tags.contains(query))
    
    logs = logs.order_by(Log.updated_at.desc()).paginate(page=page, per_page=10)
    return render_template('logs/index.html', title='搜索结果', logs=logs, query=query)
