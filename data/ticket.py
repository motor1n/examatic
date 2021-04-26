"""Модель для работы с экзаменационными билетами"""

import sqlalchemy
from random import shuffle
from datetime import datetime
from sqlalchemy_serializer import SerializerMixin
from data.question import Question
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Ticket(SqlAlchemyBase, SerializerMixin):
    def __init__(self):
        # Количество экзаменационных вопросов:
        # self.number_questions = number_questions
        # Количество вопросов в одном билете:
        # self.questions_in_ticket = questions_in_ticket
        # Словарь для хранения выданных билетов:
        self.tickets = dict()

    # Задаём имя таблицы:
    __tablename__ = 'tickets'

    # Задаём столбцы таблицы users:
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    # Значения user_id имеют внешние ключи в таблице users
    # Это задаётся в параметре sqlalchemy.ForeignKey('users.id')
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    # Кроме того, организовываем связь с таблицей users, используя метод relation(),
    # который указывает на пользователя, получившего экзаменационный билет:
    user = orm.relation('User')
    # Эта строка связана
    # со строкой ticket = orm.relation('Ticket', back_populates='user') из файла users.py

    question1 = sqlalchemy.Column(sqlalchemy.Integer)
    question2 = sqlalchemy.Column(sqlalchemy.Integer)
    practic = sqlalchemy.Column(sqlalchemy.Integer)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)

    @staticmethod
    def load_questions(db):
        """Загрузка готовых вопросов из базы данных в список"""
        # db = db_session.create_session()
        # Фильтруем вопросы - оставляем готовые:
        db_questions = db.query(Question).filter(Question.is_published == 1)
        return [item.content for item in db_questions]

    @staticmethod
    def create_questions(number):
        """Генератор перемешанного набора номеров экзаменационных вопросов"""
        # number - количество экзаменационных вопросов
        questions_list = list(range(number))
        # Перемешиваем номера:
        shuffle(questions_list)
        return questions_list

    @staticmethod
    def create_practics(number):
        """Генератор перемешанного набора номеров практических заданий"""
        # number - количество практических заданий
        practics_list = list(range(1, number + 1))
        # Перемешиваем номера:
        shuffle(practics_list)
        return practics_list
