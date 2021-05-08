![examatic-logo](static/img/examatic.svg 'examatic')

---

# Краткая характеристика

* Наименование программы: **examatic** (Exam-a-Ticket generator) - генератор экзаменационных билетов.
* Назначение программы: web-приложение предназначено для выдачи **случайных билетов** при проведении экзамена в онлайн-режиме.  
* Конечные пользователи: **преподаватели и студенты вуза**.

# Техническое задание
При помощи **web-программирования** создать приложение, реализующее выдачу случайных экзаменационных билетов при проведении онлайн-экзамена. Имеется список экзаменационных вопросов и набор практических заданий. Из этого списка следует генерировать **случайные билеты**, состоящие из двух вопросов и одного практического задания по **классическому** алгоритму:

**1**. Изначально все билеты выложены на столе.

**2**. Первый студент берёт один случайный билет.

**3**. После ответа студента, билет убирается из кучи, как использованный.

**4**. Так продолжается до тех пор, пока не закончатся, либо экзаменационные билеты, либо студенты.

**5**. Если студенты закончились раньше билетов, то никаких дополнительных действий не требуется — все студенты с билетами, работа алгоритма завершается.

**6**. Если билеты закончились раньше, чем студенты, то генерируется новый набор билетов и экзамен продолжается по указанному выше алгоритму.

**7**. Работа алгоритма завершается, когда каждый студент получил экзаменационный билет.

На **главной** странице web-приложения разместить **список** экзаменационных вопросов. Организовать **онлайн-регистрацию** студентов на экзамен. При регистрации каждый студент должен заполнить следующие **данные** о себе:

+ фамилия;  
+ имя;  
+ отчество;  
+ электронная почта.

После регистрации студент **автоматически** отправляется на страницу получения экзаменационного билета. В момент получения билета, начинается обратный **отсчёт времени**, выделенного на подготовку к ответу. По истечении времени подготовки, отправляется **сообщение** в специальный Telegram-канал преподавателю. Сообщение содержит фамилию, имя, отчество студента и вопросы его билета. Преподаватель вызывает студента на ответ.

Выданные билеты фиксируются в **базе данных**. При этом сохраняются следующие **сведения**:

+ фамилия, имя, отчество, e-mail студента;
+ номера вопросов и практического задания, полученные студентом;  
+ точное время выдачи билета.

# Сборка и запуск

Разработка и тестирование программы было осуществлено в операционной системе **Manjaro Linux 21.0.3 Ornara**. Для успешного запуска и нормальной работы должно быть установлено следующее программное обеспечение:

+ язык **Python 3.9.4**  
+ веб-фреймворк **Flask 1.1.2**  
+ библиотека **Werkzeug 1.0.1**  
+ библиотека **SQLAlchemy 1.4.13**
+ библиотека **SQLAlchemy-serializer 1.3.4.4**

Кроме того, необходимо установить дополнительные **расширения** для Flask:  

+ **Flask-Login 0.5.0**  
+ **Flask-WTF 0.14.3**  
+ **Flask-RESTful 0.3.8**

Для работы системы автоматического оповещения преподавателя **требуется**:

+ мессенджер **Telegram** с рабочим аккаунтом;
+ рабочий **чат-бот** в Telegram;
+ **публичный канал** в Telegram.

## Настройка Telegram-бота

Для того чтобы Telegram-бот принимал оповещения от **examatic** и печатал их в Telegram-канале, необходимо добавить вашего бота в качестве **администратора** с минимальными правами:

![telegram-bot-01](static/img/docpic/telegram-bot-01.png 'Настройки telegram-бота')

Проверить работу бота можно, выполнив **URL-запрос** в браузере:

```html
https://api.telegram.org/bot[BOT_API_KEY]/sendMessage?chat_id=[MY_CHANNEL_NAME]&text=[MY_MESSAGE_TEXT]
```

