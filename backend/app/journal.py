from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Journal, Tag
from datetime import datetime
from sqlalchemy import or_

bp = Blueprint('journal', __name__)

@bp.route('/journals')
@login_required
def journals():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 处理搜索和过滤
    search_query = request.args.get('search', '')
    tag_filter = request.args.get('tag', '')
    date_filter = request.args.get('date', '')
    
    query = Journal.query.filter_by(user_id=current_user.id)
    
    if search_query:
        query = query.filter(
            or_(Journal.title.ilike(f'%{search_query}%'),
                Journal.content.ilike(f'%{search_query}%'))
        )
    
    if tag_filter:
        tag = Tag.query.filter_by(name=tag_filter).first()
        if tag:
            query = query.filter(Journal.tags.contains(tag))
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d')
            query = query.filter(
                db.func.date(Journal.created_at) == filter_date.date()
            )
        except ValueError:
            flash('无效的日期格式', 'warning')
    
    journals = query.order_by(Journal.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # 获取所有标签用于过滤
    all_tags = Tag.query.join(Tag.journals).filter(Journal.user_id == current_user.id).distinct().all()
    
    return render_template('journal/journals.html', journals=journals, all_tags=all_tags, search_query=search_query, tag_filter=tag_filter, date_filter=date_filter)

@bp.route('/journal/create', methods=['GET', 'POST'])
@login_required
def create_journal():
    if request.method == 'POST':
        data = request.form
        title = data.get('title')
        content = data.get('content')
        tags = data.get('tags', '').split(',')
        
        if not title or not content:
            flash('请填写标题和内容', 'danger')
            return redirect(url_for('journal.create_journal'))
            
        # 处理标签
        tag_objects = []
        for tag_name in tags:
            tag_name = tag_name.strip()
            if tag_name:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                tag_objects.append(tag)
        
        # 创建新日志
        journal = Journal(title=title, content=content, author=current_user, tags=tag_objects)
        db.session.add(journal)
        db.session.commit()
        
        flash('日志创建成功', 'success')
        return redirect(url_for('journal.journals'))
        
    return render_template('journal/create_journal.html')

@bp.route('/journal/<int:id>')
@login_required
def view_journal(id):
    journal = Journal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('journal/view_journal.html', journal=journal)

@bp.route('/journal/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_journal(id):
    journal = Journal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        data = request.form
        title = data.get('title')
        content = data.get('content')
        tags = data.get('tags', '').split(',')
        
        if not title or not content:
            flash('请填写标题和内容', 'danger')
            return redirect(url_for('journal.edit_journal', id=id))
            
        # 处理标签
        tag_objects = []
        for tag_name in tags:
            tag_name = tag_name.strip()
            if tag_name:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                tag_objects.append(tag)
        
        # 更新日志
        journal.title = title
        journal.content = content
        journal.updated_at = datetime.utcnow()
        journal.tags = tag_objects
        db.session.commit()
        
        flash('日志更新成功', 'success')
        return redirect(url_for('journal.view_journal', id=id))
        
    # 准备标签字符串
    tag_string = ','.join([tag.name for tag in journal.tags])
    return render_template('journal/edit_journal.html', journal=journal, tag_string=tag_string)

@bp.route('/journal/<int:id>/delete', methods=['POST'])
@login_required
def delete_journal(id):
    journal = Journal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(journal)
    db.session.commit()
    flash('日志已删除', 'success')
    return redirect(url_for('journal.journals'))
