from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QListWidget, QListWidgetItem, QSpacerItem, QSizePolicy,
                             QMessageBox)
from frontend.session import get_session_cookies, clear_session
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import requests

class DashboardWidget(QWidget):
    journal_button_clicked = pyqtSignal()
    resource_button_clicked = pyqtSignal()
    profile_button_clicked = pyqtSignal()
    logout_button_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 顶部欢迎信息和用户信息
        top_layout = QHBoxLayout()
        
        welcome_label = QLabel('欢迎回来，')
        welcome_label.setFont(QFont('Arial', 16))
        self.username_label = QLabel('')
        self.username_label.setFont(QFont('Arial', 16, QFont.Bold))
        
        top_layout.addWidget(welcome_label)
        top_layout.addWidget(self.username_label)
        top_layout.addStretch()
        
        # 头像和个人资料按钮
        profile_button = QPushButton('个人资料')
        profile_button.setFont(QFont('Arial', 12))
        profile_button.setStyleSheet('background-color: #007bff; color: white; border-radius: 5px; padding: 5px 15px;')
        profile_button.clicked.connect(self.profile_button_clicked.emit)
        
        logout_button = QPushButton('退出登录')
        logout_button.setFont(QFont('Arial', 12))
        logout_button.setStyleSheet('background-color: #dc3545; color: white; border-radius: 5px; padding: 5px 15px;')
        logout_button.clicked.connect(self.logout)
        
        top_layout.addWidget(profile_button)
        top_layout.addWidget(logout_button)
        
        layout.addLayout(top_layout)
        
        # 主要功能按钮
        function_buttons_layout = QHBoxLayout()
        function_buttons_layout.setSpacing(15)
        
        # 日志备忘录按钮
        journal_button = QPushButton('日志备忘录')
        journal_button.setFont(QFont('Arial', 14, QFont.Bold))
        journal_button.setStyleSheet('background-color: #17a2b8; color: white; border-radius: 10px; padding: 20px; min-width: 200px;')
        journal_button.clicked.connect(self.journal_button_clicked.emit)
        function_buttons_layout.addWidget(journal_button)
        
        # 个性化资源按钮
        resource_button = QPushButton('个性化资源')
        resource_button.setFont(QFont('Arial', 14, QFont.Bold))
        resource_button.setStyleSheet('background-color: #ffc107; color: white; border-radius: 10px; padding: 20px; min-width: 200px;')
        resource_button.clicked.connect(self.resource_button_clicked.emit)
        function_buttons_layout.addWidget(resource_button)
        
        # 游戏设置按钮
        game_settings_button = QPushButton('游戏设置')
        game_settings_button.setFont(QFont('Arial', 14, QFont.Bold))
        game_settings_button.setStyleSheet('background-color: #28a745; color: white; border-radius: 10px; padding: 20px; min-width: 200px;')
        game_settings_button.clicked.connect(self.game_settings)
        function_buttons_layout.addWidget(game_settings_button)
        
        layout.addLayout(function_buttons_layout)
        
        # 最新动态部分
        recent_activity_layout = QVBoxLayout()
        recent_activity_label = QLabel('最新动态')
        recent_activity_label.setFont(QFont('Arial', 18, QFont.Bold))
        recent_activity_layout.addWidget(recent_activity_label)
        
        # 最新日志
        latest_journals_label = QLabel('最新日志')
        latest_journals_label.setFont(QFont('Arial', 14, QFont.Bold))
        recent_activity_layout.addWidget(latest_journals_label)
        
        self.latest_journals_list = QListWidget()
        self.latest_journals_list.setMaximumHeight(100)
        recent_activity_layout.addWidget(self.latest_journals_list)
        
        # 最新资源
        latest_resources_label = QLabel('最新资源')
        latest_resources_label.setFont(QFont('Arial', 14, QFont.Bold))
        recent_activity_layout.addWidget(latest_resources_label)
        
        self.latest_resources_list = QListWidget()
        self.latest_resources_list.setMaximumHeight(100)
        recent_activity_layout.addWidget(self.latest_resources_list)
        
        layout.addLayout(recent_activity_layout)
        
        self.setLayout(layout)
    
    def load_data(self):
        self.load_user_info()
        self.load_latest_journals()
        self.load_latest_resources()
    
    def load_user_info(self):
        try:
            # 发送请求获取用户信息
            response = requests.get('http://localhost:5000/profile', cookies=self.get_session_cookies())
            
            if response.status_code == 200:
                user_info = response.json()
                self.username_label.setText(user_info.get('username', ''))
            else:
                QMessageBox.warning(self, '警告', '无法获取用户信息', QMessageBox.Ok)
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, '错误', f'网络连接失败: {str(e)}', QMessageBox.Ok)
    
    def load_latest_journals(self):
        self.latest_journals_list.clear()
        try:
            # 发送请求获取最新日志
            response = requests.get('http://localhost:5000/journal/latest', cookies=self.get_session_cookies())
            
            if response.status_code == 200:
                journals = response.json()
                for journal in journals:
                    item = QListWidgetItem(f"{journal.get('title', '')} - {journal.get('created_at', '')[:10]}")
                    self.latest_journals_list.addItem(item)
            else:
                # 如果没有日志，添加提示信息
                item = QListWidgetItem('暂无日志记录')
                item.setFlags(Qt.NoItemFlags)
                self.latest_journals_list.addItem(item)
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, '错误', f'网络连接失败: {str(e)}', QMessageBox.Ok)
    
    def load_latest_resources(self):
        self.latest_resources_list.clear()
        try:
            # 发送请求获取最新资源
            response = requests.get('http://localhost:5000/resource/latest', cookies=self.get_session_cookies())
            
            if response.status_code == 200:
                resources = response.json()
                for resource in resources:
                    item = QListWidgetItem(f"{resource.get('name', '')} - {resource.get('uploaded_at', '')[:10]}")
                    self.latest_resources_list.addItem(item)
            else:
                # 如果没有资源，添加提示信息
                item = QListWidgetItem('暂无资源记录')
                item.setFlags(Qt.NoItemFlags)
                self.latest_resources_list.addItem(item)
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, '错误', f'网络连接失败: {str(e)}', QMessageBox.Ok)
    
    def game_settings(self):
        # 这里可以实现游戏设置功能
        QMessageBox.information(self, '提示', '游戏设置功能将在后续版本实现', QMessageBox.Ok)
    
    def logout(self):
        try:
            # 发送登出请求
            response = requests.get('http://localhost:5000/auth/logout', cookies=self.get_session_cookies())
        except:
            pass  # 忽略登出失败的情况
            
        # 清除会话信息
        self.clear_session()
        self.logout_button_clicked.emit()
    
    def get_session_cookies(self):
        # 从会话管理模块获取会话信息
        return get_session_cookies()
    
    def clear_session(self):
        # 清除会话信息
        clear_session()
