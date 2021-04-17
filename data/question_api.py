from . import db_session
from flask import Blueprint, jsonify, request
from .question import Question


blueprint = Blueprint('question_api', __name__, template_folder='templates')


# URl http://localhost:5000/api/question
@blueprint.route('/api/question')
def get_question():
    """Получение всех вопросов"""
    db = db_session.create_session()
    question = db.query(question).all()
    return jsonify(
        {
            'question': [item.to_dict(only=('title', 'content', 'user.name')) for item in question]
        }
    )


# Добавляем параметр `<int:question_id>` (целое число):
@blueprint.route('/api/question/<int:question_id>',  methods=['GET'])
def get_one_question(question_id):
    """Получение одного вопроса по его id"""
    db = db_session.create_session()
    # Передаём в запрос параметр question_id:
    question = db.query(question).get(question_id)
    if not question:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'question': question.to_dict(only=('title', 'content', 'user_id', 'is_published'))
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
    db = db_session.create_session()
    # Создаём вопрос, добывая информацию из тела запроса:
    question = question(
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
    db = db_session.create_session()
    question = db.query(question).get(question_id)
    if not question:
        return jsonify({'error': 'Not found'})
    db.delete(question)
    db.commit()
    return jsonify({'success': 'OK'})
