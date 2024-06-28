const eventHandlers = {
    get_waiting_chats: null,
    get_chats_by_user: null,
    get_messages_by_chat: null,
    send_message_to_chat: null
};

// Функция для установки обработчика события
export function setEventHandler(eventName, handler) {
    if (Object.prototype.hasOwnProperty.call(eventHandlers, eventName)) {
        eventHandlers[eventName] = handler;
    } else {
        console.warn(`Event handler for ${eventName} does not exist`);
    }
}

// Функция для получения обработчика события
export function getEventHandler(eventName) {
    if (Object.prototype.hasOwnProperty.call(eventHandlers, eventName)) {
        return eventHandlers[eventName];
    } else {
        console.warn(`Event handler for ${eventName} does not exist`);
        return null;
    }
}

// Экспортируем eventHandlers для прямого доступа, если необходимо
export default eventHandlers;
