"""Модель для регистрационной формы"""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    surname = StringField('Фамилия:', validators=[DataRequired()])
    name = StringField('Имя:', validators=[DataRequired()])
    middlename = StringField('Отчество:', validators=[DataRequired()])
    email = EmailField('Почта:', validators=[DataRequired()])
    password = PasswordField('Введите пароль:', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль:', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться на экзамен')
