const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);
const path = require('path');

//**
// Middleware для обработки JSON данных
app.use(express.json());

// Словарь для отслеживания активных чатов
let activeChats = {};

// Маршрут для получения сообщений от Telegram бота
app.post('/message', (req, res) => {
    const messageData = req.body;
    console.log('Получено сообщение от Telegram бота:', messageData);

    // Проверка, существует ли уже этот пользователь в активных чатах
    if (!activeChats[messageData.user_id]) {
        activeChats[messageData.user_id] = {
            name: messageData.full_name,
            messages: []
        };
        // Отправка информации о новом чате через WebSocket
        io.emit('new_chat', {
            name: messageData.full_name,
            chatId: messageData.user_id
        });
    }

    // Сохранение сообщения в активных чатах
    activeChats[messageData.user_id].messages.push({
        name: messageData.full_name,
        body: messageData.message_text
    });

    // Отправка сообщения через WebSocket на HTML страницу
    io.emit('new_msg', {
        name: messageData.full_name,
        body: messageData.message_text,
        chatId: messageData.user_id
    });

    res.status(200).send('Сообщение получено');
});

// Обработчик подключений через WebSocket
io.on('connection', (socket) => {
    console.log(`Новое подключение: ${socket.id}`);

    // Обработчик для события отправки сообщения от клиента (HTML страницы)
    socket.on('send_msg', async (data) => {  // Изменение на асинхронную функцию
        console.log(`Получено сообщение от клиента: ${data.body}`);

        // Проверка, существует ли уже этот пользователь в активных чатах
        if (!activeChats[data.chatId]) {
            activeChats[data.chatId] = {
                name: data.name,
                messages: []
            };
            // Отправка информации о новом чате через WebSocket
            io.emit('new_chat', {
                name: data.name,
                chatId: data.chatId
            });
        }

        // Сохранение сообщения в активных чатах
        activeChats[data.chatId].messages.push({
            name: data.name,
            body: data.body
        });

        // Отправка сообщения через WebSocket на HTML страницу
        io.emit('new_msg', {
            name: data.name,
            body: data.body,
            chatId: data.chatId
        });

        // Динамический импорт node-fetch
        const fetch = (await import('node-fetch')).default;

        // Отправка сообщения в Telegram бот
        const message = {
            chatId: data.chatId,
            text: `Сообщение от ${data.name}: ${data.body}`
        };

        try {
            const response = await fetch('http://localhost:8000/send-message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(message)
            });

            if (response.ok) {
                console.log('Сообщение успешно отправлено в Telegram');
            } else {
                console.error('Ошибка при отправке сообщения в Telegram');
            }
        } catch (error) {
            console.error('Ошибка при отправке запроса:', error);
        }
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
