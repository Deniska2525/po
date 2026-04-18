<template>
  <div class="product-card" :class="`${view}-view`">
    <div class="card-header">
      <h3 class="product-title">{{ product.name }}</h3>
      <span class="category-badge">{{ product.category }}</span>
    </div>
    
    <div class="card-content">
      <p class="product-description">{{ truncatedDescription }}</p>
            
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
  @import '@/assets/styles/product-card.css';
</style>
