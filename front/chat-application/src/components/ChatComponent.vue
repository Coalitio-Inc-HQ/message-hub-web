<template>
  <div class="wrapper">
    <div class="sidebar">
      <h2>Ожидающие</h2>
      <ul class="chat-list waiting-chats">
        <li v-for="chat in waitingChats" :key="chat.chatId" @click="selectChat(chat.chatId)" class="chat-item">{{ chat.name }}</li>
      </ul>
      <h2>Прочитанные</h2>
      <ul class="chat-list read-chats">
        <li v-for="chat in userChats" :key="chat.chatId" @click="selectChat(chat.chatId)" class="chat-item">{{ chat.name }}</li>
      </ul>
    </div>
    <div class="main">
      <div id="name" class="name-display">Вы: {{ username }}</div>
      <ul class="chat">
        <li v-for="message in currentMessages" :key="message.id">
          <div class="name">{{ message.name }}</div>
          <div class="body">{{ message.body }}</div>
        </li>
      </ul>
      <form class="form" @submit.prevent="sendMessage">
        <textarea v-model="newMessage" placeholder="Введите сообщение..."></textarea>
        <button type="submit" class="send">Отправить</button>
      </form>
    </div>
  </div>
</template>

<script>
import { connectToWebSocket, emitEvent } from '@/services/index';
import { setEventHandler } from '@/services/eventHandlers';

export default {
  data() {
    return {
      username: '',
      waitingChats: [],
      userChats: [],
      currentChatId: null,
      currentMessages: [],
      newMessage: ''
    };
  },
  created() {
    this.username = prompt('Как вас зовут?');
    setEventHandler('get_waiting_chats', (data) => { this.waitingChats = data.chats; });
    setEventHandler('get_chats_by_user', (data) => { this.userChats = data.chats; });
    setEventHandler('get_messages_by_chat', (data) => { this.currentMessages = data.messages; });

    connectToWebSocket();
    emitEvent('get_waiting_chats', { user_id: this.username });
    emitEvent('get_chats_by_user', { user_id: this.username });
  },
  methods: {
    selectChat(chatId) {
      this.currentChatId = chatId;
      emitEvent('get_messages_by_chat', { chat_id: chatId });
    },
    sendMessage() {
      if (this.newMessage.trim() !== "") {
        const message = {
          id: Date.now(),
          chatId: this.currentChatId,
          name: this.username,
          body: this.newMessage
        };
        this.currentMessages.push(message);
        emitEvent('send_message_to_chat', message);
        this.newMessage = '';
      }
    }
  }
};
</script>

<style scoped>
@import '../assets/style.css';
</style>

<!-- 
<template>
  <div class="wrapper">
    <!-- Боковая панель с списком чатов -->
    <div class="sidebar">
      <h2>Ожидающие</h2>
      <ul class="chat-list waiting-chats">
        <li v-for="chat in waitingChats" :key="chat.chatId" @click="selectChat(chat.chatId)" class="chat-item">{{ chat.name }}</li>
      </ul>
      <h2>Прочитанные</h2>
      <ul class="chat-list read-chats">
        <li v-for="chat in userChats" :key="chat.chatId" @click="selectChat(chat.chatId)" class="chat-item">{{ chat.name }}</li>
      </ul>
    </div>
    <!-- Основная область для отображения сообщений -->
    <div class="main">
      <div id="name" class="name-display">Вы: {{ username }}</div>
      <ul class="chat">
        <li v-for="message in currentMessages" :key="message.id">
          <div class="name">{{ message.name }}</div>
          <div class="body">{{ message.body }}</div>
        </li>
      </ul>
      <!-- Форма для ввода и отправки сообщений -->
      <form class="form" @submit.prevent="sendMessage">
        <textarea v-model="newMessage" placeholder="Введите сообщение..."></textarea>
        <button type="submit" class="send">Отправить</button>
      </form>
    </div>
  </div>
</template>

<script>
import { io } from 'socket.io-client';

export default {
  data() {
    return {
      socket: null,
      username: '',
      waitingChats: [],
      userChats: [],
      currentChatId: null,
      currentMessages: [],
      newMessage: ''
    };
  },
  created() {
    this.username = prompt('Как вас зовут?');
    this.socket = io();

    this.socket.emit('get_waiting_chats');
    this.socket.on('waiting_chats', (waitingChats) => {
      this.waitingChats = waitingChats;
    });

    this.socket.emit('get_chats_by_user', this.username);
    this.socket.on('user_chats', (userChats) => {
      this.userChats = userChats;
    });

    this.socket.on('chat_messages', (chatMessages) => {
      this.currentMessages = chatMessages;
    });

    this.socket.on('new_msg', (obj) => {
      if (!this.currentMessages[obj.chatId]) {
        this.currentMessages[obj.chatId] = [];
      }
      this.currentMessages[obj.chatId].push(obj);
      if (obj.chatId === this.currentChatId) {
        this.addMessageToChat(obj);
      }
      if (!this.isChatInList(obj.chatId, this.userChats) && !this.isChatInList(obj.chatId, this.waitingChats)) {
        this.moveChatToWaiting(obj.chatId);
      }
    });

    this.socket.on('new_chat', (obj) => {
      if (!this.isChatInList(obj.chatId, this.userChats) && !this.isChatInList(obj.chatId, this.waitingChats)) {
        this.waitingChats.push(obj);
      }
    });
  },
  methods: {
    selectChat(chatId) {
      if (chatId !== this.currentChatId) {
        this.currentChatId = chatId;
        this.socket.emit('get_messages_from_chat', chatId);
      }
    },
    sendMessage() {
      if (this.newMessage.trim() !== "") {
        const message = { name: this.username, body: this.newMessage, chatId: this.currentChatId };
        if (!this.currentMessages[this.currentChatId]) {
          this.currentMessages[this.currentChatId] = [];
        }
        this.currentMessages[this.currentChatId].push(message);
        this.socket.emit('send_msg', message);
        this.newMessage = '';
        this.moveChatToRead(this.currentChatId);
      }
    },
    addMessageToChat(message) {
      this.currentMessages.push(message);
      this.$nextTick(() => {
        const chat = this.$el.querySelector('.chat');
        chat.scrollTop = chat.scrollHeight;
      });
    },
    moveChatToWaiting(chatId) {
      const chatIndex = this.userChats.findIndex(chat => chat.chatId === chatId);
      if (chatIndex !== -1) {
        const [chat] = this.userChats.splice(chatIndex, 1);
        this.waitingChats.push(chat);
      }
    },
    moveChatToRead(chatId) {
      const chatIndex = this.waitingChats.findIndex(chat => chat.chatId === chatId);
      if (chatIndex !== -1) {
        const [chat] = this.waitingChats.splice(chatIndex, 1);
        this.userChats.push(chat);
      }
    },
    isChatInList(chatId, list) {
      return list.some(chat => chat.chatId === chatId);
    }
  }
};
</script>

<style scoped>
@import '../assets/style.css';
</style>

-->
