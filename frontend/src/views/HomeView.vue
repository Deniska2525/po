<template>
  <div class="home">
    <section class="hero">
      <h1>Маркетплейс программного обеспечения</h1>
      <p>Найдите идеальное ПО для ваших задач</p>
      <div class="hero-search">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Поиск программ..."
          @keyup.enter="handleSearch"
        >
        <button @click="handleSearch">Найти</button>
      </div>
    </section>

    <section class="featured">
      <div class="section-header">
        <h2>Популярные программы</h2>
        <ViewToggle v-model="viewMode" />
      </div>
      
      <div v-if="productsStore.loading" class="loading">
        <div class="spinner"></div>
      </div>
      
      <div v-else class="products-grid" :class="viewMode">
        <ProductCard 
          v-for="product in productsStore.products" 
          :key="product.id" 
          :product="product"
          :view="viewMode"
        />
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useProductsStore } from '../stores/products';
import { useRouter } from 'vue-router';
import ProductCard from '../components/ProductCard.vue';
import ViewToggle from '../components/ViewToggle.vue';

const productsStore = useProductsStore();
const router = useRouter();
const searchQuery = ref('');
const viewMode = ref('grid-3'); // Изменено с grid-4 на grid-3

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/search', query: { q: searchQuery.value } });
  }
};

onMounted(() => {
  productsStore.fetchAllProducts();
  
  const savedView = localStorage.getItem('preferred_view');
  if (savedView && ['grid-3', 'grid-2', 'list'].includes(savedView)) {
    viewMode.value = savedView;
  }
});

watch(viewMode, (newMode) => {
  localStorage.setItem('preferred_view', newMode);
});
</script>

<style scoped>
@import '@/assets/styles/home.css';
</style>