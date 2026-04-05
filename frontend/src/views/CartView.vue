<template>
  <div class="cart-page">
    <h1>Корзина</h1>
    
    <div v-if="cartStore.items.length === 0" class="empty-cart">
      <p>Корзина пуста</p>
      <router-link to="/" class="continue-shopping">Продолжить покупки</router-link>
    </div>
    
    <div v-else class="cart-content">
      <div class="cart-items">
        <div v-for="item in cartStore.items" :key="item.id" class="cart-item">
          <div class="item-icon">📦</div>
          
          <div class="item-info">
            <h3>{{ item.name }}</h3>
            <div class="item-price">{{ formatPrice(item.price) }}</div>
          </div>
          
          <div class="item-quantity">
            <button @click="updateQuantity(item.id, item.quantity - 1)" class="qty-btn">−</button>
            <span class="qty-value">{{ item.quantity }}</span>
            <button @click="updateQuantity(item.id, item.quantity + 1)" class="qty-btn">+</button>
          </div>
          
          <div class="item-total">
            {{ formatPrice(item.price * item.quantity) }}
          </div>
          
          <button @click="cartStore.removeFromCart(item.id)" class="remove-btn" title="Удалить">
            ✕
          </button>
        </div>
      </div>
      
      <div class="cart-summary">
        <h3>Итого</h3>
        
        <div class="summary-row">
          <span>Товаров:</span>
          <span>{{ cartStore.totalItems }} шт.</span>
        </div>
        
        <div class="summary-row total">
          <span>Сумма:</span>
          <span>{{ cartStore.formattedTotalPrice }}</span>
        </div>
        
        <button 
          class="checkout-btn" 
          @click="checkout"
          :disabled="!authStore.isAuthenticated"
        >
          {{ authStore.isAuthenticated ? 'Оформить заказ' : 'Войдите для оформления' }}
        </button>
        
        <p v-if="!authStore.isAuthenticated" class="login-prompt">
          <router-link to="/login">Войдите</router-link>, чтобы оформить заказ
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useCartStore } from '../stores/cart';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const cartStore = useCartStore();
const authStore = useAuthStore();
const router = useRouter();

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(price / 100);
};

const updateQuantity = (productId, quantity) => {
  cartStore.updateQuantity(productId, quantity);
};

const checkout = () => {
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  router.push('/checkout');
};
</script>

<style scoped>
.cart-page {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 2rem;
}

h1 {
  margin-bottom: 2rem;
  color: #1a2634;
}

.empty-cart {
  text-align: center;
  padding: 4rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.continue-shopping {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background-color: #2ecc71;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.cart-content {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.cart-items {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  overflow: hidden;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 1.25rem;
  border-bottom: 1px solid #eaeef2;
  gap: 1.5rem;
}

.cart-item:last-child {
  border-bottom: none;
}

.item-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: #2ecc71;
}

.item-info {
  flex: 1;
}

.item-info h3 {
  margin-bottom: 0.25rem;
  color: #1a2634;
  font-size: 1.1rem;
}

.item-price {
  color: #2ecc71;
  font-weight: 600;
  font-size: 1rem;
}

.item-quantity {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.qty-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #e0e7ed;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.2rem;
  color: #4a5568;
  transition: all 0.2s;
}

.qty-btn:hover {
  background: #f8fafc;
  border-color: #2ecc71;
  color: #2ecc71;
}

.qty-value {
  min-width: 30px;
  text-align: center;
  font-weight: 500;
}

.item-total {
  font-weight: 700;
  color: #1a2634;
  min-width: 120px;
  text-align: right;
  font-size: 1.1rem;
}

.remove-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #94a3b8;
  padding: 0.5rem;
  transition: color 0.2s;
}

.remove-btn:hover {
  color: #e74c3c;
}

.cart-summary {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  height: fit-content;
}

.cart-summary h3 {
  margin-bottom: 1.5rem;
  color: #1a2634;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  color: #4a5568;
  border-bottom: 1px solid #eaeef2;
}

.summary-row.total {
  border-bottom: none;
  margin-top: 0.5rem;
  padding-top: 1rem;
  font-weight: 700;
  color: #1a2634;
  font-size: 1.2rem;
}

.checkout-btn {
  width: 100%;
  padding: 1rem;
  margin-top: 1.5rem;
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.checkout-btn:hover:not(:disabled) {
  background-color: #27ae60;
}

.checkout-btn:disabled {
  background-color: #cbd5e0;
  cursor: not-allowed;
}

.login-prompt {
  text-align: center;
  margin-top: 1rem;
  color: #94a3b8;
  font-size: 0.9rem;
}

.login-prompt a {
  color: #2ecc71;
  text-decoration: none;
  font-weight: 500;
}
</style>