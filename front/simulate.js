const io = require('socket.io-client');
const socket = io('http://localhost:3000');

socket.on('connect', () => {
    console.log('Подключено к серверу WebSocket');

    // Запрос ожидания чатов
    socket.emit('get_waiting_chats');

    // Запрос чатов пользователя
    socket.emit('get_chats_by_user', 'User1');

    // Запрос сообщений из чата
    socket.emit('get_messages_from_chat', 1);

    // Отправка сообщения в чат
    socket.emit('send_msg', {
        name: 'User1',
        body: 'Test message from User1',
        chatId: 1
    });
});

// Обработчик получения ожидающих чатов
socket.on('waiting_chats', (waitingChats) => {
    console.log('Ожидающие чаты:', waitingChats);
});

// Обработчик получения чатов пользователя
socket.on('user_chats', (userChats) => {
    console.log('Чаты пользователя:', userChats);
});

// Обработчик получения сообщений из чата
socket.on('chat_messages', (messages) => {
    console.log('Сообщения из чата:', messages);
});

// Обработчик получения новых сообщений
socket.on('new_msg', (msg) => {
    console.log('Новое сообщение:', msg);
});

// Обработчик получения новых чатов
socket.on('new_chat', (chat) => {
    console.log('Новый чат:', chat);
});
