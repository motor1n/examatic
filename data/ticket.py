from random import shuffle
from datetime import date


TARGETFILENAME = f'exam---{date.today().isoformat()}.txt'


def create_tickets(number):
    """Генератор перемешанного набора экзаменационных билетов"""
    tickets_list = list(range(1, number + 1))
    shuffle(tickets_list)
    return tickets_list


def create_questions(number):
    """Функция формирует номера вопросов для одного билета"""
    if number == 1:
        return tickets.pop()
    else:
        return sorted([tickets.pop() for _ in range(number)])


if __name__ == '__main__':
    number_questions = int(input('Количество экзаменационных вопросов: '))
    questions_in_ticket = int(input('Количество вопросов в билете: '))
    number_students = int(input('Количество студентов: '))
    print()
    students = dict()
    while number_students:
        tickets = create_tickets(number_questions)
        while tickets and number_students:
            student = input('Фамилия Имя Отчество: ')
            try:
                students[student] = create_questions(questions_in_ticket)
            except IndexError as error:
                tickets = create_tickets(number_questions)
                students[student] = create_questions(questions_in_ticket)
            print(f'Студент: {student} ➤ вопрос(ы): {students[student]}\n')
            number_students -= 1
    print('Все студенты с билетами.')
    with open(TARGETFILENAME, mode='tw', encoding='utf-8') as f:
        f.writelines([f'{s} ➤ вопрос(ы): {q}\n' for s, q in students.items()])
