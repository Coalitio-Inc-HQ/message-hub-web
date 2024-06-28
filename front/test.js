const WebSocket = require('ws');
const { setEventHandler } = require('./eventHandlers');

const WS_LISTENER_URL = process.env.WS_LISTENER_URL || 'ws://localhost:8000/ws_listener';

const sendTestData = (action, ws) => {
    ws.send(JSON.stringify(action), (err) => {
        if (err) {
            console.error(`Error sending test data for action: ${action.name}`, err);
        } else {
            console.log(`Test data sent for action: ${action.name}`);
        }
    });
};

const testData = {
    get_waiting_chats: {
        name: "get_waiting_chats",
        body: {
            count: 5
        }
    },
    get_chats_by_user: {
        name: "get_chats_by_user",
        body: {
            user_id: 1
        }
    },
    get_messages_by_chat: {
        name: "get_messages_by_chat",
        body: {
            chat_id: 1,
            count: 10,
            offset_message_id: -1
        }
    },
    send_message_to_chat: {
        name: "send_message_to_chat",
        body: {
            user_id: 1,
            chat_id: 1,
            message: {
                id: 1,
                chat_id: 1,
                sender_id: 1,
                sended_at: new Date().toISOString(),
                text: "Hello, this is a test message"
            }
        }
    }
};

const handleWebSocketMessage = (message) => {
    const data = JSON.parse(message);
    console.log(data);
};

const connectAndSendTestData = () => {
    const ws = new WebSocket(WS_LISTENER_URL);

    ws.on('open', () => {
        console.log('Connected to WebSocket server');
        sendTestData(testData.get_waiting_chats, ws);
        //sendTestData(testData.get_chats_by_user, ws);
        //sendTestData(testData.get_messages_by_chat, ws);
        //sendTestData(testData.send_message_to_chat, ws);
    });

    ws.on('message', handleWebSocketMessage);

    ws.on('close', () => {
        console.log('WebSocket connection closed');
    });

    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
};

// Подключение и отправка тестовых данных
connectAndSendTestData();

module.exports = { connectAndSendTestData };
