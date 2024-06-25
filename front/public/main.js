const socket = io();
const username = prompt('Как вас зовут?');

const chat = document.querySelector('.chat');
const input = document.getElementById('msg');
const nameDisplay = document.getElementById('name');
const waitingChatList = document.querySelector('.waiting-chats');
const readChatList = document.querySelector('.read-chats');

nameDisplay.innerHTML = `Вы: ${username}`;

let currentChatId = null; // ID текущего выбранного чата
let messages = {};

// Запрос ожидающих чатов при подключении
socket.emit('get_waiting_chats');

// Обработчик получения ожидающих чатов
socket.on('waiting_chats', (waitingChats) => {
    waitingChats.forEach(chat => {
        addChatToSidebar(chat.name, chat.chatId, 'waiting');
    });
});

// Запрос чатов пользователя при подключении
socket.emit('get_chats_by_user', username);

// Обработчик получения чатов пользователя
socket.on('user_chats', (userChats) => {
    userChats.forEach(chat => {
        addChatToSidebar(chat.name, chat.chatId, 'read');
    });
});

// Обработчик получения сообщений из чата
socket.on('chat_messages', (chatMessages) => {
    chat.innerHTML = '';
    chatMessages.forEach(message => {
        addMessageToChat(message);
    });
});

// Обработчик отправки сообщений
document.querySelector('.form').addEventListener('submit', e => {
    e.preventDefault();
    if (input.value.trim() !== "") {
        const message = { name: username, body: input.value, chatId: currentChatId };
        if (!messages[currentChatId]) {
            messages[currentChatId] = [];
        }
        messages[currentChatId].push(message); // Сохранение сообщения в текущем чате
        addMessageToChat(message); // Добавление сообщения в интерфейс
        socket.emit('send_msg', message); // Отправка сообщения на сервер
        input.value = ''; // Очистка поля ввода
        moveChatToRead(currentChatId); // Перемещение чата в прочитанные при отправке сообщения
    }
});

// Обработчик получения новых сообщений
socket.on('new_msg', obj => {
    console.log("Получено новое сообщение", obj);
    if (!messages[obj.chatId]) {
        messages[obj.chatId] = [];
    }
    // Проверка на дублирование сообщения
    const lastMessage = messages[obj.chatId][messages[obj.chatId].length - 1];
    if (lastMessage && lastMessage.body === obj.body && lastMessage.name === obj.name) {
        return; // Пропускаем дублирующее сообщение
    }
    messages[obj.chatId].push(obj); // Сохранение сообщения в соответствующем чате
    if (obj.chatId === currentChatId) {
        addMessageToChat(obj); // Отображение сообщения, если чат активен
    }
    // Если чат уже в списке прочитанных, не перемещаем его обратно в ожидающие
    if (!isChatInList(obj.chatId, readChatList) && !isChatInList(obj.chatId, waitingChatList)) {
        moveChatToWaiting(obj.chatId); // Перемещение чата в ожидающие при получении нового сообщения
    }
});

// Обработчик получения новых чатов
socket.on('new_chat', obj => {
    console.log("Получен новый чат", obj);
    if (!messages[obj.chatId]) {
        messages[obj.chatId] = [];
    }
    if (!isChatInList(obj.chatId, readChatList) && !isChatInList(obj.chatId, waitingChatList)) {
        addChatToSidebar(obj.name, obj.chatId, 'waiting'); // Добавление нового чата в ожидающие
    }
});

// Обработчик выбора чата
document.querySelector('.sidebar').addEventListener('click', (e) => {
    if (e.target && e.target.matches('.chat-item')) {
        const chatId = parseInt(e.target.getAttribute('data-chat-id'));
        if (chatId !== currentChatId) {
            document.querySelector('.chat-item.active')?.classList.remove('active'); // Удаление класса .active с предыдущего выбранного чата
            currentChatId = chatId;
            e.target.classList.add('active'); // Добавление класса .active к новому выбранному чату
            socket.emit('get_messages_from_chat', chatId); // Запрос сообщений выбранного чата
        }
    }
});

// Функция добавления сообщения в интерфейс
function addMessageToChat(message) {
    const li = document.createElement('li');
    li.innerHTML = `
        <div class="name">${message.name}</div>
        <div class="body">${message.body}</div>`;
    chat.appendChild(li);
    chat.scrollTop = chat.scrollHeight; // Прокрутка чата к последнему сообщению
}

// Функция добавления чата в боковую панель
function addChatToSidebar(name, chatId, type) {
    if (!isChatInList(chatId, readChatList) && !isChatInList(chatId, waitingChatList)) {
        const li = document.createElement('li');
        li.classList.add('chat-item');
        li.setAttribute('data-chat-id', chatId);
        li.innerText = name;
        if (type === 'waiting') {
            waitingChatList.appendChild(li);
        } else {
            readChatList.appendChild(li);
        }
    }
}

// Функция перемещения чата в ожидающие
function moveChatToWaiting(chatId) {
    const chatItem = document.querySelector(`.chat-item[data-chat-id="${chatId}"]`);
    if (chatItem && chatItem.parentElement !== waitingChatList) {
        chatItem.remove();
        waitingChatList.appendChild(chatItem);
    }
}

// Функция перемещения чата в прочитанные
function moveChatToRead(chatId) {
    const chatItem = document.querySelector(`.chat-item[data-chat-id="${chatId}"]`);
    if (chatItem && chatItem.parentElement !== readChatList) {
        chatItem.remove();
        readChatList.appendChild(chatItem);
    }
}

// Функция проверки, находится ли чат в указанном списке
function isChatInList(chatId, list) {
    return list.querySelector(`.chat-item[data-chat-id="${chatId}"]`) !== null;
}
