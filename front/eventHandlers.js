// Объект для хранения обработчиков событий
const eventHandlers = {
    get_waiting_chats: null, // Обработчик для события получения ожидающих чатов
    get_chats_by_user: null, // Обработчик для события получения чатов пользователя
    get_messages_by_chat: null, // Обработчик для события получения сообщений из чата
    send_message_to_chat: null // Обработчик для события отправки сообщения в чат
};

// Функция для установки обработчика события
/**
 * Устанавливает обработчик для указанного события.
 * @param {string} eventName - Имя события.
 * @param {function} handler - Функция-обработчик для события.
 */
const setEventHandler = (eventName, handler) => {
    // Проверяем, существует ли событие в объекте eventHandlers
    if (eventHandlers.hasOwnProperty(eventName)) {
        // Устанавливаем обработчик для события
        eventHandlers[eventName] = handler;
    } else {
        // Выводим предупреждение, если событие не существует в объекте eventHandlers
        console.warn(`Event handler for ${eventName} does not exist`);
    }
};

// Функция для получения обработчика события
/**
 * Получает обработчик для указанного события.
 * @param {string} eventName - Имя события.
 * @returns {function|null} - Функция-обработчик для события или null, если обработчик не найден.
 */
const getEventHandler = (eventName) => {
    // Проверяем, существует ли событие в объекте eventHandlers
    if (eventHandlers.hasOwnProperty(eventName)) {
        // Возвращаем обработчик для события
        return eventHandlers[eventName];
    } else {
        // Выводим предупреждение и возвращаем null, если событие не существует в объекте eventHandlers
        console.warn(`Event handler for ${eventName} does not exist`);
        return null;
    }
};

// Экспортируем функции и объект eventHandlers для использования в других модулях
module.exports = {
    setEventHandler, // Функция для установки обработчика события
    getEventHandler, // Функция для получения обработчика события
    eventHandlers // Объект для хранения обработчиков событий
};
