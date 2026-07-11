<template>
  <div class="checkout-page">
    <h1>Оформление заказа</h1>
    
    <div v-if="!authStore.isAuthenticated" class="auth-warning">
      <p>Для оформления заказа необходимо войти в систему</p>
      <router-link to="/login" class="btn">Войти</router-link>
    </div>
    
    <div v-else-if="cartStore.items.length === 0" class="empty-cart">
      <p>Корзина пуста</p>
      <router-link to="/" class="btn">Перейти к покупкам</router-link>
    </div>
    
    <div v-else class="checkout-content">
      <div class="checkout-form">
        <h2>Данные покупателя</h2>
        
        <div class="form-group">
          <label>Имя получателя</label>
          <input 
            type="text" 
            v-model="customerInfo.fullName"
            required
          >
        </div>
        
        <div class="form-group">
          <label>Email</label>
          <input 
            type="email" 
            v-model="customerInfo.email"
            required
          >
        </div>
        
        <div class="form-group">
          <label>Телефон</label>
          <input 
            type="tel" 
            v-model="customerInfo.phone" 
            placeholder="+7 (999) 999-99-99"
            required
          >
        </div>
        
        <h2>Способ оплаты</h2>
        
        <div class="payment-methods">
          <label class="payment-method">
            <input type="radio" v-model="paymentMethod" value="card" checked>
            <span class="method-icon">💳</span>
            <span class="method-name">Банковская карта</span>
          </label>
          
          <label class="payment-method">
            <input type="radio" v-model="paymentMethod" value="yoomoney">
            <span class="method-icon">💰</span>
            <span class="method-name">ЮMoney</span>
          </label>
          
          <label class="payment-method">
            <input type="radio" v-model="paymentMethod" value="sbp">
            <span class="method-icon">📱</span>
            <span class="method-name">СБП</span>
          </label>
        </div>
        
        <div v-if="paymentMethod === 'card'" class="card-details">
          <div class="form-group">
            <label>Номер карты</label>
            <input 
              type="text" 
              v-model="cardInfo.number" 
              placeholder="1234 5678 9012 3456"
              maxlength="19"
            >
          </div>
          
          <div class="card-row">
            <div class="form-group">
              <label>ММ/ГГ</label>
              <input 
                type="text" 
                v-model="cardInfo.expiry" 
                placeholder="ММ/ГГ"
                maxlength="5"
              >
            </div>
            
            <div class="form-group">
              <label>CVV</label>
              <input 
                type="text" 
                v-model="cardInfo.cvv" 
                placeholder="123"
                maxlength="3"
              >
            </div>
          </div>
        </div>
        
        <div v-if="paymentMethod === 'yoomoney'" class="payment-info">
          <p>После подтверждения заказа вы будете перенаправлены на страницу оплаты ЮMoney</p>
        </div>
        
        <div v-if="paymentMethod === 'sbp'" class="payment-info">
          <p>Оплата через Систему Быстрых Платежей (СБП)</p>
          <p>QR-код будет сгенерирован после подтверждения заказа</p>
        </div>
      </div>
      
      <div class="order-summary">
        <h2>Ваш заказ</h2>
        
        <div class="order-items">
          <div v-for="item in cartStore.items" :key="item.id" class="order-item">
            <span class="item-name">{{ item.name }} x{{ item.quantity }}</span>
            <span class="item-price">{{ formatPrice(item.price * item.quantity) }}</span>
          </div>
        </div>
        
        <div class="summary-row">
          <span>Товаров:</span>
          <span>{{ cartStore.totalItems }} шт.</span>
        </div>
        
        <div class="summary-row total">
          <span>Итого:</span>
          <span>{{ cartStore.formattedTotalPrice }}</span>
        </div>
        
        <button 
          class="confirm-btn" 
          @click="confirmOrder"
          :disabled="isProcessing"
        >
          {{ isProcessing ? 'Обработка...' : 'Подтвердить заказ' }}
        </button>
        
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
        <p v-if="successMessage" class="success">{{ successMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useCartStore } from '../stores/cart';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import api from '../services/api';

const cartStore = useCartStore();
const authStore = useAuthStore();
const router = useRouter();

// Инициализируем данные пользователя при загрузке компонента
const customerInfo = reactive({
  fullName: '',
  email: '',
  phone: ''
});

// Заполняем данные пользователя после загрузки компонента
onMounted(() => {
  if (authStore.user) {
    customerInfo.fullName = authStore.user.full_name || '';
    customerInfo.email = authStore.user.email || '';
  }
});

const paymentMethod = ref('card');
const cardInfo = reactive({
  number: '',
  expiry: '',
  cvv: ''
});

const isProcessing = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(price / 100);
};