+ BOT_API_KEY - это **ключ API** (токен), сгенерированный BotFather при создании вашего бота (например, **1835402325:AFKGiMbK3GSFuyJnfvAXZEv0tQkoNZUr4pZ**);
+ MY_CHANNEL_NAME - название или ID вашего канала (например, **@my_channel_name** или **-1018474137298**);
+ MY_MESSAGE_TEXT - сообщение, которое вы хотите отправить.

**URL-запрос** может выглядеть примерно так:

```html
https://api.telegram.org/bot1835402325:AFKGiMbK3GSFuyJnfvAXZEv0tQkoNZUr4pZ/sendMessage?chat_id=@my_channel_name&text=Привет!
```

API вернёт ответ в формате **JSON**:

```json
{
  "ok":true,
  "result":{
    "message_id":1,
    "sender_chat":{
      "id":-1018474137298,
      "title":"examen",
      "username":"my_channel_name",
      "type":"channel"
    },
    "chat":{
      "id":-1018474137298,
      "title":"examen",
      "username":"my_channel_name",
      "type":"channel"
    },
    "date":1620273784,
    "text":"\u041f\u0440\u0438\u0432\u0435\u0442!"
  }
}
```

![](static/img/docpic/info-icon.png) Использование **id** предпочтительнее, поскольку идентификационный номер **не изменяется** в настройках и всегда привязан к **определённому** каналу.

## Редактирование JS-кода в template/ticket.html

Отправка сообщений из **examatic** в Telegram-канал реализована посредством **JavaScript**-кода:

```html
<script>
    /*
    Внимание: chat_id и token - не рабочие!
    Они указаны, как шаблон оформления кода.
    Необходимо заменить их на рабочие.
    chat_id - это id Telegram-канала
    token - это токен Telegram-бота
    */
    var chat_id = "-1018474137298";
    var token = "1835402325:AFKGiMbK3GSFuyJnfvAXZEv0tQkoNZUr4pZ";

    // Формирование сообщения:
    var text = "<b>{{surname}} {{name}} {{middlename}}</b>\nВремя подготовки окончилось!\n\n<b>Билет</b>:\n1. {{ticket[0]}}\n2. {{ticket[1]}}";

    // Функция отправки в Телеграм-канал сообщения об окончании времени подготовки к экзамену:
    function send_to_telegram(token, text, chat_id){
      var z=$.ajax({
      type: "POST",
      url: "https://api.telegram.org/bot" + token + "/sendMessage?chat_id=" + chat_id,
      data: "parse_mode=HTML&text=" + encodeURIComponent(text),
      });
     };

    var timerElem = document.querySelector('.timer'),
        // i - время в секундах
        i = {{time}},
        timerId = setInterval(function(){
            i--;
            timerElem.innerHTML = Math.floor(i / 60) + ':' + Math.floor(i % 60 / 10) + i % 60 % 10;
            if (i < 1){
                clearInterval(timerId);
                // Вызов функции отправки сообщения в Telegram-канал:
                send_to_telegram(token, text, chat_id);
            }
        },
        1000);
</script>
```

Для того чтобы данный код работал с **вашим** набором "Telegram-канал + Telegram-бот", необходимо внести **правки** в оригинальный код, указав **ID** канала и **токен** бота:

```html
var chat_id = "-1018474137298";
var token = "1835402325:AFKGiMbK3GSFuyJnfvAXZEv0tQkoNZUr4pZ";
```

# Функциональные возможности

Web-приложение **examatic** решает проблему выдачи **случайных экзаменационных билетов** при проведении экзамена в **онлайн-режиме**. При помощи **examatic** экзаменационные билеты выдаются студенту в **автоматическом** режиме и фиксируются в **базе данных**. При этом **индивидуально** по каждому студенту происходит отслеживание времени получения билета, а также запускается **обратный отсчёт времени** подготовки на экзаменационной странице. При окончании времени происходит автоматическое **оповещение преподавателя** в Telegram-канале с выводом данных:

+ фамилия; 
+ имя;
+ отчество;
+ вопросы билета.

