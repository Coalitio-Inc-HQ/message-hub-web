# MessageHub FastApi Middleware server
FastApi сервер-прослойка между [copper main](https://github.com/Coalitio-Inc-HQ/MessageHubMain)
и [веб-клиентом](https://github.com/Coalitio-Inc-HQ/message-hub-fronte).

Данная ветка отличается использованием ngrok в связке с docker.
## Установка
### 1. Клонирование репозитория
```commandline
git clone https://github.com/Coalitio-Inc-HQ/message-hub-web.git
```
### 2. Создайте файл с переменными окружения
Для этого скопируйте `ex.env` и назовите файл `.env`.

Измените значения переменных при необходимости.

### 3. Создайте файл с настройками ngrok
Скопируйте `ex_ngrok.yaml` и назовите его `ngrok.yaml`, после
чего отредактируйте переменные в файле, вставили на место 
`<Токен>` ваш ngrok-токен, а на место `<Домен>` ваш ngrok-домен.

### 4. Сборка docker compose
Для начала надо убедиться, что мы находимся в корне проекта, а именно в директории
`.../message-hub-web`.

Теперь можно начать сборку и запуск docker-compose:
```commandline
docker compose build
docker compose run -d
```

### 5. Радуемся
Вуаля, удачи!