<template>
  <div class="product-card" :class="`${view}-view`">
    <div class="card-header">
      <h3 class="product-title">{{ product.name }}</h3>
      <span class="category-badge">{{ product.category }}</span>
    </div>
    
    <div class="card-content">
      <p class="product-description">{{ truncatedDescription }}</p>
      
      <div class="product-tags">
        <span class="component-badge">🧩 Компонент</span>
        <span v-if="product.category.includes('Интеграция')" class="integration-badge">🔌 Готов к интеграции</span>
      </div>
      
      <div class="product-meta">
        <div class="meta-row">
          <span class="developer">👨‍💻 {{ developerName }}</span>
          <span class="downloads">📥 {{ product.downloads_count || 0 }}</span>
        </div>
        <div class="meta-row">
          <span class="version">📦 v{{ product.version || '1.0' }}</span>
          <span class="file-size">💾 {{ formatFileSize(product.file_size) }}</span>
        </div>
      </div>
      
      <div class="product-footer">
        <div class="price-block">
          <span class="price-label">Цена компонента:</span>
          <span class="product-price">{{ formatPrice(product.price) }}</span>
        </div>
        <div class="action-buttons">
          <button class="cart-btn" @click="addToCart">🧩 Добавить в сборку</button>
          <button class="download-btn" @click="handleDownload">📦 Скачать</button>
        </div>
      </div>
      
      <div class="build-note">
        <span>🔧</span>
        <span>Можно комбинировать с другими компонентами</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCartStore } from '../stores/cart'

const props = defineProps({
  product: {
    type: Object,
    required: true
  },
  view: {
    type: String,
    default: 'grid-3'
  }
})

const cartStore = useCartStore()

const developerName = computed(() => {
  return props.product.developer?.full_name || 
         props.product.developer?.username || 
         'Разработчик'
})

const truncatedDescription = computed(() => {
  const maxLen = props.view === 'list' ? 250 : (props.view === 'grid-2' ? 150 : 120)
  const desc = props.product.description
  return desc.length > maxLen ? desc.slice(0, maxLen) + '...' : desc
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(price / 100)
}

const formatFileSize = (mb) => {
  if (!mb) return '—'
  if (mb < 1) return `${Math.round(mb * 1024)} КБ`
  if (mb < 1000) return `${mb} МБ`
  return `${(mb / 1024).toFixed(1)} ГБ`
}

const handleDownload = () => {
  window.open(props.product.download_url, '_blank')
}

const addToCart = () => {
  cartStore.addToCart(props.product, 1)
}
</script>

<style scoped>
/* Базовые стили карточки */
.product-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
  border: 1px solid #eaeef2;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(46, 204, 113, 0.12);
  border-color: #2ecc71;
}

/* Режимы отображения */
.product-card.grid-3-view {
  padding: 1.25rem;
}

.product-card.grid-2-view {
  padding: 1.5rem;
}

.product-card.list-view {
  padding: 1.5rem;
  flex-direction: row;
  gap: 2rem;
}

/* Шапка карточки */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.product-title {
  margin: 0;
  color: #1a2634;
  font-weight: 600;
  font-size: 1.1rem;
  flex: 1;
}

.category-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #e8f5e9;
  color: #2ecc71;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

/* Описание */
.product-description {
  color: #4a5568;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0.75rem 0;
}

/* Теги */
.product-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0.5rem 0;
}

.component-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  background: #e3f2fd;
  color: #2196f3;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
}

.integration-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  background: #fff3e0;
  color: #f39c12;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
}

/* Мета информация */
.product-meta {
  background: #f8fafc;
  padding: 0.75rem;
  border-radius: 12px;
  margin: 0.75rem 0;
}

.meta-row {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #4a5568;
}

.meta-row:first-child {
  margin-bottom: 0.5rem;
}

.meta-row span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* Футер карточки */
.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0.75rem 0;
  flex-wrap: wrap;
  gap: 1rem;
}

.price-block {
  display: flex;
  flex-direction: column;
}

.price-label {
  font-size: 0.75rem;
  color: #94a3b8;
}

.product-price {
  font-size: 1.4rem;
  font-weight: 700;
  color: #2ecc71;
  line-height: 1;
}

/* Кнопки */
.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.cart-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #2ecc71;
  color: #2ecc71;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
}

.cart-btn:hover {
  background: #2ecc71;
  color: white;
}

.download-btn {
  padding: 0.5rem 1rem;
  background: #2ecc71;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
}

.download-btn:hover {
  background: #27ae60;
}

/* Примечание о сборке */
.build-note {
  margin-top: 0.75rem;
  padding: 0.5rem;
  background: #fef9e6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.7rem;
  color: #b8860b;
}

/* Адаптивность */
@media (max-width: 768px) {
  .product-card.list-view {
    flex-direction: column;
    gap: 1rem;
  }
  
  .product-footer {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-buttons {
    width: 100%;
  }
  
  .cart-btn,
  .download-btn {
    flex: 1;
    text-align: center;
  }
}
</style>
