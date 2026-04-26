<template>
  <div class="search-page">
    <div class="search-header">
      <h1>Поиск программного обеспечения</h1>
      <div class="search-bar">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Введите название или описание..."
          @keyup.enter="performSearch"
        >
        <button @click="performSearch">Поиск</button>
      </div>
    </div>

    <div class="search-content">
      <aside class="filters">
        <h3>Фильтры</h3>
        
        <div class="filter-group">
          <label>Категория</label>
          <select v-model="filters.category">
            <option value="">Все категории</option>
            <option v-for="cat in productsStore.categories" :key="cat" :value="cat">
              {{ cat }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Цена</label>
          <div class="price-range">
            <input 
              type="number" 
              v-model="filters.minPrice" 
              placeholder="От"
              min="0"
            >
            <span>—</span>
            <input 
              type="number" 
              v-model="filters.maxPrice" 
              placeholder="До"
              min="0"
            >
          </div>
        </div>

        <div class="filter-group">
          <label>Сортировка</label>
          <select v-model="sortBy">
            <option value="default">По умолчанию</option>
            <option value="price_asc">Цена (по возрастанию)</option>
            <option value="price_desc">Цена (по убыванию)</option>
            <option value="downloads">По популярности</option>
            <option value="name">По названию</option>
          </select>
        </div>

        <button class="apply-filters" @click="applyFilters">Применить</button>
        <button class="reset-filters" @click="resetFilters">Сбросить</button>
      </aside>

      <main class="results">
        <div class="results-header">
          <div class="results-info">
            Найдено: <strong>{{ productsStore.searchResults.length }}</strong> продуктов
          </div>
          
          <ViewToggle v-model="viewMode" />
        </div>

        <div v-if="productsStore.loading" class="loading">
          <div class="spinner"></div>
          <p>Загрузка...</p>
        </div>
        
        <div v-else-if="productsStore.searchResults.length === 0" class="no-results">
          <p>Ничего не найдено</p>
          <button class="clear-filters" @click="resetFilters">Сбросить фильтры</button>
        </div>
        
        <div v-else class="products-grid" :class="viewMode">
          <ProductCard 
            v-for="product in sortedProducts" 
            :key="product.id" 
            :product="product"
            :view="viewMode"
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useProductsStore } from '../stores/products';
import { useRoute } from 'vue-router';
import ProductCard from '../components/ProductCard.vue';
import ViewToggle from '../components/ViewToggle.vue';

const productsStore = useProductsStore();
const route = useRoute();

const searchQuery = ref('');
const viewMode = ref('grid-3'); // Изменено с grid-4 на grid-3
const sortBy = ref('default');
const filters = ref({
  category: '',
  minPrice: '',
  maxPrice: ''
});

// Сортировка продуктов
const sortedProducts = computed(() => {
  let products = [...productsStore.searchResults];
  
  switch (sortBy.value) {
    case 'price_asc':
      products.sort((a, b) => a.price - b.price);
      break;
    case 'price_desc':
      products.sort((a, b) => b.price - a.price);
      break;
    case 'downloads':
      products.sort((a, b) => (b.downloads_count || 0) - (a.downloads_count || 0));
      break;
    case 'name':
      products.sort((a, b) => a.name.localeCompare(b.name));
      break;
  }
  
  return products;
});

const performSearch = () => {
  const searchFilters = {};
  if (filters.value.category) searchFilters.category = filters.value.category;
  if (filters.value.minPrice) searchFilters.min_price = filters.value.minPrice * 100;
  if (filters.value.maxPrice) searchFilters.max_price = filters.value.maxPrice * 100;
  
  // Приводим поисковый запрос к нижнему регистру (но бэкенд уже делает ilike)
  const query = searchQuery.value;
  
  productsStore.searchProducts(query, searchFilters);
};

const applyFilters = () => {
  performSearch();
};

const resetFilters = () => {
  filters.value = {
    category: '',
    minPrice: '',
    maxPrice: ''
  };
  sortBy.value = 'default';
  performSearch();
};

