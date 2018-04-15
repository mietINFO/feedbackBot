# -*- coding: utf-8 -*-
import db
import telebot
import cherrypy
from states import State
import messages
import config


# Настройки вебхуков
WEBHOOK_HOST = '<your_host>'
WEBHOOK_PORT = 8443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

# Путь к сертификатам
WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

# Путь к боту
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)

# Запуск бота
bot = telebot.TeleBot(config.token, threaded=False)
msg = messages.Message(bot)
db = db.DataBase(config.db_path, config.db_file)

# Вебхук-сервер
class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)



# Набор директив для работы с ботом
@bot.message_handler(commands=['start'], func=lambda message: db.get_state(message.chat.id) == State.EMAIL.value)
def send_email(message):
    """
    Выводим сообщение с просьбой о вводе email
    """
    msg.get_email_input(message)


@bot.message_handler(commands=['start'], func=lambda message: db.get_state(message.chat.id) == State.CHOICE.value)
def send_choice(message):
    """
    Выводим меню выбора
    """
    msg.get_choice_menu(message)


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) == State.EMAIL.value, content_types=['text'])
def send_email(message):
    """
    Обрабатываем email, который ввёл пользователь
    """
    msg.get_email(message)


@bot.callback_query_handler(func=lambda call: db.get_state(call.message.chat.id) == State.CHOICE.value)
def send_choice(call):
    """
    Возвращаем сообщение после нажатия на одну из кнопок меню выбора
    """
    msg.get_choice(call)


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) == State.CHOICE.value, content_types=['text'])
def send_menu(message):
    """
    Выводим меню, если пользователь не нажал ни на одну кнопку
    """
    msg.get_choice_menu(message)


@bot.message_handler(func=lambda message: db.get_state(message.chat.id) in [State.QUESTION.value, State.ISSUE.value], content_types=['text'])
def send_answer(message):
    """
    Выводим ответ об успешном выполнении запроса или ошибку
    """
    msg.get_answer(message)



# Снимаем вебхук перед повторной установкой
bot.remove_webhook()

# Ставим вебхук
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Указываем настройки сервера CherryPy
cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

# Запуск вебхук-сервера
cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})