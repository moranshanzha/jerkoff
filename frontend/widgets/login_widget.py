from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QCheckBox, QMessageBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import requests
from frontend.session import save_session

class LoginWidget(QWidget):
    login_success_signal = pyqtSignal()
    register_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        
        # 添加标题
        title_label = QLabel('飞机大战 - 登录')
        title_label.setFont(QFont('Arial', 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 添加垂直间距
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
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
        
        # 记住密码和忘记密码
        remember_forgot_layout = QHBoxLayout()
        self.remember_checkbox = QCheckBox('记住密码')
        self.remember_checkbox.setFont(QFont('Arial', 10))
        forgot_password_button = QPushButton('忘记密码？')
        forgot_password_button.setFont(QFont('Arial', 10))
        forgot_password_button.setStyleSheet('border: none; color: #007bff;')
        forgot_password_button.clicked.connect(self.forgot_password)
        remember_forgot_layout.addWidget(self.remember_checkbox)
        remember_forgot_layout.addStretch()
        remember_forgot_layout.addWidget(forgot_password_button)
        layout.addLayout(remember_forgot_layout)
        
        # 登录按钮
        self.login_button = QPushButton('登录')
        self.login_button.setFont(QFont('Arial', 14, QFont.Bold))
        self.login_button.setStyleSheet('background-color: #007bff; color: white; border-radius: 5px; padding: 10px;')
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)
        
        # 注册链接
        register_layout = QHBoxLayout()
        register_layout.addStretch()
        register_label = QLabel('还没有账号？')
        register_label.setFont(QFont('Arial', 10))
        register_button = QPushButton('立即注册')
        register_button.setFont(QFont('Arial', 10))
        register_button.setStyleSheet('border: none; color: #007bff;')
        register_button.clicked.connect(self.show_register)
        register_layout.addWidget(register_label)
        register_layout.addWidget(register_button)
        register_layout.addStretch()
        layout.addLayout(register_layout)
        
        # 添加垂直间距
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.setLayout(layout)
    
    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        remember = self.remember_checkbox.isChecked()
        
        if not email or not password:
            QMessageBox.warning(self, '警告', '请填写邮箱和密码', QMessageBox.Ok)
            return
            
        try:
            # 发送登录请求到后端
            response = requests.post('http://localhost:5000/auth/login', data={
                'email': email,
                'password': password,
                'remember': 'on' if remember else ''
            })
            
            if response.status_code == 200:
                # 登录成功，保存cookie或token
                self.save_session(response.cookies)
                self.login_success_signal.emit()
            else:
                # 登录失败，显示错误信息
                error_message = response.json().get('message', '登录失败')
                QMessageBox.warning(self, '登录失败', error_message, QMessageBox.Ok)
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, '错误', f'网络连接失败: {str(e)}', QMessageBox.Ok)
    
    def forgot_password(self):
        # 这里可以实现忘记密码功能
        QMessageBox.information(self, '提示', '忘记密码功能将在后续版本实现', QMessageBox.Ok)
    
    def show_register(self):
        self.register_signal.emit()
    
    def save_session(self, cookies):
        # 保存会话信息
        save_session(cookies)
