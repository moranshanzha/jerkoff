# 会话管理模块

# 存储会话信息
session_cookies = {}

def save_session(cookies):
    """保存会话信息"""
    global session_cookies
    session_cookies = cookies.get_dict().get_dict()
    
def get_session_cookies():
    """获取会话信息"""
    global session_cookies
    return session_cookies
    
def clear_session():
    """清除会话信息"""
    global session_cookies
    session_cookies = {}
