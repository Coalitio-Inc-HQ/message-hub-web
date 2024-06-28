const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require('socket.io');
const WebSocket = require('ws');
const { setEventHandler, getEventHandler } = require('./eventHandlers'); // Импорт функций из модуля

const WS_LISTENER_URL = process.env.WS_LISTENER_URL || 'ws://localhost:8000/ws_listener';
let wsClient;

// Обработчики действий
const actions = {
    get_waiting_chats: (body) => {
        return new Promise((resolve, reject) => {
            const actionDTO = {
                name: "get_waiting_chats",
                body: { count: body.count }
            };
            console.log(`Sending request for waiting chats with count: ${body.count}`);
            try {
                wsClient.send(JSON.stringify(actionDTO));
                resolve();
            } catch (err) {
                reject(err);
            }
        });
    },
    get_chats_by_user: (body) => {
        return new Promise((resolve, reject) => {
            const actionDTO = {
                name: "get_chats_by_user",
                body: { user_id: body.user_id }
            };
            console.log(`Sending request for chats by user with user_id: ${body.user_id}`);
            try {
                wsClient.send(JSON.stringify(actionDTO));
                resolve();
            } catch (err) {
                reject(err);
            }
        });
    },
    get_messages_by_chat: (body) => {
        return new Promise((resolve, reject) => {
            const actionDTO = {
                name: "get_messages_by_chat",
                body: {
                    chat_id: body.chat_id,
                    count: body.count,
                    offset_message_id: body.offset_message_id
                }
            };
            console.log(`Sending request for messages by chat with chat_id: ${body.chat_id}, count: ${body.count}, offset_message_id: ${body.offset_message_id}`);
            try {
                wsClient.send(JSON.stringify(actionDTO));
                resolve();
            } catch (err) {
                reject(err);
            }
        });
    },
    send_message_to_chat: (body) => {
        return new Promise((resolve, reject) => {
            const actionDTO = {
                name: "send_message_to_chat",
                body: {
                    user_id: body.user_id,
                    chat_id: body.chat_id,
                    message: {
                        id: body.message.id,
                        chat_id: body.chat_id,
                        sender_id: body.user_id,
                        sended_at: new Date().toISOString(),
                        text: body.message.text
                    }
                }
            };
            console.log(`Sending message to chat with chat_id: ${body.chat_id}, user_id: ${body.user_id}, message: ${body.message.text}`);
            try {
                wsClient.send(JSON.stringify(actionDTO));
                resolve();
            } catch (err) {
                reject(err);
            }
        });
    }
};

const handleWebSocketMessage = (message) => {
    const data = JSON.parse(message);
    console.log(data);

    const eventHandler = getEventHandler(data.name);
    if (eventHandler) {
        eventHandler(data);
    } else {
        console.log(`No handler for event: ${data.name}`);
    }
};

// Функция для подключения к WebSocket серверу
const connectToWebSocket = (get_waiting_chats = null, get_chats_by_user = null, get_messages_by_chat = null, send_message_to_chat = null) => {
    wsClient = new WebSocket(WS_LISTENER_URL);

    setEventHandler('get_waiting_chats', get_waiting_chats);
    setEventHandler('get_chats_by_user', get_chats_by_user);
    setEventHandler('get_messages_by_chat', get_messages_by_chat);
    setEventHandler('send_message_to_chat', send_message_to_chat);

    wsClient.on('open', () => {
        console.log('Connected to WebSocket server');
    });

    wsClient.on('message', handleWebSocketMessage);

    wsClient.on('close', () => {
        console.log('WebSocket connection closed. Reconnecting...');
        setTimeout(connectToWebSocket, 5000);
    });

    wsClient.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
};

// Подключение к WebSocket серверу
connectToWebSocket(
    (data) => { console.log('get_waiting_chats', data); },
    (data) => { console.log('get_chats_by_user', data); },
    (data) => { console.log('get_messages_by_chat', data); },
    (data) => { console.log('send_message_to_chat', data); }
);

module.exports = { actions, connectToWebSocket };
