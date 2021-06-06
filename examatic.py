"""
examatic 1.1.1
Exam-a-Ticket Generator
developed on flask
"""

import os
import datetime as dt
from flask import (
    Flask,
    render_template,
    make_response,
    session,
    jsonify
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.utils import redirect
from data import db_session
from data.question import Question
from data.resource_tickets import IssuedTickets
from data.resource_questions import QueRes, QueLiRes
from data.users import User
from data.register import RegisterForm
from data.login import LoginForm
from data.ticket import Ticket
from flask_restful import Api
from decouple import config


# База данных:
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

# Чтение регистрационных данных Telegram-бота из переменных среды:
TELEGRAM_CHAT_ID = config('TELEGRAM_CHAT_ID', default='')
TELEGRAM_TOKEN = config('TELEGRAM_TOKEN', default='')

# Создаём приложение Flask:
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = dt.timedelta(days=365)
api = Api(app)

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
    db_questions = db.query(Question).filter(Question.is_published == 1).order_by(Question.number)
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
        user.surname = regform.surname.data
        user.name = regform.name.data
        user.middlename = regform.middlename.data
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
            telegram_chat_id=TELEGRAM_CHAT_ID,
            telegram_token=TELEGRAM_TOKEN,
            ticket=current_ticket,
            source_time=TIME,
            time=time_left.seconds
        )
    else:
        # Иначе у пользователя ещё нет билета:
        try:
            # Обработка исключения, когда формирование очередного билета
            # вызовет обращение к несуществующему элементу:
            ticket.tickets[current_user_email] = create_ticket(QUESTIONS_IN_TICKET)
        except IndexError:
            # В этом случае заново генерируем новый набор номеров вопросов:
            questions = ticket.create_questions(count_questions())
            # И создаём новый билет из нового набора:
            ticket.tickets[current_user_email] = create_ticket(QUESTIONS_IN_TICKET)

        # Заполняем билет текстами вопросов по их номерам:
        current_ticket = [lst[q_num] for q_num in ticket.tickets[current_user_email]]

        try:
            # Добавляем в билет номер практического задания:
            current_ticket.append(create_practic_number())
        except IndexError:
            practics = ticket.create_practics(number_practics)
            current_ticket.append(create_practic_number())

        # Добавляем билет в базу данных:
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
            telegram_chat_id=TELEGRAM_CHAT_ID,
            telegram_token=TELEGRAM_TOKEN,
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
    # Рендерим билеты на шаблон страницы:
    return render_template('issued.html', tickets=db_tickets)


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


def clear_table(table):
    """Очистка таблицы БД"""
    db = db_session.create_session()
    db.query(table).delete()
    db.commit()


if __name__ == '__main__':
    db_session.global_init(DATABASE)

    # Очищаем перед началом нового экзамена
    # таблицу users (пользователи) и tickets (экзаменационные билеты):
    clear_table(User)
    clear_table(Ticket)
    # Если очистка не требуется - закомментировать.

    # Добавляем классы из resources.py в настройки API:
    api.add_resource(IssuedTickets, '/api/issued')
    api.add_resource(QueLiRes, '/api/question')
    api.add_resource(QueRes, '/api/question/<int:question_id>')

    # Создаём экземпляр объекта "Билет":
    ticket = Ticket()

    # Запускаем web-приложение локально:
    # app.run(host='localhost', debug=True)

    # Запускаем web-приложение на Heroku:
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
