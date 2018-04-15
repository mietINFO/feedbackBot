# -*- coding: utf-8 -*-
import config
from re import *
from db import DataBase
from states import State
import functions as func
from telebot import types
import mail


db = DataBase(config.db_path, config.db_file)

class Message:
    def __init__(self, bot):
        self.bot = bot

    def get_email_input(self, message):
        """
        Обрабатываем и возвращаем стартовое сообщение
        """
        self.bot.send_message(message.chat.id,
                              func.message_wrapper({
                                  'headline': 'Ввод email',
                                  'text': 'Для того, чтобы мы могли Вам ответить, введите Ваш email:'
                              }),
                              parse_mode="HTML")


    def get_choice_menu(self, message):
        """
        Обрабатываем и возвращаем меню выбора
        """
        db.set_state(message.chat.id, str(State.CHOICE.value))

        # Добавляем встроенную клавиатуру
        keyboard = types.InlineKeyboardMarkup()
        button_ask = types.InlineKeyboardButton(text="Задать вопрос", callback_data="question")
        button_issue = types.InlineKeyboardButton(text="Сообщить о проблеме", callback_data="issue")
        button_change = types.InlineKeyboardButton(text="Изменить email", callback_data="change")

        # Добавляем кнопки
        keyboard.add(button_ask)
        keyboard.add(button_issue)
        keyboard.add(button_change)

        # Отправляем сообщение
        self.bot.send_message(message.chat.id,
                              func.message_wrapper({
                                  'headline': 'Меню выбора',
                                  'text': 'Здесь Вы можете задать нам интересующий вопрос или сообщить нам о возникшей проблеме при работе с @mietINFO!\n\rВыберите подходящее действие:'
                              }),
                              reply_markup=keyboard, parse_mode="HTML")


    def get_email(self, message):
        """
        Проверяем и добавляем/обновляем email пользователя
        """
        pattern = compile('(^|\s)[-a-zA-Z0-9_.]+@([-a-zA-Z0-9]+\.)+[A-Za-z]{2,6}(\s|$)')
        is_valid = pattern.match(message.text)

        # Проверка нового email, который ввёл пользователь
        if db.get_email(message.chat.id) == message.text:
            self.bot.send_message(message.chat.id,
                                  func.message_wrapper({
                                      'headline': 'Ввод email',
                                      'text': 'Вы ввели email-адрес, который используете в данный момент!\n\r\n\rНапишите ещё раз:'
                                  }),
                                  parse_mode="HTML")
        elif is_valid and len(message.text) > 7 and len(message.text) < 40:
            db.set_state(message.chat.id, State.EMAIL.value)
            db.update_email(message.chat.id, message.text)
            self.get_choice_menu(message)
        else:
            self.bot.send_message(message.chat.id,
                                  func.message_wrapper({
                                      'headline': 'Ввод email',
                                      'text': 'Вы ввели некорректный формат email-адреса!\n\r\n\rНапишите ещё раз:'
                                  }),
                                  parse_mode="HTML")


    def get_choice(self, call):
        """
        Возвращаем одно из выбранных действий меню
        """
        if call.data == "question":
            db.set_state(call.message.chat.id, State.QUESTION.value)
            self.bot.edit_message_text(chat_id=call.message.chat.id,
                                       message_id=call.message.message_id,
                                       text=func.message_wrapper({
                                           'headline': 'Ввод вопроса',
                                           'text': 'Напишите вопрос, который Вас интересует (15-300 символов):'
                                       }),
                                       parse_mode="HTML")
        elif call.data == "issue":
            db.set_state(call.message.chat.id, State.ISSUE.value)
            self.bot.edit_message_text(chat_id=call.message.chat.id,
                                       message_id=call.message.message_id,
                                       text=func.message_wrapper({
                                           'headline': 'Ввод проблемы',
                                           'text': 'Опишите проблему, которая у Вас возникла (15-300 символов):'
                                       }),
                                       parse_mode="HTML")
        elif call.data == "change":
            db.set_state(call.message.chat.id, State.EMAIL.value)
            self.bot.edit_message_text(chat_id=call.message.chat.id,
                                       message_id=call.message.message_id,
                                       text=func.message_wrapper({
                                           'headline': 'Ввод email',
                                           'text': 'Введите новый email:'
                                       }),
                                       parse_mode="HTML")


    def get_answer(self, message):
        """
        Отправляем вопрос или проблему администратору на почту
        """
        if len(message.text) >= 15 and len(message.text) <= 300:
            if message.from_user.first_name and message.from_user.last_name:
                user_name = message.from_user.first_name + " " + message.from_user.last_name
            elif message.from_user.first_name:
                user_name = message.from_user.first_name
            else:
                user_name = message.from_user.username


            if db.get_state(message.chat.id) == State.QUESTION.value:
                self.bot.send_message(message.chat.id,
                                      func.message_wrapper({
                                          'headline': 'Вопрос принят на рассмотрение',
                                          'text': 'Мы обязательно пришлём Вам ответ на заданный вопрос!'
                                      }),
                                      parse_mode="HTML")

                # Отправляем вопрос пользователя на почту администратора
                mail.send(user_name, db.get_email(message.chat.id),
                          "Новый вопрос от " + user_name,
                          "Пользователь " + user_name + " написал следующий вопрос:\r\n" + message.text)
            else:
                self.bot.send_message(message.chat.id,
                                      func.message_wrapper({
                                          'headline': 'Проблема принята на рассмотрение',
                                          'text': 'Мы обязательно проанализируем и пришлём Вам ответ!'
                                      }),
                                      parse_mode="HTML")

                # Отправляем проблему пользователя на почту администратора
                mail.send(user_name, db.get_email(message.chat.id),
                          user_name + " сообщил о возникшей проблеме",
                          "Пользователь " + user_name + " описал следующую проблему, с которой он столкнулся:\r\n" + message.text)

            # Возвращаем пользователя в меню
            self.get_choice_menu(message)
        else:
            if db.get_state(message.chat.id) == State.QUESTION.value:
                self.bot.send_message(message.chat.id,
                                      func.message_wrapper({
                                          'headline': 'Ошибка',
                                          'text': 'Вы ввели некорректный формат вопроса!\n\rДлина вопроса меньше 15 или больше 300 символов!\n\rНапишите вопрос ещё раз:'
                                      }),
                                      parse_mode="HTML")
            else:
                self.bot.send_message(message.chat.id,
                                      func.message_wrapper({
                                          'headline': 'Ошибка',
                                          'text': 'Вы ввели некорректный формат проблемы!\n\rДлина проблемы меньше 15 или больше 300 символов!\n\rНапишите проблему ещё раз:'
                                      }),
                                      parse_mode="HTML")