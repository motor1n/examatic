from .db_session import create_session
from flask import Blueprint, jsonify, request
from .question import Question


blueprint = Blueprint('question_api', __name__, template_folder='templates')


# URl http://localhost:5000/api/question
@blueprint.route('/api/question')
def get_question():
    """Получение всех вопросов"""
    db = create_session()
    question = db.query(Question).all()
    return jsonify(
        {
            'question': [item.to_dict(
                only=('number', 'content', 'created_date', 'is_published')
            ) for item in question]
        }
    )


# Добавляем параметр `<int:question_id>` (целое число):
@blueprint.route('/api/question/<int:question_id>',  methods=['GET'])
def get_one_question(question_id):
    """Получение одного вопроса по его id"""
    db = create_session()
    # Передаём в запрос параметр question_id:
    question = db.query(Question).get(question_id)
    if not question:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'question': question.to_dict(
                only=('number', 'content', 'created_date', 'is_published')
            )
        }
    )


@blueprint.route('/api/question', methods=['POST'])
def create_question():
    """Добавление вопроса"""
    # Проверяем, что запрос содержит все требуемые поля и они корректные:
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'content', 'is_published', 'user_id']):
        return jsonify({'error': 'Bad request'})
    # Создаём сессию:
    db = create_session()
    # Создаём вопрос, добывая информацию из тела запроса:

    """
    ticket_tmp = Ticket(None, None)
    ticket_tmp.user_id = current_user.id
    ticket_tmp.question1 = ticket.tickets[user_email][0]
    ticket_tmp.question2 = ticket.tickets[user_email][1]
    ticket_tmp.practic = ticket.tickets[user_email][2]
    db.add(ticket_tmp)
    db.commit()

    question = Question()
    question.title
    """
    question = Question(
        title=request.json['title'],
        content=request.json['content'],
        is_published=request.json['is_published'],
        user_id=request.json['user_id']
    )
    db.add(question)
    db.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/question/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    """Удаление вопроса по его id"""
    db = create_session()
    question = db.query(Question).get(question_id)
    if not question:
        return jsonify({'error': 'Not found'})
    db.delete(question)
    db.commit()
    return jsonify({'success': 'OK'})
