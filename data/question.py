"""Модель для работы с вопросами"""

import datetime
import sqlalchemy
from flask_wtf import FlaskForm
from sqlalchemy_serializer import SerializerMixin
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from . db_session import SqlAlchemyBase


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


class QuestionForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField('Содержание')
    is_published = BooleanField('Черновик')
    submit = SubmitField('Применить')
