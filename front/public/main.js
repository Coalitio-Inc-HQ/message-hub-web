const socket = io();
const username = prompt('Как вас зовут?');

const chat = document.querySelector('.chat');
const input = document.getElementById('msg');
const nameDisplay = document.getElementById('name');
const chatList = document.querySelector('.chat-list');

nameDisplay.innerHTML = `Вы: ${username}`;

let currentChatId = 1; // ID текущего выбранного чата
let messages = {
    1: [], // Сообщения для чата 1
    2: [], // Сообщения для чата 2
    3: []  // Сообщения для чата 3
};

// Обработчик отправки сообщений
document.querySelector('.form').addEventListener('submit', e => {
    e.preventDefault();
    if (input.value.trim() !== "") {
        const message = { name: username, body: input.value, chatId: currentChatId };
        messages[currentChatId].push(message); // Сохранение сообщения в текущем чате
        addMessageToChat(message); // Добавление сообщения в интерфейс
        socket.emit('send_msg', message); // Отправка сообщения на сервер
        input.value = ''; // Очистка поля ввода
    }
});

// Обработчик получения новых сообщений
socket.on('new_msg', obj => {
    console.log("Получено новое сообщение", obj);
    if (!messages[obj.chatId]) {
        messages[obj.chatId] = [];
    }
    // Проверка на дублирование
    const lastMessage = messages[obj.chatId][messages[obj.chatId].length - 1];
    if (lastMessage && lastMessage.body === obj.body && lastMessage.name === obj.name) {
        return; // Пропускаем дублирующее сообщение
    }
    messages[obj.chatId].push(obj); // Сохранение сообщения в соответствующем чате
    if (obj.chatId === currentChatId) {
        addMessageToChat(obj); // Отображение сообщения, если чат активен
    }
});

// Обработчик получения новых чатов
socket.on('new_chat', obj => {
    console.log("Получен новый чат", obj);
    if (!messages[obj.chatId]) {
        messages[obj.chatId] = [];
    }
    addChatToSidebar(obj.name, obj.chatId); // Добавление нового чата в боковую панель
});

// Обработчик выбора чата
chatList.addEventListener('click', (e) => {
    if (e.target && e.target.matches('.chat-item')) {
        const chatId = parseInt(e.target.getAttribute('data-chat-id'));
        if (chatId !== currentChatId) {
            document.querySelector('.chat-item.active')?.classList.remove('active'); // Удаление класса .active с предыдущего выбранного чата
            currentChatId = chatId;
            e.target.classList.add('active'); // Добавление класса .active к новому выбранному чату
            loadChatMessages(chatId); // Загрузка сообщений выбранного чата
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

// Функция загрузки сообщений выбранного чата
function loadChatMessages(chatId) {
    chat.innerHTML = '';
    messages[chatId].forEach(addMessageToChat); // Отображение всех сообщений выбранного чата
}

// Функция добавления чата в боковую панель
function addChatToSidebar(name, chatId) {
    const li = document.createElement('li');
    li.classList.add('chat-item');
    li.setAttribute('data-chat-id', chatId);
    li.innerText = name;
    chatList.appendChild(li);
}
