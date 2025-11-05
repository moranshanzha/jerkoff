from app import app, db
from app.models import User, Log, Resource

with app.app_context():
    # 创建所有表
    db.create_all()
    print('数据库表创建成功！')

    # 检查是否有初始用户
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', is_verified=True)
        admin.set_password('Admin123!')
        db.session.add(admin)
        db.session.commit()
        print('创建默认管理员用户：admin@example.com / Admin123!')
