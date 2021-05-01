"""
examatic 0.2.0
Exam-a-Ticket Generator
developed on flask
"""

import os
import datetime as dt
from flask import Flask, render_template, make_response, session, jsonify, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# from sqlalchemy import exc
# from sqlalchemy import or_
from werkzeug.exceptions import abort
from werkzeug.utils import redirect
from data import db_session
from data.question import Question, QuestionForm
from data.users import User
from data.register import RegisterForm
from data.login import LoginForm
from data.ticket import Ticket
from data import question_api


DATABASE = 'dbase/examen.db'

# Время на подготовку к экзамену (минут):
TIME = 50

# Количество вопросов в билете:
QUESTIONS_IN_TICKET = 2

# Путь к файлам практических заданий:
PATH_PRACTICS = 'static/img/practic'
# Количество практических заданий:
number_practics = len(os.listdir(path=PATH_PRACTICS))

# Список для перемешанного набора номеров вопросов:
questions = list()

# Список для перемешанного набора номеров практики:
practics = list()

# Готовый билет с вопросами (список строк) для текущего пользователя:
current_ticket = list()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = dt.timedelta(days=365)

# Инициализация менеджера логинов:
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
    # Фильтруем вопросы - оставляем готовые:
    db_questions = db.query(Question).filter(Question.is_published == 1)
    # Рендерим готовые вопросы на шаблон страницы:
    return render_template('index.html', questions=db_questions)


# URL http://localhost:5000/register
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    regform = RegisterForm()
    if regform.validate_on_submit():
        # Модальное окно на ошибку "Введённые пароли не совпадают":
        if regform.password.data != regform.password_again.data:
            return redirect('/register#iw-modal-01')
        db = db_session.create_session()
        # Модальное окно на ошибку "Такой пользователь уже есть":
        if db.query(User).filter(User.email == regform.email.data).first():
            return redirect('/register#iw-modal-02')
        # Считываем данные пользователя из формы:
        user = User()
        user.name = regform.name.data
        user.surname = regform.surname.data,
        user.middlename = regform.middlename.data,
        user.email = regform.email.data
        user.set_password(regform.password.data)
        # Добавляем юзера в БД:
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
            return redirect('/ticket')
        # Модальное окно в случае ошибки авторизации:
        return redirect('/login#iw-modal')
    return render_template('login.html', title='Авторизация', form=login_form)


# URL http://localhost:5000/ticket
@app.route('/ticket')
def ticket():
    """Экзаменационный билет"""
    global current_ticket, questions, practics
    db = db_session.create_session()

    # Почта текущего пользователя, именно по ней идёт авторизация:
    current_user_email = current_user.email

    # Список строк экзаменационных вопросов из базы данных:
    lst = ticket.load_questions(db)

    # Смотрим, есть ли id текущего пользователя в таблице tickets:
    ticket_tmp = db.query(Ticket).filter(Ticket.user_id == current_user.id).first()
    if ticket_tmp:
        # Если есть, то значит пользователь уже взял билет.
        # Читаем из БД билет, взятый пользователем ранее:
        current_ticket = [
            lst[ticket_tmp.question1 - 1],
            lst[ticket_tmp.question2 - 1],
            ticket_tmp.practic
        ]

        # Заменяем номер практического задания на путь к файлу:
        current_ticket[-1] = path_picture(current_ticket[-1])

        # Восстановление времени обратного отсчёта при закрытии страницы при помощи
        # разницы времени получения билета и текущим временем повторного захода на страницу.

        # Времени прошло:
        time_has_passed = dt.datetime.now() - ticket_tmp.created_date

        # Если прошедшее время больше чем выделенное, то его не осталось:
        if time_has_passed > dt.timedelta(minutes=TIME):
            time_left = dt.timedelta(seconds=1)
        else:
            # иначе, времени осталось:
            time_left = dt.timedelta(minutes=TIME) - time_has_passed

        # Рендерим билет на шаблон страницы:
        return render_template(
            'ticket.html',
            name=current_user.name,
            surname=current_user.surname,
            middlename=current_user.middlename,
            ticket=current_ticket,
            source_time=TIME,
            time=time_left.seconds
        )
    else:
        # Иначе у пользователя ещё нет билета.
        try:
            # Обработка исключения, когда формирование очередного билета
            # вызовет обращение к несуществующему элементу:
            ticket.tickets[current_user_email] = create_ticket(QUESTIONS_IN_TICKET)
        except IndexError:
            # В этом случае заново генерируем новый набор номеров вопросов:
            questions = ticket.create_questions(count_questions())
            # И создаём новый билет из нового набора:
            ticket.tickets[current_user_email] = create_ticket(QUESTIONS_IN_TICKET)

        print(f'Студент: {current_user_email} ➤ вопрос(ы): {ticket.tickets[current_user_email]}\n')

        # Заполняем билет текстами вопросов по их номерам:
        current_ticket = [lst[q_num] for q_num in ticket.tickets[current_user_email]]

        try:
            # Добавляем в билет номер практического задания:
            current_ticket.append(create_practic_number())
        except IndexError:
            practics = ticket.create_practics(number_practics)
            current_ticket.append(create_practic_number())

        print('questions:', questions)
        print('practics:', practics)
        print('current_ticket:', current_ticket)

        ticket_tmp = Ticket()
        ticket_tmp.user_id = current_user.id
        ticket_tmp.question1 = ticket.tickets[current_user_email][0] + 1
        ticket_tmp.question2 = ticket.tickets[current_user_email][1] + 1
        ticket_tmp.practic = current_ticket[-1]
        db.add(ticket_tmp)
        db.commit()

        # Заменяем номер практического задания на путь к файлу:
        current_ticket[-1] = path_picture(current_ticket[-1])

        # Рендерим билет на шаблон страницы:
        return render_template(
            'ticket.html',
            name=current_user.name,
            surname=current_user.surname,
            middlename=current_user.middlename,
            ticket=current_ticket,
            source_time=TIME,
            time=TIME*60
        )


