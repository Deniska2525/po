<template>
  <div class="admin-orders">
    <div class="page-header">
      <h2>Управление заказами</h2>
      <div class="header-actions">
        <select v-model="statusFilter" @change="onFilterChange" class="filter-select">
          <option value="">Все статусы</option>
          <option value="pending">Ожидает оплаты</option>
          <option value="paid">Оплачен</option>
          <option value="completed">Выполнен</option>
          <option value="cancelled">Отменён</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка заказов...</p>
    </div>

    <div v-else-if="orders.length === 0" class="empty-state">
      <p>Заказов пока нет{{ statusFilter ? ' с таким статусом' : '' }}</p>
    </div>

    <div v-else class="orders-table-container">
      <table class="orders-table">
        <thead>
          <tr>
            <th>№</th>
            <th>Покупатель</th>
            <th>Товары</th>
            <th>Сумма</th>
            <th>Дата</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td class="order-id">#{{ order.id }}</td>
            <td class="buyer-cell">
              <div class="buyer-name">{{ order.user?.full_name || order.user?.username || `Пользователь #${order.user_id}` }}</div>
              <div class="buyer-email">{{ order.user?.email || '' }}</div>
            </td>
            <td class="products-cell" :title="order.products.map(p => p.name).join(', ')">
              {{ order.products.length }} {{ pluralizeItems(order.products.length) }}
            </td>
            <td class="order-amount">{{ formatPrice(order.total_amount) }}</td>
            <td>{{ formatDate(order.created_at) }}</td>
            <td>
              <select
                :value="order.status"
                @change="onStatusChange(order, $event.target.value)"
                class="status-select"
                :class="getStatusClass(order.status)"
              >
                <option value="pending">Ожидает оплаты</option>
                <option value="paid">Оплачен</option>
                <option value="completed">Выполнен</option>
                <option value="cancelled">Отменён</option>
              </select>
            </td>
            <td class="actions">
              <button class="action-btn" @click="viewingOrder = order" title="Подробнее">
                👁️
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button :disabled="currentPage === 1" @click="currentPage--; loadOrders()">←</button>
        <span>Стр. {{ currentPage }}</span>
        <button :disabled="orders.length < pageSize" @click="currentPage++; loadOrders()">→</button>
      </div>
    </div>

    <!-- Модалка просмотра состава заказа -->
    <div v-if="viewingOrder" class="modal-overlay" @click.self="viewingOrder = null">
      <div class="modal-content">
        <h3>Заказ #{{ viewingOrder.id }}</h3>
        <div class="order-details-list">
          <div v-for="product in viewingOrder.products" :key="product.id" class="order-detail-item">
            <span class="detail-name">{{ product.name }}</span>
            <span class="detail-price">{{ formatPrice(product.price) }}</span>
          </div>
        </div>
        <div class="order-details-total">
          <span>Итого</span>
          <strong>{{ formatPrice(viewingOrder.total_amount) }}</strong>
        </div>
        <button class="btn btn-secondary close-btn" @click="viewingOrder = null">Закрыть</button>
      </div>
    </div>

    <!-- Подтверждение отмены заказа -->
    <ConfirmModal
      v-if="cancellingOrder"
      title="Отменить заказ?"
      :danger="true"
      confirm-text="Отменить заказ"
      cancel-text="Не отменять"
      @confirm="confirmCancelOrder"
      @cancel="cancellingOrder = null"
    >
      Заказ <strong>#{{ cancellingOrder.id }}</strong> будет помечен как отменённый.
    </ConfirmModal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import adminService from '../services/admin';
import ConfirmModal from '../components/ConfirmModal.vue';

const orders = ref([]);
const loading = ref(true);
const statusFilter = ref('');
const currentPage = ref(1);
const pageSize = 10;
const viewingOrder = ref(null);
const cancellingOrder = ref(null);
const pendingStatus = ref(null);

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(price / 100);
};

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
};

const pluralizeItems = (n) => {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return 'товар';
  if ([2, 3, 4].includes(mod10) && ![12, 13, 14].includes(mod100)) return 'товара';
  return 'товаров';
};

const getStatusClass = (status) => `status-${status}`;

const loadOrders = async () => {
  loading.value = true;
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
      status: statusFilter.value || undefined
    };
    orders.value = await adminService.getOrders(params);
  } catch (error) {
    console.error('Error loading orders:', error);
  } finally {
    loading.value = false;
  }
};

const onFilterChange = () => {
  currentPage.value = 1;
  loadOrders();
};

const onStatusChange = (order, newStatus) => {
  if (newStatus === 'cancelled') {
    pendingStatus.value = newStatus;
    cancellingOrder.value = order;
    return;
  }
  applyStatusChange(order, newStatus);
};

const applyStatusChange = async (order, newStatus) => {
  const previousStatus = order.status;
  order.status = newStatus;
  try {
    await adminService.updateOrderStatus(order.id, newStatus);
  } catch (error) {
    console.error('Error updating order status:', error);
    order.status = previousStatus;
  }
};

const confirmCancelOrder = async () => {
  const order = cancellingOrder.value;
  cancellingOrder.value = null;
  if (order) {
    await applyStatusChange(order, pendingStatus.value || 'cancelled');
  }
  pendingStatus.value = null;
};

onMounted(() => {
  loadOrders();
});
</script>

<style scoped>
.admin-orders {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-header h2 {
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 600;
}

.filter-select {
  padding: 0.75rem 2rem 0.75rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-primary);
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1rem;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  background: var(--bg-card);
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  color: var(--text-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 1rem;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.orders-table-container {
  background: var(--bg-card);
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.orders-table {
  width: 100%;
  border-collapse: collapse;
}

.orders-table th {
  background: var(--bg-tertiary);
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.9rem;
  border-bottom: 2px solid var(--border-color);
}

.orders-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.orders-table tr:hover {
  background: var(--bg-tertiary);
}

.order-id {
  font-weight: 600;
  color: var(--text-secondary);
}

.buyer-name {
  font-weight: 500;
}

.buyer-email {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.products-cell {
  color: var(--text-secondary);
  cursor: help;
}

.order-amount {
  font-weight: 600;
}

.status-select {
  padding: 0.4rem 1.5rem 0.4rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  font-size: 0.85rem;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.3rem center;
  background-size: 1rem;
}

.status-select.status-pending { background-color: var(--warning-bg); color: var(--warning-text); }
.status-select.status-paid { background-color: var(--info-bg); color: var(--info-text); }
.status-select.status-completed { background-color: var(--success-bg); color: var(--primary-color); }
.status-select.status-cancelled { background-color: var(--danger-bg); color: var(--danger-text); }

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
}

.action-btn:hover {
  background: var(--hover-bg);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid var(--border-color);
}

.pagination button {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination button:hover:not(:disabled) {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.pagination button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.order-details-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin: 1rem 0;
}

.order-detail-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: var(--bg-tertiary);
  border-radius: 8px;
}

.order-details-total {
  display: flex;
  justify-content: space-between;
  padding-top: 1rem;
  margin-top: 0.5rem;
  border-top: 1px solid var(--border-color);
  font-size: 1.1rem;
}

.close-btn {
  width: 100%;
  margin-top: 1.5rem;
}
</style>
