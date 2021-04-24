"""Модель для работы с экзаменационными билетами"""

import sqlalchemy
from random import shuffle
from datetime import datetime
# from data import db_session
from sqlalchemy_serializer import SerializerMixin
from data.question import Question
from sqlalchemy import orm
# from examatic import DATABASE
from . db_session import SqlAlchemyBase


class Ticket(SqlAlchemyBase, SerializerMixin):
    def __init__(self, number_questions, questions_in_ticket):
        # Количество экзаменационных вопросов:
        self.number_questions = number_questions
        # Количество вопросов в одном билете:
        self.questions_in_ticket = questions_in_ticket
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

    def count_questions(self, db):
        """Определение количества вопросов"""
        return len(self.load_questions(db))

    @staticmethod
    def create_questions(number):
        """Генератор перемешанного набора экзаменационных вопросов"""
        # number - количество экзаменационных вопросов
        tickets_list = list(range(number))
        # Перемешиваем номера:
        shuffle(tickets_list)
        return tickets_list
