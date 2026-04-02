<template>
  <div class="profile-orders">
    <h2>Мои заказы</h2>
    
    <div v-if="orders.length === 0" class="no-orders">
      <p>У вас пока нет заказов</p>
      <router-link to="/" class="btn">Перейти к покупкам</router-link>
    </div>
    
    <div v-else class="orders-list">
      <div v-for="order in orders" :key="order.id" class="order-card">
        <div class="order-header">
          <span class="order-id">Заказ #{{ order.id }}</span>
          <span class="order-date">{{ formatDate(order.created_at) }}</span>
          <span class="order-status" :class="order.status">{{ order.status }}</span>
        </div>
        
        <div class="order-items">
          <div v-for="product in order.products" :key="product.id" class="order-item">
            <img :src="product.logo_url || 'https://via.placeholder.com/50'" alt="" class="item-image">
            <span class="item-name">{{ product.name }}</span>
            <span class="item-price">{{ formatPrice(product.price) }}</span>
          </div>
        </div>
        
        <div class="order-footer">
          <span class="order-total">Итого: {{ formatPrice(order.total_amount) }}</span>
          <button class="repeat-btn" @click="repeatOrder(order)">Повторить заказ</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useCartStore } from '../stores/cart';
import { useRouter } from 'vue-router';
import api from '../services/api';

const authStore = useAuthStore();
const cartStore = useCartStore();
const router = useRouter();

const orders = ref([]);

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(price / 100);
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
};

const loadOrders = async () => {
  try {
    const response = await api.get('/orders/');
    orders.value = response.data;
  } catch (error) {
    console.error('Error loading orders:', error);
  }
};

const repeatOrder = (order) => {
  // Добавляем все товары из заказа в корзину
  order.products.forEach(product => {
    cartStore.addToCart(product, 1);
  });
  
  router.push('/cart');
};

onMounted(() => {
  loadOrders();
});
</script>

<style scoped>
.profile-orders {
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 2rem;
  color: #333;
}

.no-orders {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background-color: #2ecc71;
  color: white;
  text-decoration: none;
  border-radius: 4px;
}

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.order-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.order-header {
  padding: 1rem;
  background-color: #f9f9f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
}

.order-id {
  font-weight: bold;
  color: #333;
}

.order-date {
  color: #666;
  font-size: 0.9rem;
}

.order-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  text-transform: capitalize;
}

.order-status.completed {
  background-color: #d4edda;
  color: #155724;
}

.order-status.pending {
  background-color: #fff3cd;
  color: #856404;
}

.order-items {
  padding: 1rem;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.order-item:last-child {
  border-bottom: none;
}

.item-image {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
}

.item-name {
  flex: 1;
  color: #333;
}

.item-price {
  font-weight: 500;
  color: #2ecc71;
}

.order-footer {
  padding: 1rem;
  background-color: #f9f9f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #eee;
}

.order-total {
  font-weight: bold;
  color: #333;
}

.repeat-btn {
  padding: 0.5rem 1rem;
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.repeat-btn:hover {
  background-color: #27ae60;
}
</style>