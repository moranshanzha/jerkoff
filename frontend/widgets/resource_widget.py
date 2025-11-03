from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QListWidget, QListWidgetItem, QLineEdit, QMessageBox, QFileDialog,
                             QSpacerItem, QSizePolicy, QFrame, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QIcon
import requests
import os
import math
from frontend.session import get_session_cookies

class UploadThread(QThread):
    upload_progress = pyqtSignal(int)
    upload_finished = pyqtSignal(bool, str)
    
    def __init__(self, file_path, resource_type, cookies):
        super().__init__()
        self.file_path = file_path
        self.resource_type = resource_type
        self.cookies = cookies
    
    def run(self):
        try:
            # 获取文件大小
            file_size = os.path.getsize(self.file_path)
            
            # 检查文件大小（10MB限制）
            if file_size > 10 * 1024 * 1024:
                self.upload_finished.emit(False, '文件大小不能超过10MB')
                return
                
            # 检查文件格式
            allowed_formats = {
                'skin': ['.jpg', '.jpeg', '.png', '.bmp'],
                'model': ['.obj', '.fbx', '.dae', '.stl']
            }
            
            file_ext = os.path.splitext(self.file_path)[1].lower()
            if file_ext not in allowed_formats.get(self.resource_type, []):
                self.upload_finished.emit(False, f'不支持的文件格式。支持的格式: {', '.join(allowed_formats.get(self.resource_type, []))}')
                return
                
            # 打开文件并发送请求
            with open(self.file_path, 'rb') as f:
                # 准备请求数据
                files = {'file': (os.path.basename(self.file_path), f)}
                data = {'type': self.resource_type}
                
                # 发送POST请求
                response = requests.post('http://localhost:5000/resource/upload', files=files, data=data,
                                       cookies=self.cookies, stream=True)
                
                if response.status_code == 200:
                    # 处理响应
                    response_json = response.json()
                    if response_json.get('success'):
                        self.upload_finished.emit(True, '资源上传成功')
                    else:
                        self.upload_finished.emit(False, response_json.get('message', '资源上传失败'))
                else:
                    self.upload_finished.emit(False, f'服务器错误: {response.status_code}')
                    
        except Exception as e:
            self.upload_finished.emit(False, f'上传失败: {str(e)}')

