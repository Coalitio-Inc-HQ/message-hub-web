# MessageHub FastApi Middleware server
FastApi сервер-прослойка между [copper main](https://github.com/Coalitio-Inc-HQ/MessageHubMain)
и [веб-клиентом](https://github.com/Coalitio-Inc-HQ/message-hub-fronte).
## Установка
### 1. Клонирование репозитория
```commandline
git clone https://github.com/Coalitio-Inc-HQ/message-hub-web.git
```
### 2. Создайте файл с переменными окружения
Для этого скопируйте `ex.env` и назовите файл `.env`.

Измените значения переменных при необходимости.
### 3. Сборка Докер контейнера
Для начала надо убедиться, что мы находимся в корне проекта, а именно в директории
`.../message-hub-web`.

Теперь можно начать сборку и запуск контейнера:
```commandline
docker build . -t app
docker run -p 8000:8000 app
```
При необходимости измените название контейнера `app`, а также порт. Однако в таком случае
важно изменить порт и в переменных окружения.
### 4. Радуемся
Вуаля, удачи!