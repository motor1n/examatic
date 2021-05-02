"""Ресурс для работы с экзаменационными вопросами"""

from flask import jsonify
from flask_restful import abort, Resource
from . import db_session
from .question import Question
from .parse import parser


def not_found(question_id):
    db = db_session.create_session()
    question = db.query(Question).get(question_id)
    if not question:
        abort(404, message=f'Вопрос {question_id} не найден')


class QueRes(Resource):
    @staticmethod
    def get(question_id):
        not_found(question_id)
        db = db_session.create_session()
        question = db.query(Question).get(question_id)
        return jsonify(
            {
                'question': question.to_dict(
                    only=(
                        'number',
                        'content',
                        'is_published',
                        'user_id'
                    )
                )
            }
        )

    @staticmethod
    def delete(question_id):
        not_found(question_id)
        db = db_session.create_session()
        question = db.query(Question).get(question_id)
        db.delete(question)
        db.commit()
        return jsonify({'success': 'OK'})


class QueLiRes(Resource):
    @staticmethod
    def get():
        db = db_session.create_session()
        question = db.query(Question).all()
        return jsonify(
            {
                'question': [item.to_dict(
                    only=('number', 'content', 'user.name')) for item in question]
            }
        )

    @staticmethod
    def post():
        args = parser.parse_args()
        db = db_session.create_session()
        question = Question()
        question.number = args['number']
        question.content = args['content']
        question.is_published = args['is_published']
        question.user_id = args['user_id']
        db.add(question)
        db.commit()
        return jsonify({'success': 'OK'})
