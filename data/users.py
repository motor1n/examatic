"""Модель для работы с пользователями"""

import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    """Работа с информацией о пользователях"""
    
    # Задаём имя таблицы:
    __tablename__ = 'users'

    # Задаём столбцы таблицы users:
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    middlename = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    # Экзаменационный билет пользователя.
    # Используем метод relation(),
    # который связывает пользователя и экзаменационный билет, который он взял:
    ticket = orm.relation('Ticket', back_populates='user')
    # Эта строка связана со строкой из файла ticket.py --> user = orm.relation('User')

    # Экзаменационный вопрос админа.
    # Используем метод relation(),
    # который связывает пользователя и экзаменационный билет, который он добавил:
    question = orm.relation('Question', back_populates='user')
    # Эта строка связана со строкой из файла question.py --> user = orm.relation('User')

    # Хранить пароль в открытом виде нельзя, поэтому во Flask есть инструменты,
    # которые позволяют получить хешированное значение по строке и проверить,
    # соответствует ли пароль хешу, который хранится в нашей базе данных.
    def set_password(self, password):
        """Создание хэша пароля"""
        # Функция используется при регистрации пользователя.
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        """Проверка пароля"""
        # Смотрим, соответствует ли пароль значению хэша на сервере:
        return check_password_hash(self.hashed_password, password)
