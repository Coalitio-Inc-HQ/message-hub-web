const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);
const path = require('path');

// Middleware для обработки JSON данных
app.use(express.json());

// Словарь для отслеживания активных чатов
// Словарь для отслеживания123активных чатов
let activeChats = {
    1: { name: 'Alice', messages: [{ name: 'Alice', body: 'Hello!' }], read: false },
    2: { name: 'Bob', messages: [{ name: 'Bob', body: 'Hi!' }], read: true }
};

io.on('connection', (socket) => {
    console.log(`Новое подключение: ${socket.id}`);

    // Обработчик получения ожидающих чатов
    socket.on('get_waiting_chats', () => {
        const waitingChats = Object.keys(activeChats).filter(chatId => !activeChats[chatId].read).map(chatId => {
            return { chatId, name: activeChats[chatId].name };
        });
        socket.emit('waiting_chats', waitingChats);
    });

    // Обработчик получения чатов пользователя
    socket.on('get_chats_by_user', (username) => {
        const userChats = Object.keys(activeChats).filter(chatId => activeChats[chatId].name === username).map(chatId => {
            return { chatId, name: activeChats[chatId].name };
        });
        socket.emit('user_chats', userChats);
    });

    // Обработчик получения сообщений из чата
    socket.on('get_messages_from_chat', (chatId) => {
        if (activeChats[chatId]) {
            socket.emit('chat_messages', activeChats[chatId].messages);
        } else {
            socket.emit('chat_messages', []);
        }
    });

    // Обработчик отправки сообщения от клиента (HTML страницы)
    socket.on('send_msg', async (data) => {
        console.log(`Получено сообщение от клиента: ${data.body}`);

        // Проверка, существует ли уже этот пользователь в активных чатах
        if (!activeChats[data.chatId]) {
            activeChats[data.chatId] = {
                name: data.name,
                messages: [],
                read: false
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
