from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import requests

class RegisterWidget(QWidget):
    back_to_login_signal = pyqtSignal()
    register_success_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        
        # 添加标题
        title_label = QLabel('飞机大战 - 注册')
        title_label.setFont(QFont('Arial', 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 添加垂直间距
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # 用户名输入框
        username_layout = QHBoxLayout()
        username_label = QLabel('用户名:')
        username_label.setFixedWidth(80)
        username_label.setFont(QFont('Arial', 12))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('请输入您的用户名')
        self.username_input.setFont(QFont('Arial', 12))
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # 邮箱输入框
        email_layout = QHBoxLayout()
        email_label = QLabel('邮箱:')
        email_label.setFixedWidth(80)
        email_label.setFont(QFont('Arial', 12))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('请输入您的邮箱')
        self.email_input.setFont(QFont('Arial', 12))
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)
        
        # 密码输入框
        password_layout = QHBoxLayout()
        password_label = QLabel('密码:')
        password_label.setFixedWidth(80)
        password_label.setFont(QFont('Arial', 12))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('请输入您的密码')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont('Arial', 12))
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # 确认密码输入框
        confirm_password_layout = QHBoxLayout()
        confirm_password_label = QLabel('确认密码:')
        confirm_password_label.setFixedWidth(80)
        confirm_password_label.setFont(QFont('Arial', 12))
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('请再次输入您的密码')
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setFont(QFont('Arial', 12))
        confirm_password_layout.addWidget(confirm_password_label)
        confirm_password_layout.addWidget(self.confirm_password_input)
        layout.addLayout(confirm_password_layout)
        
        # 注册按钮
        self.register_button = QPushButton('注册')
        self.register_button.setFont(QFont('Arial', 14, QFont.Bold))
        self.register_button.setStyleSheet('background-color: #28a745; color: white; border-radius: 5px; padding: 10px;')
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)
        
        # 返回登录链接
        back_to_login_layout = QHBoxLayout()
        back_to_login_layout.addStretch()
        back_to_login_label = QLabel('已有账号？')
        back_to_login_label.setFont(QFont('Arial', 10))
        back_to_login_button = QPushButton('立即登录')
        back_to_login_button.setFont(QFont('Arial', 10))
        back_to_login_button.setStyleSheet('border: none; color: #007bff;')
        back_to_login_button.clicked.connect(self.back_to_login)
        back_to_login_layout.addWidget(back_to_login_label)
        back_to_login_layout.addWidget(back_to_login_button)
        back_to_login_layout.addStretch()
        layout.addLayout(back_to_login_layout)
        
        # 添加垂直间距
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.setLayout(layout)
    
    def register(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        
        if not username or not email or not password or not confirm_password:
            QMessageBox.warning(self, '警告', '请填写所有必填字段', QMessageBox.Ok)
            return
            
        if password != confirm_password:
            QMessageBox.warning(self, '警告', '两次输入的密码不一致', QMessageBox.Ok)
            return
            
        if len(password) < 8:
            QMessageBox.warning(self, '警告', '密码长度不能少于8个字符', QMessageBox.Ok)
            return
            
        try:
            # 发送注册请求到后端
            response = requests.post('http://localhost:5000/auth/register', data={
                'username': username,
                'email': email,
                'password': password,
                'confirm_password': confirm_password
            })
            
            if response.status_code == 200:
                QMessageBox.information(self, '注册成功', '注册成功！请检查您的邮箱以确认账户', QMessageBox.Ok)
                self.register_success_signal.emit()
            else:
                # 注册失败，显示错误信息
                error_message = response.json().get('message', '注册失败')
                QMessageBox.warning(self, '注册失败', error_message, QMessageBox.Ok)
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, '错误', f'网络连接失败: {str(e)}', QMessageBox.Ok)
    
    def back_to_login(self):
        self.back_to_login_signal.emit()