# URL http://localhost:5000/issued
@app.route('/issued', methods=['GET'])
@login_required
def issued():
    """Список выданных билетов"""
    db = db_session.create_session()
    db_tickets = db.query(Ticket)
    # db_users = db.query(User)
    # db_tickets = db.query(Ticket).join(User, Ticket.user_id == User.name)
    # Рендерим билеты на шаблон страницы:
    return render_template('issued.html', tickets=db_tickets)


# URL http://localhost:5000/question
@app.route('/question',  methods=['GET', 'POST'])
@login_required
def add_question():
    """Добавление вопроса"""
    question_form = QuestionForm()
    if question_form.validate_on_submit():
        db = db_session.create_session()
        question = Question()
        question.number = question_form.number.data
        question.content = question_form.content.data
        question.is_published = not question_form.is_published.data
        current_user.question.append(question)
        db.merge(current_user)
        db.commit()
        return redirect('/')
    return render_template(
        'question.html',
        title='Добавление вопроса',
        form=question_form
    )


@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    """Редактирование вопроса"""
    question_form = QuestionForm()
    if request.method == 'GET':
        db = db_session.create_session()
        question = db.query(Question).filter(
            Question.id == question_id,
            Question.user == current_user
        ).first()
        if question:
            question_form.number.data = question.number
            question_form.content.data = question.content
            question_form.is_published.data = question.is_published
        else:
            abort(404)
    if question_form.validate_on_submit():
        db = db_session.create_session()
        question = db.query(Question).filter(
            Question.id == question_id,
            Question.user == current_user
        ).first()
        if question:
            question.number = question_form.number.data
            question.content = question_form.content.data
            question.is_published = question_form.is_published.data
            db.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template(
        'question.html',
        title='Редактирование вопроса',
        form=question_form
    )


@app.route('/question_delete/<int:question_id>', methods=['GET', 'POST'])
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


def count_questions():
    """Определение количества вопросов"""
    db = db_session.create_session()
    return len(ticket.load_questions(db))


def create_ticket(number):
    """Формирование номеров экзаменационных вопросов для одного билета"""
    # параметр number - количество вопросов в одном билете:
    if number == 1:
        # Возвращаем, если в билете всего один вопрос:
        return questions.pop()
    else:
        # Возращаем, если в билете более одного вопроса:
        return sorted([questions.pop() for _ in range(number)])


def create_practic_number():
    """Создание номера практического задания для экзаменационного билета"""
    if practics:
        # Если набор ещё не пустой, берём оттуда номер:
        return practics.pop()
    else:
        # Иначе создаём новый набор и берём номер оттуда:
        ticket.create_practics(number_practics)
        return practics.pop()


def path_picture(number_practic):
    """Формирование пути к изображению с практическим заданием"""
    # Добавление ведущих нулей в имя файла при помощи метода zfill()
    zeros = 3  # три ведущих нуля
    number_file = str(number_practic).zfill(zeros)
    return f'../static/img/practic/{number_file}.png'


if __name__ == '__main__':
    db_session.global_init(DATABASE)
    # Регистрация схемы Blueprint
    app.register_blueprint(question_api.blueprint)
    # Создаём экземпляр объекта "Билет":
    ticket = Ticket()
    app.run(host='localhost', debug=True)
