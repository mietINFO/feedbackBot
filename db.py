# -*- coding: utf-8 -*-
import sqlite3


class DataBase:
    def __init__(self, db_path, db_file):
        self.db_file = db_path + db_file
        self.db = None


    def create_db(self):
        """
        Создание необходимых таблиц для работы с ботом
        """
        self.db = sqlite3.connect(self.db_file)
        cursor = self.db.cursor()

        # Создаём таблицу users, если она не существует
        cursor.execute("""CREATE TABLE IF NOT EXISTS users
                          (
                            user_id INT PRIMARY KEY,
                            state INT,
                            email TEXT
                          )""")
        self.db.commit()


    def check_user(self, user_id):
        """
        Проверяем на существование пользователя в системе
        """
        self.create_db()

        self.db = sqlite3.connect(self.db_file)
        cursor = self.db.cursor()

        cursor.execute('SELECT * FROM users WHERE user_id = ?', [user_id])

        if cursor.fetchone() == None:
            self.add_user(user_id)


    def add_user(self, user_id):
        """
        Добавляем нового пользователя в БД
        """
        self.db = sqlite3.connect(self.db_file)
        cursor = self.db.cursor()

        data = [user_id, '1']
        cursor.execute('INSERT INTO users (user_id, state) VALUES (?, ?)', data)
        self.db.commit()


    def update_email(self, user_id, email):
        """
        Добавляем или обновляем email пользователя
        """
        self.check_user(user_id)

        self.db = sqlite3.connect(self.db_file)
        cursor = self.db.cursor()

        data = [email, user_id]
        cursor.execute('UPDATE users SET email = ? WHERE user_id = ?', data)
        self.db.commit()


    def get_user(self, user_id):
        """
        Возвращаем данные определённого пользователя
        """
        self.db = sqlite3.connect(self.db_file)
        cursor = self.db.cursor()

        cursor.execute('SELECT state, email FROM users WHERE user_id = ?', [user_id])
        return cursor.fetchone()


    def get_state(self, user_id):
        """
        Возвращаем текущее состояние пользователя
        """
        self.check_user(user_id)
        return self.get_user(user_id)[0]


    def set_state(self, user_id, state):
        """
        Устанавливаем определённое состояние пользователя
        """
        self.db = sqlite3.connect(self.db_file)
        cursor = self.db.cursor()
        state = state

        data = [state, user_id]
        cursor.execute('UPDATE users SET state = ? WHERE user_id = ?', data)
        self.db.commit()


    def get_email(self, user_id):
        """
        Возвращаем email пользователя
        """
        return self.get_user(user_id)[1]