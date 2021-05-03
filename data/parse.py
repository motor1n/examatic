"""RESTfull API: парсинг запроса"""

from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('number', required=True, type=int)
parser.add_argument('content', required=True)
parser.add_argument('is_published', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)
