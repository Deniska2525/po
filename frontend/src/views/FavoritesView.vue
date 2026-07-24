<template>
  <div class="favorites-page">
    <div class="favorites-header">
      <h1>❤️ Избранное <span v-if="favoritesStore.count" class="count-badge">{{ favoritesStore.count }}</span></h1>
      <p class="subtitle">Товары, которые вы сохранили, чтобы вернуться к ним позже</p>
    </div>

    <div v-if="favoritesStore.loading" class="loading">
      <div class="spinner"></div>
      <p>Загрузка избранного...</p>
    </div>

    <div v-else-if="favoritesStore.items.length === 0" class="empty-state">
      <div class="empty-icon">🤍</div>
      <p>Вы пока ничего не добавили в избранное</p>
      <router-link to="/search" class="browse-link">Перейти к каталогу</router-link>
    </div>

    <div v-else class="products-grid grid-3">
      <ProductCard
        v-for="product in favoritesStore.items"
        :key="product.id"
        :product="product"
        view="grid-3"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useFavoritesStore } from '../stores/favorites';
import ProductCard from '../components/ProductCard.vue';

const authStore = useAuthStore();
const favoritesStore = useFavoritesStore();
const router = useRouter();

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  favoritesStore.fetchFavorites();
});
</script>

<style scoped>
.favorites-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 60vh;
}

.favorites-header {
  margin-bottom: 2rem;
}

.favorites-header h1 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-primary);
  font-size: 1.8rem;
  font-weight: 700;
}

.count-badge {
  background: var(--primary-color);
  color: white;
  font-size: 0.9rem;
  font-weight: 700;
  min-width: 28px;
  height: 28px;
  padding: 0 0.5rem;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.subtitle {
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem;
  color: var(--text-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  margin-bottom: 1rem;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-secondary);
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.browse-link {
  display: inline-block;
  margin-top: 1.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border-radius: 8px;
  font-weight: 600;
  transition: background 0.2s;
}

.browse-link:hover {
  background: var(--primary-hover);
}

.products-grid {
  display: grid;
  gap: 1.5rem;
}

.products-grid.grid-3 {
  grid-template-columns: repeat(3, 1fr);
}

@media (max-width: 1200px) {
  .products-grid.grid-3 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .products-grid.grid-3 {
    grid-template-columns: 1fr;
  }
}
</style>