onMounted(() => {
  productsStore.fetchCategories();
  
  // Если есть query параметр из URL
  if (route.query.q) {
    searchQuery.value = route.query.q;
    performSearch();
  }
  
  // Загружаем сохраненный вид
  const savedView = localStorage.getItem('preferred_view');
  if (savedView && ['grid-3', 'grid-2', 'list'].includes(savedView)) {
    viewMode.value = savedView;
  }
});

// Сохраняем вид в localStorage
watch(viewMode, (newMode) => {
  localStorage.setItem('preferred_view', newMode);
});
</script>

<style scoped>
.search-page {
  min-height: 100vh;
  background-color: #f8fafc;
}

.search-header {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
  padding: 3rem 2rem;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.search-header h1 {
  font-size: 2.2rem;
  margin-bottom: 2rem;
  font-weight: 600;
}

.search-bar {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  gap: 0.5rem;
}

.search-bar input {
  flex: 1;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.search-bar input:focus {
  outline: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.search-bar button {
  padding: 1rem 2.5rem;
  background-color: white;
  color: #2ecc71;
  border: none;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.search-bar button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.search-content {
  max-width: 1400px; /* Увеличено с 1200px */
  margin: 2rem auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: 280px 1fr; /* Увеличена ширина фильтров */
  gap: 2rem;
}

.filters {
  background-color: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  height: fit-content;
  border: 1px solid #eaeef2;
}

.filters h3 {
  margin-bottom: 1.5rem;
  color: #1a2634;
  font-size: 1.2rem;
  font-weight: 600;
}

.filter-group {
  margin-bottom: 1.5rem;
}

.filter-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #4a5568;
  font-weight: 500;
  font-size: 0.95rem;
}

.filter-group select,
.filter-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e0e7ed;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

.filter-group select:focus,
.filter-group input:focus {
  outline: none;
  border-color: #2ecc71;
  box-shadow: 0 0 0 3px rgba(46, 204, 113, 0.1);
}

.price-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.price-range input {
  width: calc(50% - 1rem);
}

.apply-filters {
  width: 100%;
  padding: 0.75rem;
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
  margin-bottom: 0.5rem;
}

.apply-filters:hover {
  background-color: #27ae60;
}

.reset-filters {
  width: 100%;
  padding: 0.75rem;
  background-color: #f1f5f9;
  color: #4a5568;
  border: 1px solid #e0e7ed;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.reset-filters:hover {
  background-color: #e2e8f0;
  border-color: #cbd5e0;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #eaeef2;
}

.results-info {
  color: #4a5568;
  font-size: 1rem;
}

.results-info strong {
  color: #2ecc71;
  font-size: 1.2rem;
  margin-left: 0.25rem;
}

.products-grid {
  display: grid;
  gap: 1.5rem;
  transition: all 0.3s;
}

/* Сетка для разных видов */
.products-grid.grid-3 {
  grid-template-columns: repeat(3, 1fr);
}

.products-grid.grid-2 {
  grid-template-columns: repeat(2, 1fr);
}

.products-grid.list {
  grid-template-columns: 1fr;
}

.loading {
  text-align: center;
  padding: 4rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #eaeef2;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 1rem;
  border: 3px solid #f1f5f9;
  border-top-color: #2ecc71;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-results {
  text-align: center;
  padding: 4rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #eaeef2;
}

.no-results p {
  color: #94a3b8;
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
}

.clear-filters {
  padding: 0.75rem 1.5rem;
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.clear-filters:hover {
  background-color: #27ae60;
}

/* Адаптивность */
@media (max-width: 1200px) {
  .products-grid.grid-3 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .search-content {
    grid-template-columns: 1fr;
  }
  
  .products-grid.grid-3,
  .products-grid.grid-2 {
    grid-template-columns: 1fr;
  }
}

[data-theme="dark"] .search-content,
[data-theme="dark"] .search-page,
[data-theme="dark"] .filters {
  background-color: var(--bg-secondary);
}

[data-theme="dark"] .results-header,
[data-theme="dark"] .filters {
  color: #fff;
}

[data-theme="dark"] .filters h3 {
  color: #4a5568;
}

[data-theme="dark"] .results-header {
  background-color: #1e293b;
}
</style>
