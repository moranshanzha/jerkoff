import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from widgets.login_widget import LoginWidget
from widgets.register_widget import RegisterWidget
from widgets.dashboard_widget import DashboardWidget
from widgets.journal_widget import JournalWidget
from widgets.resource_widget import ResourceWidget
from widgets.profile_widget import ProfileWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('飞机大战 - 个人中心')
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建堆叠式窗口管理不同页面
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # 创建各个页面
        self.login_widget = LoginWidget()
        self.register_widget = RegisterWidget()
        self.dashboard_widget = DashboardWidget()
        self.journal_widget = JournalWidget()
        self.resource_widget = ResourceWidget()
        self.profile_widget = ProfileWidget()
        
        # 添加页面到堆叠式窗口
        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.register_widget)
        self.stacked_widget.addWidget(self.dashboard_widget)
        self.stacked_widget.addWidget(self.journal_widget)
        self.stacked_widget.addWidget(self.resource_widget)
        self.stacked_widget.addWidget(self.profile_widget)
        
        # 连接信号和槽
        self.login_widget.login_success_signal.connect(self.show_dashboard)
        self.login_widget.register_signal.connect(self.show_register)
        self.register_widget.back_to_login_signal.connect(self.show_login)
        self.register_widget.register_success_signal.connect(self.show_login)
        self.dashboard_widget.journal_button_clicked.connect(self.show_journal)
        self.dashboard_widget.resource_button_clicked.connect(self.show_resource)
        self.dashboard_widget.profile_button_clicked.connect(self.show_profile)
        self.dashboard_widget.logout_button_clicked.connect(self.show_login)
        self.journal_widget.back_button_clicked.connect(self.show_dashboard)
        self.resource_widget.back_button_clicked.connect(self.show_dashboard)
        self.profile_widget.back_button_clicked.connect(self.show_dashboard)
        
        # 显示登录页面
        self.show_login()
    
    def show_login(self):
        self.stacked_widget.setCurrentWidget(self.login_widget)
        self.setWindowTitle('飞机大战 - 登录')
    
    def show_register(self):
        self.stacked_widget.setCurrentWidget(self.register_widget)
        self.setWindowTitle('飞机大战 - 注册')
    
    def show_dashboard(self):
        self.stacked_widget.setCurrentWidget(self.dashboard_widget)
        self.setWindowTitle('飞机大战 - 控制台')
        self.dashboard_widget.load_data()  # 加载数据
    
    def show_journal(self):
        self.stacked_widget.setCurrentWidget(self.journal_widget)
        self.setWindowTitle('飞机大战 - 日志备忘录')
        self.journal_widget.load_journals()  # 加载日志数据
    
    def show_resource(self):
        self.stacked_widget.setCurrentWidget(self.resource_widget)
        self.setWindowTitle('飞机大战 - 个性化资源')
        self.resource_widget.load_resources()  # 加载资源数据
    
    def show_profile(self):
        self.stacked_widget.setCurrentWidget(self.profile_widget)
        self.setWindowTitle('飞机大战 - 个人资料')
        self.profile_widget.load_profile()  # 加载个人资料

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
