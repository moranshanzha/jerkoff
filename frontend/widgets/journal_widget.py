from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QListWidget, QListWidgetItem, QLineEdit, QTextEdit, QDateEdit,
                             QComboBox, QMessageBox, QSpacerItem, QSizePolicy, QDialog,
                             QDialogButtonBox)
from PyQt5.QtCore import Qt, pyqtSignal, QDateTime
from PyQt5.QtGui import QFont
import requests
from datetime import datetime
from frontend.session import get_session_cookies

class JournalWidget(QWidget):
    back_button_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.journals = []
    
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
        self.search_input.setPlaceholderText('搜索日志...')
        self.search_input.setFont(QFont('Arial', 12))
        self.search_input.returnPressed.connect(self.load_journals)
        top_layout.addWidget(self.search_input)
        
        # 搜索按钮
        search_button = QPushButton('搜索')
        search_button.setFont(QFont('Arial', 12))
        search_button.setStyleSheet('background-color: #007bff; color: white; border-radius: 5px; padding: 5px 15px;')
        search_button.clicked.connect(self.load_journals)
        top_layout.addWidget(search_button)
        
        # 添加日志按钮
        add_button = QPushButton('添加日志')
        add_button.setFont(QFont('Arial', 12))
        add_button.setStyleSheet('background-color: #28a745; color: white; border-radius: 5px; padding: 5px 15px;')
        add_button.clicked.connect(self.add_journal)
        top_layout.addWidget(add_button)
        
        layout.addLayout(top_layout)
        
        # 筛选区域
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)
        
        # 日期筛选
        date_label = QLabel('日期:')
        date_label.setFont(QFont('Arial', 12))
        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDate(QDateTime.currentDateTime().date())
        self.date_filter.setMaximumDate(QDateTime.currentDateTime().date())
        self.date_filter.setFont(QFont('Arial', 12))
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.date_filter)
        
        # 标签筛选
        tag_label = QLabel('标签:')
        tag_label.setFont(QFont('Arial', 12))
        self.tag_filter = QComboBox()
        self.tag_filter.setFont(QFont('Arial', 12))
        self.tag_filter.addItem('所有标签')
        filter_layout.addWidget(tag_label)
        filter_layout.addWidget(self.tag_filter)
        
        # 应用筛选按钮
        apply_filter_button = QPushButton('应用筛选')
        apply_filter_button.setFont(QFont('Arial', 12))
        apply_filter_button.setStyleSheet('background-color: #007bff; color: white; border-radius: 5px; padding: 5px 15px;')
        apply_filter_button.clicked.connect(self.load_journals)
        filter_layout.addWidget(apply_filter_button)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # 日志列表
        self.journal_list = QListWidget()
        self.journal_list.itemDoubleClicked.connect(self.view_journal)
        layout.addWidget(self.journal_list)
        
        self.setLayout(layout)
    
    def load_journals(self):
        self.journal_list.clear()
        try:
            # 准备请求参数
            params = {}
            search_query = self.search_input.text().strip()
            if search_query:
                params['search'] = search_query
                
            # 日期筛选
            date = self.date_filter.date().toString('yyyy-MM-dd')
            if date != datetime.now().strftime('%Y-%m-%d'):
                params['date'] = date
                
            # 标签筛选
            tag = self.tag_filter.currentText()
            if tag != '所有标签':
                params['tag'] = tag
                
            # 发送请求获取日志列表
            response = requests.get('http://localhost:5000/journal/journals', params=params, cookies=self.get_session_cookies())
            
            if response.status_code == 200:
                self.journals = response.json()['journals']
                
                if not self.journals:
                    item = QListWidgetItem('没有找到匹配的日志')
                    item.setFlags(Qt.NoItemFlags)
                    self.journal_list.addItem(item)
                    return
                    
                # 更新标签筛选下拉框
                self.update_tag_filter()
                
                # 显示日志列表
                for journal in self.journals:
                    item = QListWidgetItem(f"{journal.get('title', '')} - {journal.get('created_at', '')[:10]}")
                    self.journal_list.addItem(item)
            else:
                QMessageBox.warning(self, '警告', '无法获取日志列表', QMessageBox.Ok)
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, '错误', f'网络连接失败: {str(e)}', QMessageBox.Ok)
    
    def update_tag_filter(self):
        # 获取所有唯一标签
        tags = set()
        for journal in self.journals:
            for tag in journal.get('tags', []):
                tags.add(tag)
                
        # 保存当前选择的标签
        current_tag = self.tag_filter.currentText()
        
        # 清空并重新添加标签
        self.tag_filter.clear()
        self.tag_filter.addItem('所有标签')
        for tag in sorted(tags):
            self.tag_filter.addItem(tag)
            
        # 尝试恢复之前选择的标签
        if current_tag and self.tag_filter.findText(current_tag) >= 0:
            self.tag_filter.setCurrentText(current_tag)
    
    def add_journal(self):
        # 创建添加日志的对话框
        dialog = JournalDialog()
        if dialog.exec_() == QDialog.Accepted:
            title = dialog.title_input.text().strip()
            content = dialog.content_input.toPlainText().strip()
            tags = dialog.tags_input.text().strip().split(',')
            tags = [tag.strip() for tag in tags if tag.strip()]
            
            if not title or not content:
                QMessageBox.warning(self, '警告', '请填写标题和内容', QMessageBox.Ok)
                return
                
            try:
                # 发送添加日志请求
                response = requests.post('http://localhost:5000/journal/create', data={
                    'title': title,
                    'content': content,
                    'tags': ','.join(tags)
                }, cookies=self.get_session_cookies())
                
                if response.status_code == 200:
                    QMessageBox.information(self, '成功', '日志创建成功', QMessageBox.Ok)
                    self.load_journals()  # 刷新日志列表
                else:
                    error_message = response.json().get('message', '日志创建失败')
                    QMessageBox.warning(self, '失败', error_message, QMessageBox.Ok)
                    
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, '错误', f'网络连接失败: {str(e)}', QMessageBox.Ok)
    
    def view_journal(self, item):
        # 获取点击的日志索引
        index = self.journal_list.row(item)
        if index >= 0 and index < len(self.journals):
            journal = self.journals[index]
            
            # 创建查看日志的对话框
            dialog = JournalDialog()
            dialog.setWindowTitle('查看日志')
            dialog.title_input.setText(journal.get('title', ''))
            dialog.content_input.setPlainText(journal.get('content', ''))
            dialog.tags_input.setText(','.join(journal.get('tags', [])))
            
            # 禁用编辑
            dialog.title_input.setReadOnly(True)
            dialog.content_input.setReadOnly(True)
            dialog.tags_input.setReadOnly(True)
            
            # 添加编辑和删除按钮
            edit_button = QPushButton('编辑')
            delete_button = QPushButton('删除')
            dialog.button_box.addButton(edit_button, QDialogButtonBox.ActionRole)
            dialog.button_box.addButton(delete_button, QDialogButtonBox.ActionRole)
            
            edit_button.clicked.connect(lambda: self.edit_journal(dialog, journal))
            delete_button.clicked.connect(lambda: self.delete_journal(dialog, journal))
            
            dialog.exec_()
    
    def edit_journal(self, dialog, journal):
        # 启用编辑
        dialog.title_input.setReadOnly(False)
        dialog.content_input.setReadOnly(False)
        dialog.tags_input.setReadOnly(False)
        
        # 隐藏查看按钮，显示保存按钮
        dialog.button_box.clear()
        dialog.button_box.addButton(QDialogButtonBox.Save)
        dialog.button_box.addButton(QDialogButtonBox.Cancel)
        
        # 连接保存按钮信号
        def save_edit():
            title = dialog.title_input.text().strip()
            content = dialog.content_input.toPlainText().strip()
            tags = dialog.tags_input.text().strip().split(',')
            tags = [tag.strip() for tag in tags if tag.strip()]
            
            if not title or not content:
                QMessageBox.warning(self, '警告', '请填写标题和内容', QMessageBox.Ok)
                return
                
            try:
                # 发送编辑日志请求
                response = requests.post(f'http://localhost:5000/journal/{journal.get('id')}/edit', data={
                    'title': title,
                    'content': content,
                    'tags': ','.join(tags)
                }, cookies=self.get_session_cookies())
                
                if response.status_code == 200:
                    QMessageBox.information(self, '成功', '日志更新成功', QMessageBox.Ok)
                    dialog.accept()
                    self.load_journals()  # 刷新日志列表
                else:
                    error_message = response.json().get('message', '日志更新失败')
                    QMessageBox.warning(self, '失败', error_message, QMessageBox.Ok)
                    
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, '错误', f'网络连接失败: {str(e)}', QMessageBox.Ok)
                
        dialog.button_box.accepted.connect(save_edit)
    
    def delete_journal(self, dialog, journal):
        result = QMessageBox.question(self, '确认删除', '确定要删除这篇日志吗？', QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            try:
                # 发送删除日志请求
                response = requests.post(f'http://localhost:5000/journal/{journal.get('id')}/delete', cookies=self.get_session_cookies())
                
                if response.status_code == 200:
                    QMessageBox.information(self, '成功', '日志删除成功', QMessageBox.Ok)
                    dialog.accept()
                    self.load_journals()  # 刷新日志列表
                else:
                    error_message = response.json().get('message', '日志删除失败')
                    QMessageBox.warning(self, '失败', error_message, QMessageBox.Ok)
                    
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, '错误', f'网络连接失败: {str(e)}', QMessageBox.Ok)
    
    def get_session_cookies(self):
        # 从会话管理模块获取会话信息
        return get_session_cookies()

class JournalDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('添加日志')
        self.setGeometry(200, 200, 600, 400)
        
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题输入框
        title_label = QLabel('标题:')
        title_label.setFont(QFont('Arial', 12))
        layout.addWidget(title_label)
        
        self.title_input = QLineEdit()
        self.title_input.setFont(QFont('Arial', 12))
        layout.addWidget(self.title_input)
        
        # 内容输入框
        content_label = QLabel('内容:')
        content_label.setFont(QFont('Arial', 12))
        layout.addWidget(content_label)
        
        self.content_input = QTextEdit()
        self.content_input.setFont(QFont('Arial', 12))
        layout.addWidget(self.content_input)
        
        # 标签输入框
        tags_label = QLabel('标签 (用逗号分隔):')
        tags_label.setFont(QFont('Arial', 12))
        layout.addWidget(tags_label)
        
        self.tags_input = QLineEdit()
        self.tags_input.setFont(QFont('Arial', 12))
        self.tags_input.setPlaceholderText('例如: 工作, 学习, 生活')
        layout.addWidget(self.tags_input)
        
        # 按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
        self.setLayout(layout)
