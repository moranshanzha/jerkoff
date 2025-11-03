from flask_script import Manager
from flask_migrate import MigrateCommand
from app import create_app, db

app = create_app()
manager = Manager(app)

# 添加数据库迁移命令
manager.add_command('db', MigrateCommand)

@manager.command
def create_db():
    """创建数据库表"""
    db.create_all()
    print('数据库表创建成功')

@manager.command
def drop_db():
    """删除数据库表"""
    if input('确定要删除所有数据库表吗？这将导致数据丢失！(y/n): ').lower() == 'y':
        db.drop_all()
        print('数据库表删除成功')

if __name__ == '__main__':
    manager.run()
