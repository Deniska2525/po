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
.navbar {
  background: var(--navbar-bg);
  padding: 1rem 0;
  box-shadow: var(--navbar-shadow);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: all 0.3s;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--primary-color);
  transition: color 0.3s;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: var(--text-secondary);
  font-weight: 500;
  transition: color 0.2s;
}

.nav-link:hover {
  color: var(--primary-color);
}

.cart-link {
  color: var(--primary-color);
}

.admin-link {
  color: #f39c12;
}

.admin-link:hover {
  color: #e67e22;
}

.register-btn {
  background: var(--primary-color);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 8px;
}

.register-btn:hover {
  background: var(--primary-hover);
  color: white;
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
  }
}
</style>
