from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, send_from_directory
from flask_login import login_required, current_user
from app import db, app
from app.models import Resource
from datetime import datetime
import os
from werkzeug.utils import secure_filename

bp = Blueprint('resource', __name__)

# 检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@bp.route('/resources')
@login_required
def resources():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 处理搜索和过滤
    search_query = request.args.get('search', '')
    type_filter = request.args.get('type', '')
    
    query = Resource.query.filter_by(user_id=current_user.id)
    
    if search_query:
        query = query.filter(
            Resource.name.ilike(f'%{search_query}%') | \
            Resource.description.ilike(f'%{search_query}%')
        )
    
    if type_filter:
        query = query.filter(Resource.file_type == type_filter)
    
    resources = query.order_by(Resource.uploaded_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # 获取所有文件类型用于过滤
    all_types = Resource.query.filter_by(user_id=current_user.id).with_entities(Resource.file_type).distinct().all()
    all_types = [t[0] for t in all_types if t[0]]
    
    return render_template('resource/resources.html', resources=resources, all_types=all_types, search_query=search_query, type_filter=type_filter)

@bp.route('/resource/upload', methods=['GET', 'POST'])
@login_required
def upload_resource():
    if request.method == 'POST':
        # 检查是否有文件上传
        if 'file' not in request.files:
            flash('请选择一个文件', 'danger')
            return redirect(url_for('resource.upload_resource'))
            
        file = request.files['file']
        
        # 检查文件是否为空
        if file.filename == '':
            flash('请选择一个文件', 'danger')
            return redirect(url_for('resource.upload_resource'))
            
        # 检查文件类型
        if not allowed_file(file.filename):
            flash('不支持的文件类型', 'danger')
            return redirect(url_for('resource.upload_resource'))
            
        # 处理表单数据
        name = request.form.get('name', file.filename.rsplit('.', 1)[0])
        description = request.form.get('description', '')
        
        # 保存文件
        filename = secure_filename(file.filename)
        # 确保上传目录存在
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 获取文件类型
        file_type = filename.rsplit('.', 1)[1].lower()
        
        # 创建资源记录
        resource = Resource(
            name=name,
            description=description,
            file_type=file_type,
            file_path=file_path,
            owner=current_user
        )
        db.session.add(resource)
        db.session.commit()
        
        flash('文件上传成功', 'success')
        return redirect(url_for('resource.resources'))
        
    return render_template('resource/upload_resource.html')

@bp.route('/resource/<int:id>')
@login_required
def view_resource(id):
    resource = Resource.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('resource/view_resource.html', resource=resource)

@bp.route('/resource/<int:id>/download')
@login_required
def download_resource(id):
    resource = Resource.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=os.path.basename(resource.file_path), as_attachment=True)

@bp.route('/resource/<int:id>/delete', methods=['POST'])
@login_required
def delete_resource(id):
    resource = Resource.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # 删除文件
    if os.path.exists(resource.file_path):
        try:
            os.remove(resource.file_path)
        except OSError:
            flash('文件删除失败，但资源记录已删除', 'warning')
    
    # 删除数据库记录
    db.session.delete(resource)
    db.session.commit()
    flash('资源已删除', 'success')
    return redirect(url_for('resource.resources'))

@bp.route('/resource/<int:id>/activate', methods=['POST'])
@login_required
def activate_resource(id):
    resource = Resource.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # 取消所有其他资源的激活状态
    Resource.query.filter_by(user_id=current_user.id, is_active=True).update({'is_active': False})
    
    # 激活当前资源
    resource.is_active = True
    db.session.commit()
    
    flash(f'已激活资源: {resource.name}', 'success')
    return redirect(url_for('resource.resources'))
