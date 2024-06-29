# Дубль два
Здесь будет фронт на Vue.js и сервера на FastAPI
# Терминология
- Глобальный пользователь — пользователь в системе message-hub, хранимый на сервере copper main
- Локальный пользователь — пользователь веба, хранимый на веб сервере (не фронт)
- Администратор — то же, что и локальный пользователь Веба
- Фронт — приложение на Vue.js, отображающее данные, который отправляет ему веб
- Веб — сервер на FastAPI, являющийся прослойкой между фронтом и copper main
- Чат — переписка пользователей. Имеет только chat_id. В одном чате может быть несколько пользователей
- Ожидающих чат — чат, в котором есть только пользователь (без администратора). Такой чат визуально отделяется от остальных
## Нейминг функций
- Приписка `answer_..` в начале функции означает, что это обработчик запроса на получение данных через вебсокет 
- Приписка `process_..` в начале функции означает, что это обработчик запроса на отправку данных через вебсокет
- Приписка `trigger_...` в начале функции означает, что это метод отправки данных через веб сокет

# Таблицы
1. user
# Веб
_Ответственный: Владислав "ladislav" Лага_

Что такое веб? Веб это сервера на FastAPI, через который будет происходить общение copper main с фронтом. Важно общаться с каждой системой на её языке.
Чаты создаются НЕ В ВЕБЕ. Чаты рождаются в copper main, после чего по запросу мы получаем список чатов пользователя.

Предлагаю сделать общение с copper main через запросы,
а уведомления веба через сокеты. Таким образом 
можно выделить следующие события от copper main.
## События от copper main:
* Появился новый ожидающий чат
* Пришло новое сообщение в чат
## Обращения к copper main
- **Зарегистрировать платформу**
    
    `register_plaform(url, platform_name)`
- **Зарегистрировать глобального пользователя**

    `register_user(platform_name, user_firstname) -> user_id` 
    При регистрации глобального пользователя отправляется имя платформы (например, 'web') и имя пользователя.
    Copper main возвращает нам id глобального пользователя(нового), который будет использоваться в качетсве id локального пользователя.
- ***Получить список ожидающих чатов***

    `get_waiting_chats(user_id) -> list[Chat]`
- **Подключить администратора к ожидающему чату**

    `read_chat_by_user(user_id, chat_id) -> Chat`
- **Добавить пользователя в чат**

    `add_user_to_chat(user_id, chat_id) -> None`
- **Получить список чатов пользователя (локальный)**

    `get_chats_by_user(user_id) -> list[Chat]`
- **Получить сообщения в чате**

    `get_messages_from_chat(chat_id, count) -> list[Message]`
- **Отправить сообщение в чат**

    `send_message_to_chat(message) -> None` Отправляем сообщение в чат. Сообщение (message) содержит в себе как id отправителя, так и chat_id
## Обращения от copper main
* **Отправить сообщение в чат**

  `send_message_to_chat(message)` отправляем сообщение от глобального пользователя в чат

# Фронт
_Ответственный: Крылов "whoami" Василий_

Фронт — приложение на Vue.js, отображающее данные, который отправляет ему веб.

Пользователь фронта имеет преимущества над пользователями
ботов. Его условно можно назвать администратором.

Все пользователи веба видят ожидающие чаты (чаты с одним пользователем)
и имеют доступ к чатам, в которых сами состоят.

При инициализации приложения необходимо получить список ожидающих
чатов и чатов пользователя.
При нажатии на ожидающий чат отправляется запрос на
снятие статуса "ожидающий" у чата (`read_chat_by_user`) и открывается окно
чата.

При открытии окна чата делается запрос на получение сообщений
из чата, после чего они выводятся в чате, отсортированные по
id, либо дате, пока не знаю.
Главное, что эти чаты, после получения их с сервера, хранятся у тебя
в условном массиве, связанном с определенным чатом.

Вывод сообщений зависит от id отправителя. То есть, сообщения
от текущего пользователя веба расположены справа, а всех остальных - слева.

## События от фронта
* Чат прочитан
* Отправка сообщения в чат
# Связывание
Общение через Сокеты. Устанавливаем соединение и ждем события.
# Описание интерфейса
Взаимодействие по сокетам происходит путём обмена экземпляров класса
**ActionDTO** (его описание лежит в `core/fastapi_app/schemes.py`).

Имена используемых запросов лежат в той же директории и указаны в
модели **ActionsMapTypedDict**

Формат **ActionDTO** таков:

```json
{
  "name": "example_name",
  "body": {
    "parameter_name": ParameterModel
  }
}
```
Например, при запросе на получение ожидающих чатов
необходимо отправить имя запроса имя пользователя (user_id).
```json
{
  "name": "get_waiting_chats",
  "body": {
    "user_id": 12
  }
}
```