class ResourceWidget(QWidget):
    back_button_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.resources = []
        self.upload_thread = None
    
    def init_ui(self):
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 顶部导航
        top_layout = QHBoxLayout()
        
        back_button = QPushButton('返回')
        back_button.setFont(QFont('Arial', 12))
        back_button.setStyleSheet('background-color: #6c757d; color: white; border-radius: 5px; padding: 5px 15px;')
        back_button.clicked.connect(self.back_button_clicked.emit)
        
        top_layout.addWidget(back_button)
        top_layout.addStretch()
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜索资源...')
        self.search_input.setFont(QFont('Arial', 12))
        self.search_input.returnPressed.connect(self.load_resources)
        top_layout.addWidget(self.search_input)
        
        # 搜索按钮
        search_button = QPushButton('搜索')
        search_button.setFont(QFont('Arial', 12))
        search_button.setStyleSheet('background-color: #007bff; color: white; border-radius: 5px; padding: 5px 15px;')
        search_button.clicked.connect(self.load_resources)
        top_layout.addWidget(search_button)
        
        # 上传按钮
        upload_button = QPushButton('上传资源')
        upload_button.setFont(QFont('Arial', 12))
        upload_button.setStyleSheet('background-color: #28a745; color: white; border-radius: 5px; padding: 5px 15px;')
        upload_button.clicked.connect(self.upload_resource)
        top_layout.addWidget(upload_button)
        
        layout.addLayout(top_layout)
        
        # 资源类型选择
        type_layout = QHBoxLayout()
        type_layout.setSpacing(15)
        
        type_label = QLabel('资源类型:')
        type_label.setFont(QFont('Arial', 12))
        type_layout.addWidget(type_label)
        
        self.type_filter = QPushButton('所有资源')
        self.type_filter.setFont(QFont('Arial', 12))
        self.type_filter.setStyleSheet('background-color: #007bff; color: white; border-radius: 5px; padding: 5px 15px;')
        self.type_filter.clicked.connect(lambda: self.load_resources('all'))
        type_layout.addWidget(self.type_filter)
        
        self.skin_filter = QPushButton('皮肤')
        self.skin_filter.setFont(QFont('Arial', 12))
        self.skin_filter.setStyleSheet('background-color: #6c757d; color: white; border-radius: 5px; padding: 5px 15px;')
        self.skin_filter.clicked.connect(lambda: self.load_resources('skin'))
        type_layout.addWidget(self.skin_filter)
        
        self.model_filter = QPushButton('模型')
        self.model_filter.setFont(QFont('Arial', 12))
        self.model_filter.setStyleSheet('background-color: #6c757d; color: white; border-radius: 5px; padding: 5px 15px;')
        self.model_filter.clicked.connect(lambda: self.load_resources('model'))
        type_layout.addWidget(self.model_filter)
        
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # 资源列表
        self.resource_list = QListWidget()
        self.resource_list.setIconSize(self.resource_list.iconSize() * 2)
        layout.addWidget(self.resource_list)
        
        # 上传进度条
        self.upload_progress = QProgressBar()
        self.upload_progress.setVisible(False)
        layout.addWidget(self.upload_progress)
        
        self.setLayout(layout)
    
    def load_resources(self, resource_type='all'):
        self.resource_list.clear()
        try:
            # 更新筛选按钮样式
            buttons = [self.type_filter, self.skin_filter, self.model_filter]
            for btn in buttons:
                btn.setStyleSheet('background-color: #6c757d; color: white; border-radius: 5px; padding: 5px 15px;')
                
            if resource_type == 'all':
                self.type_filter.setStyleSheet('background-color: #007bff; color: white; border-radius: 5px; padding: 5px 15px;')
            elif resource_type == 'skin':
                self.skin_filter.setStyleSheet('background-color: #007bff; color: white; border-radius: 5px; padding: 5px 15px;')
            elif resource_type == 'model':
                self.model_filter.setStyleSheet('background-color: #007bff; color: white; border-radius: 5px; padding: 5px 15px;')
                
            # 准备请求参数
            params = {}
            search_query = self.search_input.text().strip()
            if search_query:
                params['search'] = search_query
                
            if resource_type != 'all':
                params['type'] = resource_type
                
            # 发送请求获取资源列表
            response = requests.get('http://localhost:5000/resource/resources', params=params, cookies=self.get_session_cookies())
            
            if response.status_code == 200:
                self.resources = response.json()['resources']
                
                if not self.resources:
                    item = QListWidgetItem('没有找到匹配的资源')
                    item.setFlags(Qt.NoItemFlags)
                    self.resource_list.addItem(item)
                    return
                    
                # 显示资源列表
                for resource in self.resources:
                    # 创建资源项
                    item = QListWidgetItem()
                    
                    # 设置图标
                    if resource.get('type') == 'skin':
                        pixmap = QPixmap(':/icons/skin.png')  # 需要添加皮肤图标资源
                        if pixmap.isNull():
                            icon = QIcon()
                        else:
                            icon = QIcon(pixmap)
                    else:
                        pixmap = QPixmap(':/icons/model.png')  # 需要添加模型图标资源
                        if pixmap.isNull():
                            icon = QIcon()
                        else:
                            icon = QIcon(pixmap)
                    
                    item.setIcon(icon)
                    
                    # 设置显示文本
                    file_name = resource.get('file_name', '未知文件')
                    file_size = self.format_file_size(resource.get('file_size', 0))
                    created_at = resource.get('created_at', '')[:10]
                    item.setText(f"{file_name} - {file_size} - {created_at}")
                    
                    # 设置工具提示
                    tooltip = f"名称: {file_name}\n类型: {resource.get('type')}\n大小: {file_size}\n上传时间: {created_at}"
                    if resource.get('is_active'):
                        tooltip += "\n状态: 已激活"
                    item.setToolTip(tooltip)
                    
                    self.resource_list.addItem(item)
            else:
                QMessageBox.warning(self, '警告', '无法获取资源列表', QMessageBox.Ok)
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, '错误', f'网络连接失败: {str(e)}', QMessageBox.Ok)
    
    def format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        
        size_name = ["B", "KB", "MB", "GB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"
    
    def upload_resource(self):
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(self, '选择资源文件', '',
                                                   '所有支持的文件 (*.jpg *.jpeg *.png *.bmp *.obj *.fbx *.dae *.stl);;
                                                    图片文件 (*.jpg *.jpeg *.png *.bmp);;
                                                    模型文件 (*.obj *.fbx *.dae *.stl)')
        
        if not file_path:
            return
            
        # 让用户选择资源类型
        dialog = QMessageBox(self)
        dialog.setWindowTitle('选择资源类型')
        dialog.setText('请选择上传的资源类型:')
        dialog.setStandardButtons(QMessageBox.NoButton)
        
        skin_button = dialog.addButton('皮肤', QMessageBox.ActionRole)
        model_button = dialog.addButton('模型', QMessageBox.ActionRole)
        cancel_button = dialog.addButton(QMessageBox.Cancel)
        
        dialog.exec_()
        
        if dialog.clickedButton() == skin_button:
            resource_type = 'skin'
        elif dialog.clickedButton() == model_button:
            resource_type = 'model'
        else:
            return
            
        # 创建上传线程
        self.upload_thread = UploadThread(file_path, resource_type, self.get_session_cookies())
        self.upload_thread.upload_progress.connect(self.update_upload_progress)
        self.upload_thread.upload_finished.connect(self.upload_finished)
        self.upload_thread.start()
        
        # 显示进度条
        self.upload_progress.setVisible(True)
        self.upload_progress.setValue(0)
    
    @pyqtSlot(int)
    def update_upload_progress(self, progress):
        self.upload_progress.setValue(progress)
    
    @pyqtSlot(bool, str)
    def upload_finished(self, success, message):
        self.upload_progress.setVisible(False)
        
        if success:
            QMessageBox.information(self, '成功', message, QMessageBox.Ok)
            self.load_resources()  # 刷新资源列表
        else:
            QMessageBox.warning(self, '失败', message, QMessageBox.Ok)
    
    def get_session_cookies(self):
        # 从会话管理模块获取会话信息
        return get_session_cookies()
