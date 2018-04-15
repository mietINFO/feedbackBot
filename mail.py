# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.header import Header


def send(sender_name, sender_email, subject, text):
    """
    Отправляем заявку пользователя на почту администратора
    """
    sender = sender_name + " <" + sender_email + ">"

    # SMTP-сервер
    server = "<your_smtp_server>"
    user_name = "<your_mail_login>"
    user_password = "<your_mail_password>"

    # Формируем новое сообщение
    message = MIMEText(text, 'plain', 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    message['From'] = sender
    message['To'] = user_name

    # Отправляем сообщение на почту администратора
    s = smtplib.SMTP_SSL(server)
    s.login(user_name, user_password)
    s.sendmail(user_name, user_name, message.as_string())
    s.quit()