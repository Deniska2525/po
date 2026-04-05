<template>
  <div class="user-menu" ref="menuRef">
    <button class="user-trigger" @click="toggle">
      <span class="user-avatar">{{ initials }}</span>
      <span class="user-name">{{ displayName }}</span>
      <span class="arrow" :class="{ open: isOpen }">▼</span>
    </button>
    
    <div v-if="isOpen" class="dropdown">
      <div class="welcome">{{ authStore.welcomeMessage }}</div>
      <router-link to="/profile" class="dropdown-item" @click="close">📝 Редактировать</router-link>
      <button class="dropdown-item logout" @click="handleLogout">🚪 Выйти</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const isOpen = ref(false)
const menuRef = ref(null)

const initials = computed(() => {
  const name = authStore.user?.full_name || authStore.user?.username || 'U'
  return name.slice(0, 2).toUpperCase()
})

const displayName = computed(() => {
  return authStore.user?.full_name || authStore.user?.username
})

const toggle = () => { isOpen.value = !isOpen.value }
const close = () => { isOpen.value = false }

const handleLogout = () => {
  close()
  authStore.logout()
}

const handleClickOutside = (e) => {
  if (menuRef.value && !menuRef.value.contains(e.target)) {
    close()
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>

<style scoped>
@import '@/assets/styles/user-menu.css';
</style>