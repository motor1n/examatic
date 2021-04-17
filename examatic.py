"""
examatic 0.0.3
Exam-a-Ticket Generator
developed on flask
"""

import datetime
from flask import Flask, render_template, request, make_response, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from sqlalchemy import or_
# from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from data import db_session
from data.question import Question
from data.users import User
from data.register import RegisterForm
from data.login import LoginForm
from data import question_api


DATABASE = 'dbase/examen.db'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

# Инициализация менеджера логинов
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Загрузка пользователя"""
    db = db_session.create_session()
    return db.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    """Корневая страница"""
    db = db_session.create_session()
    # Фильтруем вопросы - исключаем черновики (Question.is_published == 0):
    db_questions = db.query(Question).filter(Question.is_published == 1)
    # Рендерим вопросы на шаблон страницы:
    return render_template('index.html', questions=db_questions)


# URL http://localhost:5000/register
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    regform = RegisterForm()
    if regform.validate_on_submit():
        if regform.password.data != regform.password_again.data:
            # TODO: модальное окно на ошибку
            return render_template(
                'register.html',
                title='Регистрация',
                form=regform,
                message='Пароли не совпадают'
            )
        db = db_session.create_session()
        if db.query(User).filter(User.email == regform.email.data).first():
            return redirect('/register#iw-modal')
        user = User(
            name=regform.name.data,
            surname=regform.surname.data,
            middlename=regform.middlename.data,
            email=regform.email.data
        )
        user.set_password(regform.password.data)
        db.add(user)
        db.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=regform)


# URL http://localhost:5000/login
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Авторизация"""
    login_form = LoginForm()
    if login_form.validate_on_submit():
        db = db_session.create_session()
        user = db.query(User).filter(User.email == login_form.email.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user, remember=login_form.remember_me.data)
            # TODO: Выдача билета пользователю
            print(f'Студент: {user.surname} {user.name} {user.middlename}')
            return redirect('/ticket')
        return redirect('/login#iw-modal')
    return render_template('login.html', title='Авторизация', form=login_form)


# URL http://localhost:5000/ticket
@app.route('/ticket')
def ticket():
    """Экзаменационный билет"""
    # db = db_session.create_session()
    # Фильтруем вопросы - исключаем черновики (Question.is_published == 0):
    # db_questions = db.query(Question).filter(Question.is_published == 1)
    ticket_number = 14
    # Рендерим билет на шаблон страницы:
    return render_template(
        'ticket.html',
        name=current_user.name,
        surname=current_user.surname,
        middlename=current_user.middlename,
        ticket=ticket_number
    )


'''
# URL http://localhost:5000/question
@app.route('/question',  methods=['GET', 'POST'])
@login_required
def add_question():
    """Добавление вопроса"""
    question_form = QuestionForm()
    if question_form.validate_on_submit():
        db = db_session.create_session()
        question = Question()
        question.title = question_form.title.data
        question.content = question_form.content.data
        question.is_published = question_form.is_published.data
        current_user.question.append(question)
        db.merge(current_user)
        db.commit()
        return redirect('/')
    return render_template(
        'question.html',
        title='Добавление вопроса',
        form=question_form
    )


@app.route('/question/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    """Редактирование вопроса"""
    form = QuestionForm()
    if request.method == 'GET':
        db = db_session.create_session()
        question = db.query(Question).filter(
            Question.id == question_id,
            Question.user == current_user
        ).first()
        if question:
            form.title.data = question.title
            form.content.data = question.content
            form.is_published.data = question.is_published
        else:
            abort(404)
    if form.validate_on_submit():
        db = db_session.create_session()
        question = db.query(Question).filter(
            Question.id == question_id,
            Question.user == current_user
        ).first()
        if question:
            question.title = form.title.data
            question.content = form.content.data
            question.is_published = form.is_published.data
            db.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('question.html', title='Редактирование вопроса', form=form)


@app.route('/question_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def question_delete(question_id):
    """Удаление вопроса"""
    db = db_session.create_session()
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.user == current_user
    ).first()
    if question:
        db.delete(question)
        db.commit()
    else:
        abort(404)
    return redirect('/')
'''


# URL http://localhost:5000/session_count
@app.route('/session_count')
def session_count():
    """Счётчик посещений страницы (способ session)"""
    # Смотрим ключ 'visits_count' в объекте session:
    if 'visits_count' in session:
        # Если мы уже посещали страницу, то увеличиваем счётчик:
        session['visits_count'] = session.get('visits_count') + 1
        visits = session['visits_count']
        response = make_response(f'Количество посещений этой страницы: {visits}')
    else:
        # Если мы на странице в первый раз, то начинаем счёт:
        session['visits_count'] = 1
        response = make_response('Здравствуйте! Вы пришли на эту страницу в первый раз, '
                                 'или же заходили так давно, что мы о вас почти забыли;)')
    return response


# URL http://localhost:5000/logout
@app.route('/logout')
@login_required
def logout():
    """Выход из аккаунта"""
    logout_user()
    return redirect('/')


@app.errorhandler(404)
def not_found():
    """Обработка ошибки 404"""
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    db_session.global_init(DATABASE)
    app.register_blueprint(question_api.blueprint)  # Регистрация схемы Blueprint
    app.run(host='localhost', debug=True)
