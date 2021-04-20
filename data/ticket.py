from random import shuffle
# from datetime import date
# from data import db_session
from data.question import Question
# from examatic import DATABASE


class Ticket:
    def __init__(self, number_questions, questions_in_ticket):
        # Количество экзаменационных вопросов:
        self.number_questions = number_questions
        # Количество вопросов в одном билете:
        self.questions_in_ticket = questions_in_ticket
        # Список премешанных номеров экзаменационных вопросов:
        # self.questions = [10, 8, 1, 11, 17, 7, 9, 3, 16, 12, 0, 14, 2, 15, 6, 4, 5, 13, 18, 19]
        # Словарь для хранения выданных билетов:
        self.tickets = dict()

    @staticmethod
    def load_questions(db):
        """Загрузка готовых вопросов из базы данных в список"""
        # db = db_session.create_session()
        # Фильтруем вопросы - оставляем готовые:
        db_questions = db.query(Question).filter(Question.is_published == 1)
        return [item.content for item in db_questions]

    def count_questions(self, db):
        """Определение количества вопросов"""
        return len(self.load_questions(db))

    @staticmethod
    def create_questions(number):
        """Генератор перемешанного набора экзаменационных вопросов"""
        # number - количество экзаменационных вопросов
        tickets_list = list(range(number))
        # Перемешиваем номера:
        shuffle(tickets_list)
        return tickets_list


"""
if __name__ == '__main__':
    ticket = Ticket(NUMBER_QUESTIONS, QUESTIONS_IN_TICKET)

    # Бесконечный цикл:
    while True:
        # Генерируем набор перемешанных вопросов:
        questions = ticket.create_questions(NUMBER_QUESTIONS)
        print(questions)

        # Пока имеются вопросы в очередном наборе:
        while questions:
            student = input('Фамилия Имя Отчество: ')

            # Обработка исключения, когда формирование очередного билета
            # вызовет обращение к несуществующему элементу:
            try:
                ticket.tickets[student] = ticket.create_ticket(QUESTIONS_IN_TICKET)
            except IndexError as error:
                # В этом случае заново генерируем новый набор вопросов:
                questions = ticket.create_questions(NUMBER_QUESTIONS)
                # И создаём новый билет из нового набора:
                ticket.tickets[student] = ticket.create_ticket(QUESTIONS_IN_TICKET)

            # Выводим сообщение:
            print(f'Студент: {student} ➤ вопрос(ы): {ticket.tickets[student]}\n')
            print(ticket.tickets)

        tickets = [f'{s} ➤ вопрос(ы): {q}\n' for s, q in ticket.tickets.items()]
"""
