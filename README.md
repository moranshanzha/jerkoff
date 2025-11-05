# 飞机大战游戏 - 项目管理系统

一个基于Flask框架开发的多功能项目管理系统，为飞机大战游戏提供用户管理、日志管理和个性化资源管理等功能。

## 功能特性

### 1. 用户认证系统
- ✅ 用户注册（邮箱验证、密码强度检测）
- ✅ 用户登录（支持记住密码）
- ✅ 密码重置（通过安全邮箱链接）
- ✅ 邮箱验证机制
- ✅ 密码强度检查（至少8个字符，包含大小写字母和数字）

### 2. 日志备忘录系统
- ✅ 创建、查看、编辑和删除个人日志
- ✅ 按日期、标签分类管理
- ✅ 搜索功能（标题、内容、标签）
- ✅ 分页显示
- ✅ 富文本编辑支持

### 3. 个性化资源管理系统
- ✅ 上传个性化皮肤和人物模型
- ✅ 文件格式验证（图片：png/jpg/jpeg/gif；模型：obj/fbx）
- ✅ 大小限制（16MB）
- ✅ 预览功能
- ✅ 资源激活机制
- ✅ 下载功能

## 技术栈

- **后端框架**: Flask 2.3.3
- **数据库**: SQLite
- **ORM**: SQLAlchemy 2.0.19
- **表单处理**: Flask-WTF 1.1.1
- **用户认证**: Flask-Login 0.6.3
- **邮件发送**: Flask-Mail 0.9.1
- **密码加密**: Werkzeug
- **文件上传**: Werkzeug
- **游戏开发**: Pygame (原项目)

## 项目结构

```
jerkoff/
├── app/                          # 主应用目录
│   ├── auth/                    # 用户认证模块
│   │   ├── __init__.py
│   │   ├── forms.py             # 认证表单
│   │   └── views.py             # 认证视图
│   ├── logs/                    # 日志管理模块
│   │   ├── __init__.py
│   │   ├── forms.py             # 日志表单
│   │   └── views.py             # 日志视图
│   ├── main/                    # 主模块
│   │   ├── __init__.py
│   │   └── views.py             # 主视图
│   ├── resources/               # 资源管理模块
│   │   ├── __init__.py
│   │   ├── forms.py             # 资源表单
│   │   └── views.py             # 资源视图
│   ├── templates/               # HTML模板
│   │   ├── auth/               # 认证模板
│   │   ├── logs/               # 日志模板
│   │   ├── main/               # 主模板
│   │   ├── resources/          # 资源模板
│   │   └── base.html           # 基础模板
│   ├── __init__.py
│   └── models.py               # 数据库模型
├── backend/                     # 后端目录
├── frontend/                    # 前端目录
├── material/                    # 游戏素材
│   ├── image/                  # 图片资源
│   └── sound/                  # 音频资源
├── src/                         # 游戏源码
│   ├── bullet.py              # 子弹类
│   ├── enemy.py               # 敌人类
│   └── plane.py               # 飞机类
├── app.py                       # 应用入口
├── migrate.py                   # 数据库迁移脚本
├── requirements.txt             # 依赖文件
└── uploads/                     # 文件上传目录
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件并配置以下内容：

```
SECRET_KEY=your-secret-key-here
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
```

### 3. 初始化数据库

```bash
python migrate.py
```

### 4. 运行应用

```bash
python app.py
```

应用将在 http://localhost:5000 运行

## 访问应用

- 首页: http://localhost:5000
- 注册: http://localhost:5000/auth/register
- 登录: http://localhost:5000/auth/login
- 仪表板: http://localhost:5000/dashboard
- 日志管理: http://localhost:5000/logs
- 资源管理: http://localhost:5000/resources

## 默认管理员

初始化数据库后会创建默认管理员用户：
- 邮箱: admin@example.com
- 密码: Admin123!

## 原有游戏功能

- ✈️ 飞机大战游戏核心逻辑
- 🎮 玩家控制飞机移动和射击
- 🎯 多种敌人类型和难度
- 💥 丰富的爆炸效果和音效
- 🏆 分数统计和游戏结束机制

## 技术文档

### API 接口

- **用户认证**: `/auth/` 前缀
- **日志管理**: `/logs/` 前缀
- **资源管理**: `/resources/` 前缀

### 数据库模型

- `User`: 用户信息
- `Log`: 日志记录
- `Resource`: 资源文件

## 开发计划

- [ ] 实现3D模型预览功能
- [ ] 添加文件上传进度条
- [ ] 支持日志导出功能
- [ ] 实现用户角色管理
- [ ] 添加更多皮肤和模型格式支持
- [ ] 实现数据统计和分析
- [ ] 开发Qt桌面客户端
- [ ] 将资源管理与游戏集成
- [ ] 实现游戏皮肤切换功能

## 许可证

MIT License

## 作者

您的名字

