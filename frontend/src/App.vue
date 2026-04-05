<template>
  <div id="app">
    <NavBar />
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import NavBar from './components/NavBar.vue'
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
main {
  flex: 1;
}
</style>