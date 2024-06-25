<template>
  <div>
    <input v-model="message" @keyup.enter="sendMessage"/>
    <button @click="sendMessage">Send</button>
    <p v-if="receivedMessage">Received: {{ receivedMessage }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: '',
      receivedMessage: ''
    };
  },
  mounted() {
    this.socket = new WebSocket('ws://localhost:8000/ws');
    this.socket.onmessage = (event) => {
      this.receivedMessage = event.data;
    };
  },
  methods: {
    sendMessage() {
      this.socket.send(this.message);
      this.message = '';
    }
  }
};
</script>