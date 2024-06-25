const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);
const path = require('path');
const WebSocket = require('ws');

// Middleware для обработки JSON данных
app.use(express.json());

// Словарь для отслеживания активных чатов
let activeChats = {};

// Настройка WebSocket клиента
const WS_LISTENER_URL = process.env.WS_LISTENER_URL || 'ws://localhost:8000/ws_listener';
let wsClient;
let userId = 2; // Пример userId, замените на актуальный

function connectWebSocket() {
    wsClient = new WebSocket(WS_LISTENER_URL);

    wsClient.on('open', () => {
        console.log(`WebSocket клиент подключен к ${WS_LISTENER_URL}`);

        // Отправка запросов при подключении
        const actions = [
            {
                name: "get_waiting_chats",
                body: {
                    user_id: userId
                }
            },
            {
                name: "get_chats_by_user",
                body: {
                    user_id: userId
                }
            }
        ];

        actions.forEach(action => {
            console.log(`Отправка запроса ${action.name} при подключении: `, JSON.stringify(action, null, 2));
            wsClient.send(JSON.stringify(action));
        });
    });

    wsClient.on('message', (message) => {
        console.log(`Получено сообщение через WebSocket: ${message}`);
        let data;

        try {
            data = JSON.parse(message);
        } catch (error) {
            console.error(`Ошибка при разборе JSON: ${error.message}`);
            return;
        }

        function fixJsonString(jsonString) {
            // Заменяем одинарные кавычки на двойные
            let fixedString = jsonString.replace(/'/g, '"');
            // Удаляем возможные экранированные двойные кавычки
            fixedString = fixedString.replace(/\\"/g, '"');
            return fixedString;
        }

        // Обработка различных типов сообщений
        switch (data.name) {
            case 'get_waiting_chats':
                console.log("Метод: get_waiting_chats");
                try {
                    console.log(`Полученные чаты: ${data.body.chats}`);
                    const chats = JSON.parse(fixJsonString(data.body.chats));
                    io.emit('waiting_chats', chats);
                } catch (error) {
                    console.error(`Ошибка при разборе чатов: ${error.message}`);
                }
                break;
            case 'get_chats_by_user':
                console.log("Метод: get_chats_by_user");
                try {
                    console.log(`Полученные чаты: ${data.body.chats}`);
                    const chats = JSON.parse(fixJsonString(data.body.chats));
                    io.emit('user_chats', chats);
                } catch (error) {
                    console.error(`Ошибка при разборе чатов: ${error.message}`);
                }
                break;
            default:
                console.log(`Неизвестный метод: ${data.name}`);
        }
    });

    wsClient.on('close', () => {
        console.log('WebSocket соединение закрыто. Попытка переподключения через 5 секунд...');
        setTimeout(connectWebSocket, 5000); // Переподключение через 5 секунд
    });

    wsClient.on('error', (error) => {
        console.error(`WebSocket ошибка: ${error.message}`);
    });
}

// Инициализация WebSocket клиента
connectWebSocket();

io.on('connection', (socket) => {
    console.log(`Новое подключение: ${socket.id}`);

    // Обработчик получения ожидающих чатов
    socket.on('get_waiting_chats', () => {
        const actionDTO = {
            name: "get_waiting_chats",
            body: {
                user_id: userId
            }
        };

        console.log("Отправка запроса get_waiting_chats: ", JSON.stringify(actionDTO, null, 2));
        wsClient.send(JSON.stringify(actionDTO));
    });

    // Обработчик получения чатов пользователя
    socket.on('get_chats_by_user', () => {
        const actionDTO = {
            name: "get_chats_by_user",
            body: {
                user_id: userId
            }
        };

        console.log("Отправка запроса get_chats_by_user: ", JSON.stringify(actionDTO, null, 2));
        wsClient.send(JSON.stringify(actionDTO));
    });

    // Обработчик отключения клиента
    socket.on('disconnect', () => {
        console.log(`Клиент отключился: ${socket.id}`);
    });
});

// Middleware для обслуживания статических файлов
app.use(express.static(path.join(__dirname, 'public')));

// Маршрут для отображения HTML-страницы
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

// Запуск сервера
server.listen(3000, () => {
    console.log('Сервер слушает на порту 3000');
});
