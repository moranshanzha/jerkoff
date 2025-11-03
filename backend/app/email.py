from flask import render_template
from flask_mail import Message
from app import mail, app
from threading import Thread

# 使用异步方式发送邮件
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

# 通用邮件发送函数
def send_email(subject, recipients, template, **kwargs):
    msg = Message(subject, recipients=recipients)
    msg.body = render_template(f'{template}.txt', **kwargs)
    msg.html = render_template(f'{template}.html', **kwargs)
    
    # 异步发送邮件
    Thread(target=send_async_email, args=(app, msg)).start()
