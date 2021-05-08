"""examatic RESTfull API: ресурс для работы с экзаменационными билетами"""

from flask import jsonify
from flask_restful import Resource
from . import db_session
from .ticket import Ticket


class IssuedTickets(Resource):
    @staticmethod
    def get():
        db = db_session.create_session()
        ticket = db.query(Ticket).all()
        return jsonify(
            {
                'ticket': [item.to_dict(
                    only=(
                        'id',
                        'question1',
                        'question2',
                        'practic',
                        'user.surname',
                        'user.name',
                        'user.middlename'
                    )
                ) for item in ticket]
            }
        )
