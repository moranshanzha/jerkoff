from flask import render_template, url_for, flash, redirect, request, Blueprint, send_from_directory
from flask_login import current_user, login_required
from app import app, db
from app.models import Resource
from app.resources.forms import ResourceForm
import os
import uuid
from werkzeug.utils import secure_filename


bp = Blueprint('resources', __name__)

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_file_extension(filename):
    """获取文件扩展名"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


@bp.route('/resources')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    resources = Resource.query.filter_by(user_id=current_user.id)
        .order_by(Resource.created_at.desc())
        .paginate(page=page, per_page=10)
    return render_template('resources/index.html', title='资源管理', resources=resources)


@bp.route('/resources/upload', methods=['GET', 'POST'])
@login_required
def upload_resource():
    form = ResourceForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            # 使用UUID确保文件名唯一
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # 保存文件
            file.save(file_path)
            
            # 创建资源记录
            resource = Resource(
                filename=unique_filename,
                original_filename=filename,
                file_type=form.file_type.data,
                file_extension=get_file_extension(filename),
                size=os.path.getsize(file_path),
                description=form.description.data,
                owner=current_user
            )
            
            db.session.add(resource)
            db.session.commit()
            
            flash('资源上传成功！', 'success')
            return redirect(url_for('resources.index'))
    return render_template('resources/upload.html', title='上传资源', form=form)


@bp.route('/resources/<int:resource_id>')
@login_required
def view_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    if resource.owner != current_user:
        flash('您无权查看此资源', 'danger')
        return redirect(url_for('resources.index'))
    return render_template('resources/view.html', title='资源详情', resource=resource)


@bp.route('/resources/<int:resource_id>/delete', methods=['POST'])
@login_required
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    if resource.owner != current_user:
        flash('您无权删除此资源', 'danger')
        return redirect(url_for('resources.index'))
    
    # 删除文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], resource.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 删除数据库记录
    db.session.delete(resource)
    db.session.commit()
    
    flash('资源删除成功！', 'success')
    return redirect(url_for('resources.index'))


@bp.route('/resources/<int:resource_id>/activate', methods=['POST'])
@login_required
def activate_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    if resource.owner != current_user:
        flash('您无权操作此资源', 'danger')
        return redirect(url_for('resources.index'))
    
    # 取消所有同类型资源的激活状态
    Resource.query.filter_by(user_id=current_user.id, file_type=resource.file_type).update({'is_active': False})
    
    # 激活当前资源
    resource.is_active = True
    db.session.commit()
    
    flash(f'{resource.file_type}已激活！', 'success')
    return redirect(url_for('resources.index'))


@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@bp.route('/resources/preview/<int:resource_id>')
@login_required
def preview_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    if resource.owner != current_user:
        flash('您无权预览此资源', 'danger')
        return redirect(url_for('resources.index'))
    
    return render_template('resources/preview.html', title='资源预览', resource=resource)
