<template>
  <div id="app">
    <ChatComponent />
  </div>
</template>

<script>
import ChatComponent from './components/ChatComponent.vue';

export default {
  name: 'App',
  components: {
    ChatComponent
  }
};
</script>

<style>
@import './assets/style.css'; /* Импорт стилей */


</style>
