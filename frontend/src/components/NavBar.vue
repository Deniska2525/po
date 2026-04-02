<template>
  <nav class="navbar">
    <div class="nav-container">
      <router-link to="/" class="logo">Marketplace ПО</router-link>
      
      <div class="nav-links">
        <router-link to="/" class="nav-link">Главная</router-link>
        <router-link to="/search" class="nav-link">Поиск</router-link>
        <router-link to="/cart" class="nav-link cart-link">🛒 Корзина</router-link>
        
        <router-link v-if="isAdmin" to="/admin" class="nav-link admin-link">
          👑 Админ
        </router-link>
        
        <ThemeToggle />
        
        <template v-if="authStore.isAuthenticated">
          <router-link v-if="authStore.isDeveloper" to="/dashboard" class="nav-link">
            Кабинет
          </router-link>
          <UserMenu :user="authStore.user" @logout="logout" />
        </template>
        
        <template v-else>
          <router-link to="/login" class="nav-link">Вход</router-link>
          <router-link to="/register" class="nav-link register-btn">Регистрация</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import UserMenu from './UserMenu.vue'
import ThemeToggle from './ThemeToggle.vue'

const authStore = useAuthStore()
const router = useRouter()

const isAdmin = computed(() => {
  return authStore.user?.role === 'admin' || authStore.user?.role === 'superuser'
})

const logout = () => {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
@import '@/assets/styles/navbar.css';
</style>