const confirmOrder = async () => {
  // Валидация
  if (!customerInfo.fullName || !customerInfo.email || !customerInfo.phone) {
    errorMessage.value = 'Пожалуйста, заполните все поля';
    return;
  }
  
  if (paymentMethod.value === 'card') {
    if (!cardInfo.number || !cardInfo.expiry || !cardInfo.cvv) {
      errorMessage.value = 'Пожалуйста, заполните данные карты';
      return;
    }
  }
  
  isProcessing.value = true;
  errorMessage.value = '';
  
  try {
    // Подготовка данных заказа
    const orderData = {
      items: cartStore.items.map(item => ({
        product_id: item.id,
        quantity: item.quantity,
        price_at_time: item.price
      })),
      payment_method: paymentMethod.value
    };
    
    // Отправка заказа на сервер
    const response = await api.post('/orders/', orderData);
    
    // Если есть интеграция с платежной системой
    if (paymentMethod.value === 'card' && response.data.id) {
      // Здесь можно добавить интеграцию с платежным шлюзом
      await api.post(`/orders/${response.data.id}/pay`, {
        payment_token: 'test_token'
      });
    }
    
    successMessage.value = 'Заказ успешно оформлен!';
    
    // Очищаем корзину
    cartStore.clearCart();
    
    // Перенаправление на страницу заказов через 2 секунды
    setTimeout(() => {
      router.push('/profile/orders');
    }, 2000);
    
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Ошибка при оформлении заказа';
  } finally {
    isProcessing.value = false;
  }
};
</script>

<style scoped>
.checkout-page {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 2rem;
}

h1 {
  margin-bottom: 2rem;
  color: var(--text-primary);
}

.auth-warning,
.empty-cart {
  text-align: center;
  padding: 4rem;
  background: var(--bg-card);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background-color: var(--primary-color);
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: var(--primary-hover);
}

.checkout-content {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 2rem;
}

.checkout-form {
  background: var(--bg-card);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.checkout-form h2 {
  margin: 1.5rem 0 1rem;
  color: var(--text-primary);
}

.checkout-form h2:first-child {
  margin-top: 0;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.payment-methods {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.payment-method {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.payment-method:hover {
  background-color: var(--bg-tertiary);
}

.payment-method input[type="radio"] {
  width: auto;
  margin-right: 0.5rem;
}

.method-icon {
  font-size: 1.5rem;
}

.method-name {
  font-weight: 500;
}

.card-details {
  margin-top: 1rem;
  padding: 1rem;
  background-color: var(--bg-tertiary);
  border-radius: 4px;
}

.card-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.payment-info {
  padding: 1rem;
  background-color: var(--success-bg);
  border-radius: 4px;
  color: var(--success-text);
}

.order-summary {
  background: var(--bg-card);
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  height: fit-content;
}

.order-summary h2 {
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.order-items {
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.order-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  color: var(--text-secondary);
}

.item-name {
  flex: 1;
}

.item-price {
  font-weight: 500;
  color: var(--text-primary);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  color: var(--text-secondary);
}

.summary-row.total {
  border-top: 2px solid var(--border-color);
  margin-top: 0.5rem;
  padding-top: 1rem;
  font-weight: bold;
  color: var(--text-primary);
  font-size: 1.2rem;
}

.confirm-btn {
  width: 100%;
  padding: 1rem;
  margin-top: 1rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.confirm-btn:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.confirm-btn:disabled {
  background-color: var(--border-color);
  cursor: not-allowed;
}

.error {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: var(--danger-bg);
  color: var(--danger-text);
  border-radius: 4px;
  text-align: center;
}

.success {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: var(--success-bg);
  color: var(--success-text);
  border-radius: 4px;
  text-align: center;
}
</style>