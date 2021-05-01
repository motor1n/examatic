"""Модель для работы с вопросами"""

import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_wtf import FlaskForm
from sqlalchemy_serializer import SerializerMixin
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
# from wtforms.validators import DataRequired
from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase, SerializerMixin):
    """Экзаменационный вопрос"""

    # Задаём имя таблицы:
    __tablename__ = 'questions'

    # Задаём столбцы таблицы questions:
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    number = sqlalchemy.Column(sqlalchemy.Integer)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_published = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    # Значения user_id имеют внешние ключи в таблице users
    # Это задаётся в параметре sqlalchemy.ForeignKey('users.id')
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))

    # Организовываем связь с таблицей users, используя метод relation(),
    # который указывает на пользователя, создавшего вопрос:
    user = orm.relation('User')
    # Эта строка связана со строкой
    # из файла users.py:
    # question = orm.relation('Question', back_populates='user')


class QuestionForm(FlaskForm):
    number = StringField('Номер вопроса:')
    content = TextAreaField('Содержание вопроса:')
    is_published = BooleanField('Черновик')
    submit = SubmitField('OK')
