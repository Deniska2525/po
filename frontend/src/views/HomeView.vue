<template>
  <div class="home">
    <section class="hero" :class="{ 'hero--compact': hasSearched }">
      <h1>Какое ПО вам нужно?</h1>
      <p>Опишите своими словами задачу — ИИ подберёт подходящие варианты из каталога</p>
      <div class="hero-search">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Например: нужна интеграция 1С с телеграмом, желательно недорого"
          @keyup.enter="handleSearch"
          :disabled="loading"
        >
        <button @click="handleSearch" :disabled="loading || !searchQuery.trim()">
          {{ loading ? 'Ищу…' : 'Найти' }}
        </button>
      </div>
    </section>

    <section v-if="loading" class="ai-status">
      <div class="spinner"></div>
      <p>ИИ анализирует каталог и подбирает варианты под ваш запрос…</p>
    </section>

    <section v-else-if="errorMessage" class="ai-status ai-status--error">
      <p>{{ errorMessage }}</p>
    </section>

    <section v-else-if="hasSearched" class="results">
      <div class="ai-message" v-if="aiMessage">
        <span class="ai-message-icon">✨</span>
        <p>{{ aiMessage }}</p>
      </div>

      <div v-if="productsStore.searchResults.length" class="products-grid grid-3">
        <ProductCard
          v-for="product in productsStore.searchResults"
          :key="product.id"
          :product="product"
          view="grid-3"
        />
      </div>
      <div v-else class="empty-results">
        <p>По вашему запросу ничего не нашлось. Попробуйте переформулировать — например, укажите категорию задачи или уберите лишние детали.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useProductsStore } from '../stores/products';
import ProductCard from '../components/ProductCard.vue';

const productsStore = useProductsStore();
const searchQuery = ref('');
const hasSearched = ref(false);
const errorMessage = ref('');

const loading = computed(() => productsStore.loading);
const aiMessage = computed(() => productsStore.aiSearchMessage);

const handleSearch = async () => {
  const query = searchQuery.value.trim();
  if (!query || loading.value) return;

  errorMessage.value = '';
  const result = await productsStore.aiSearch(query);
  hasSearched.value = true;
  if (!result.success) {
    errorMessage.value = result.message;
  }
};
</script>

<style scoped>
@import '@/assets/styles/home.css';
</style>
