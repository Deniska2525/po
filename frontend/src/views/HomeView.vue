<template>
  <div class="home">
    <section class="hero" :class="{ 'hero--compact': hasSearched }">
      <h1>Какое ПО вам нужно?</h1>
      <p>Опишите своими словами задачу или чего вам не хватает — ИИ разберётся, что внедрить, и подберёт подходящие варианты из каталога</p>
      <div class="hero-search">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Чем вам помочь?"
          @keyup.enter="handleSearch"
          :disabled="loading"
        >
        <button @click="handleSearch" :disabled="loading || !searchQuery.trim()">
          {{ loading ? 'Ищу…' : 'Найти' }}
        </button>
      </div>
      <button v-if="hasSearched && !loading" class="new-search-btn" @click="resetSearch">
        ✕ Новый поиск
      </button>
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

      <div class="ai-advice" v-if="aiAdvice.length">
        <h3>💡 Что стоит внедрить и как</h3>
        <ol>
          <li v-for="(step, i) in aiAdvice" :key="i">{{ step }}</li>
        </ol>
      </div>

      <div v-if="recommendations.length" class="products-grid grid-3">
        <ProductCard
          v-for="item in recommendations"
          :key="item.product.id"
          :product="item.product"
          :reason="item.reason"
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
const aiAdvice = computed(() => productsStore.aiAdvice);
const recommendations = computed(() => productsStore.aiRecommendations);

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

const resetSearch = () => {
  searchQuery.value = '';
  hasSearched.value = false;
  errorMessage.value = '';
  productsStore.aiRecommendations = [];
  productsStore.aiAdvice = [];
  productsStore.aiSearchMessage = '';
};
</script>

<style scoped>
@import '@/assets/styles/home.css';
</style>
