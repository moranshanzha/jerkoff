from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QSpacerItem, QSizePolicy, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
import requests
import os

class ProfileWidget(QWidget):
    back_button_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 顶部导航
        top_layout = QHBoxLayout()
        
        back_button = QPushButton('返回控制台')
        back_button.setFont(QFont('Arial', 12))
        back_button.setStyleSheet('background-color: #6c757d; color: white; border-radius: 5px; padding: 5px 15px;')
        back_button.clicked.connect(self.back_button_clicked.emit)
        
        top_layout.addWidget(back_button)
        top_layout.addStretch()
        
        # 保存按钮
        save_button = QPushButton('保存修改')
        save_button.setFont(QFont('Arial', 12))
        save_button.setStyleSheet('background-color: #28a745; color: white; border-radius: 5px; padding: 5px 15px;')
        save_button.clicked.connect(self.save_profile)
        top_layout.addWidget(save_button)
        
        layout.addLayout(top_layout)
        
        # 用户头像
        avatar_layout = QHBoxLayout()
        
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(150, 150)
        self.avatar_label.setStyleSheet('border: 2px solid #ccc; border-radius: 75px;')
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.load_avatar()
        
        avatar_layout.addStretch()
        avatar_layout.addWidget(self.avatar_label)
        avatar_layout.addStretch()
        layout.addLayout(avatar_layout)
        
        # 更换头像按钮
        change_avatar_button = QPushButton('更换头像')
        change_avatar_button.setFont(QFont('Arial', 12))
        change_avatar_button.setStyleSheet('background-color: #007bff; color: white; border-radius: 5px; padding: 5px 15px;')
        change_avatar_button.clicked.connect(self.change_avatar)
        
        avatar_button_layout = QHBoxLayout()
        avatar_button_layout.addStretch()
        avatar_button_layout.addWidget(change_avatar_button)
        avatar_button_layout.addStretch()
        layout.addLayout(avatar_button_layout)
        
        # 个人信息表单
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel('用户名:')
        username_label.setFont(QFont('Arial', 12))
        username_label.setFixedWidth(100)
        self.username_input = QLineEdit()
        self.username_input.setFont(QFont('Arial', 12))
        self.username_input.setStyleSheet('border-radius: 5px; border: 1px solid #ccc; padding: 5px;')
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        form_layout.addLayout(username_layout)
        
        # 邮箱
        email_layout = QHBoxLayout()
        email_label = QLabel('邮箱:')
        email_label.setFont(QFont('Arial', 12))
        email_label.setFixedWidth(100)
        self.email_input = QLineEdit()
        self.email_input.setFont(QFont('Arial', 12))
        self.email_input.setStyleSheet('border-radius: 5px; border: 1px solid #ccc; padding: 5px;')
        self.email_input.setReadOnly(True)  # 邮箱通常不允许修改
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        form_layout.addLayout(email_layout)
        
        # 手机号
        phone_layout = QHBoxLayout()
        phone_label = QLabel('手机号:')
        phone_label.setFont(QFont('Arial', 12))
        phone_label.setFixedWidth(100)
        self.phone_input = QLineEdit()
        self.phone_input.setFont(QFont('Arial', 12))
        self.phone_input.setStyleSheet('border-radius: 5px; border: 1px solid #ccc; padding: 5px;')
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        form_layout.addLayout(phone_layout)
        
        # 个人简介
        bio_layout = QHBoxLayout()
        bio_label = QLabel('个人简介:')
        bio_label.setFont(QFont('Arial', 12))
        bio_label.setFixedWidth(100)
        bio_label.setAlignment(Qt.AlignTop)
        self.bio_input = QTextEdit()
        self.bio_input.setFont(QFont('Arial', 12))
        self.bio_input.setStyleSheet('border-radius: 5px; border: 1px solid #ccc; padding: 5px;')
        self.bio_input.setFixedHeight(100)
        bio_layout.addWidget(bio_label)
        bio_layout.addWidget(self.bio_input)
        form_layout.addLayout(bio_layout)
        
        layout.addLayout(form_layout)
        
        # 加载用户信息
        self.load_user_profile()
        
        self.setLayout(layout)
    
    def load_user_profile(self):
        try:
            # 发送请求获取用户信息
            response = requests.get('http://localhost:5000/main/profile', cookies=self.get_session_cookies())
            
            if response.status_code == 200:
                user_data = response.json()
                self.username_input.setText(user_data.get('username', ''))
                self.email_input.setText(user_data.get('email', ''))
                self.phone_input.setText(user_data.get('phone', ''))
                self.bio_input.setPlainText(user_data.get('bio', ''))
            else:
                QMessageBox.warning(self, '警告', '无法获取用户信息', QMessageBox.Ok)
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, '错误', f'网络连接失败: {str(e)}', QMessageBox.Ok)
    
    def load_avatar(self):
        # 加载默认头像或用户头像
        default_avatar = QPixmap(':/icons/avatar.png')  # 需要添加默认头像资源
        if not default_avatar.isNull():
            self.avatar_label.setPixmap(default_avatar.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.avatar_label.setText('暂无头像')
    
    def change_avatar(self):
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(self, '选择头像文件', '',
                                                   '图片文件 (*.jpg *.jpeg *.png *.bmp)')
        
        if not file_path:
            return
            
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > 5 * 1024 * 1024:  # 5MB限制
            QMessageBox.warning(self, '警告', '头像文件大小不能超过5MB', QMessageBox.Ok)
            return
            
        # 加载并显示头像
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            self.avatar_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            QMessageBox.warning(self, '警告', '无法加载头像文件', QMessageBox.Ok)
    
    def save_profile(self):
        username = self.username_input.text().strip()
        phone = self.phone_input.text().strip()
        bio = self.bio_input.toPlainText().strip()
        
        if not username:
            QMessageBox.warning(self, '警告', '请填写用户名', QMessageBox.Ok)
            return
            
        try:
            # 发送请求保存用户信息
            response = requests.post('http://localhost:5000/main/update_profile', data={
                'username': username,
                'phone': phone,
                'bio': bio
            }, cookies=self.get_session_cookies())
            
            if response.status_code == 200:
                QMessageBox.information(self, '成功', '个人信息更新成功', QMessageBox.Ok)
            else:
                error_message = response.json().get('message', '个人信息更新失败')
                QMessageBox.warning(self, '失败', error_message, QMessageBox.Ok)
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, '错误', f'网络连接失败: {str(e)}', QMessageBox.Ok)
    
    def get_session_cookies(self):
        # 从文件或内存中获取会话信息
        # 这里简单地返回空字典，实际应用中应该保存和恢复会话信息
        return {}
