import { io } from 'socket.io-client';
import eventHandlers from './eventHandlers';

let socket;

export function connectToWebSocket() {
    socket = io();

    socket.on('get_waiting_chats', (data) => {
        const handler = eventHandlers.get_waiting_chats;
        if (handler) handler(data);
    });

    socket.on('get_chats_by_user', (data) => {
        const handler = eventHandlers.get_chats_by_user;
        if (handler) handler(data);
    });

    socket.on('get_messages_by_chat', (data) => {
        const handler = eventHandlers.get_messages_by_chat;
        if (handler) handler(data);
    });

    socket.on('send_message_to_chat', (data) => {
        const handler = eventHandlers.send_message_to_chat;
        if (handler) handler(data);
    });
}

export function emitEvent(event, data) {
    if (socket) {
        socket.emit(event, data);
    } else {
        console.error('Socket is not connected');
    }
}
