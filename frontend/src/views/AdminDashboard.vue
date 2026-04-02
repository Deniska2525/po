<template>
  <div class="admin-dashboard">
    <div class="admin-header">
      <h1>Панель администратора</h1>
      <div class="admin-nav">
        <router-link 
          v-for="item in navItems" 
          :key="item.path"
          :to="item.path" 
          class="nav-link" 
          :class="{ active: $route.path === item.path }"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-text">{{ item.name }}</span>
        </router-link>
      </div>
    </div>

    <div class="admin-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import { onMounted } from 'vue';

const authStore = useAuthStore();
const router = useRouter();

const navItems = [
  { path: '/admin', name: 'Дашборд', icon: '📊' },
  { path: '/admin/users', name: 'Пользователи', icon: '👥' },
  { path: '/admin/products', name: 'Продукты', icon: '📦' },
  { path: '/admin/categories', name: 'Категории', icon: '🏷️' },
  { path: '/admin/orders', name: 'Заказы', icon: '🛒' },
  { path: '/admin/stats', name: 'Статистика', icon: '📈' }
];

onMounted(() => {
  if (!authStore.isAuthenticated || !['admin', 'superuser'].includes(authStore.user?.role)) {
    router.push('/');
  }
});
</script>

<style scoped>
.admin-dashboard {
  max-width: 1400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: auto;
  min-height: 100vh;
  background-color: #f8fafc;
}

.admin-header {
  background: white;
  padding: 1.5rem 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border-bottom: 1px solid #eaeef2;
  position: sticky;
  top: 0;
  z-index: 100;
}

.admin-header h1 {
  color: #1a2634;
  margin-bottom: 1rem;
  font-size: 1.8rem;
  font-weight: 600;
}

.admin-nav {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  text-decoration: none;
  color: #4a5568;
  border-radius: 10px;
  transition: all 0.2s;
  font-weight: 500;
}

.nav-link:hover {
  background-color: #f1f5f9;
  color: #2ecc71;
}

.nav-link.active {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
  box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
}

.nav-icon {
  font-size: 1.2rem;
}

.nav-text {
  font-size: 0.95rem;
}

.admin-content {
  padding: 2rem;
}

@media (max-width: 768px) {
  .nav-text {
    display: none;
  }
  
  .nav-link {
    padding: 0.75rem;
  }
  
  .nav-icon {
    font-size: 1.4rem;
  }
}
</style>