Кроме того web-приложение **examatic** имеет **API** для просмотра выданных экзаменационных билетов и редактирования списка экзаменационных вопросов.

# Интерфейс web-приложения

## Главная страница

Главная страница отображает список экзаменационных вопросов с указанием направления и профиля подготовки экзаменуемых студентов.

![screen-01](static/img/docpic/screen-01.png 'Главная страница web-приложения')

## Страница регистрации

На странице регистрации пользователь вводит свои **данные**. Без регистрации **невозможно** получить экзаменационный билет и попасть на экзамен.

![screen-02](static/img/docpic/screen-02.png 'Страница регистрации')

В случае несовпадения введённого пароля и его подтверждения, пользователь получает сообщение об ощибке в виде **модального** окна.

![modal-01](static/img/docpic/modal-01.png 'Модальное окно: пароли не совпадают')

Если пользователь уже зарегистрирован в системе, то при попытке повторной регистрации он также получает предупреждающее сообщение.

![modal-02](static/img/docpic/modal-02.png 'Модальное окно: пользователь уже зарегестрирован в системе')

## Страница входа на экзамен

После регистрации пользователь **автоматически** перенаправляется на страницу выдачи экзаменационного билета.

![screen-03](static/img/docpic/screen-03.png 'Страница входа на экзамен')

В случае некорректного ввода регистрационных данных (e-mail или пароль) при входе на экзаменационную страницу пользователь получает соответствующее сообщение в виде модального окна. 

![modal-03](static/img/docpic/modal-03.png 'Модальное окно: неправильный логин или пароль')

## Экзаменационная страница

После нажатия кнопки **"Получить экзаменационный билет"** система случайным образом генерирует экзаменационный билет и сразу же начинает обратный отсчёт времени, выделенного на подготовку.

![screen-04](static/img/docpic/screen-04.png 'Экзаменационная страница')

По **истечении** времени подготовки, преподавателю приходят соотвествующие **сообщения** в Telegram-канал.

![telegram-bot-02](static/img/docpic/telegram-bot-02.png 'Сообщения в Telegram-канале')

# API examatic

## /issued

API examatic предназначено для просмотра выданных экзаменационных билетов и 
редактирования списка экзаменационных вопросов.



HTTP-запрос к API examatic  
соответствии со значениями параметров, передаваемых сервису в URL следующего 
формата:

{examatic-сервер}/api/{параметры_URL}



http://localhost:5000/api/question

question - просмотреть все вопросы

question/<int:question_id>


Строка {параметры URL} представляет собой последовательность пар вида {имя параметра}={значение параметра}, разделенных символом амперсанда (&).

Ниже приведен пример запроса изображения карты центра Москвы с двумя пронумерованными метками:

https://static-maps.yandex.ru/1.x/?ll=37.620070,55.753630&size=450,450&z=13&l=map&pt=37.620070,55.753630,pmwtm1~37.64,55.76363,pmwtm99


Просмотр выданных билетов

### скрин


## API: просмотр выданных билетов

```python
from requests import get


# Посмотреть все выданные билеты:
print(get('http://localhost:5000/api/issued').json())
```

## API: просмотр экзаменационных вопросов

```python
from requests import get


# Посмотреть все вопросы:
print(get('http://localhost:5000/api/question').json())

# Посмотреть вопрос с id == 3:
print(get('http://localhost:5000/api/question/3').json())

```

## API: добавление экзаменационного вопроса

```python
from requests import post


# Номер добавляемого экзаменационного вопроса:
number_question = 21

# Содержание экзаменационного вопроса:
content_question = 'Добавленный экзаменационный вопрос'

# POST-запрос:
print(
    post(
        'http://localhost:5000/api/question',
        json={
            'number': number_question,
            'content': content_question,
            'is_published': True,
            'user_id': 12
        }
    ).json()
)
```

## API: удаление экзаменационного вопроса


```python
from requests import delete


# id удаляемого вопроса:
question_id = 21

# Удаление вопроса с id == :
print(delete(f'http://localhost:5000/api/question/{question_id}').json())
```
