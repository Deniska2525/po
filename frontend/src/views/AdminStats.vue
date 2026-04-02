<template>
  <div class="admin-stats">
    <div class="stats-header">
      <h2>Статистика</h2>
      <select v-model="period" @change="loadStats" class="period-select">
        <option value="day">За последние 30 дней</option>
        <option value="month">За последние 12 месяцев</option>
        <option value="year">За последние 3 года</option>
      </select>
    </div>
    
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка статистики...</p>
    </div>

    <div v-else>
      <div class="stats-grid" v-if="stats">
        <div class="stat-card" v-for="stat in mainStats" :key="stat.label">
          <div class="stat-icon">{{ stat.icon }}</div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>

      <div class="charts-section">
        <div class="chart-container">
          <h3>Популярные продукты</h3>
          <div v-if="stats?.popular_products?.length" class="popular-list">
            <div v-for="(product, index) in stats.popular_products.slice(0, 5)" :key="product.id" class="popular-item">
              <span class="rank">#{{ index + 1 }}</span>
              <span class="product-name">{{ product.name }}</span>
              <span class="product-count">{{ product.downloads_count || 0 }} скач.</span>
            </div>
          </div>
          <div v-else class="no-data">
            Нет данных о скачиваниях
          </div>
        </div>

        <div class="chart-container">
          <h3>Последние заказы</h3>
          <div v-if="stats?.recent_orders?.length" class="orders-list">
            <div v-for="order in stats.recent_orders" :key="order.id" class="order-item">
              <span class="order-id">Заказ #{{ order.id }}</span>
              <span class="order-amount">{{ formatPrice(order.total_amount) }}</span>
              <span class="order-status" :class="order.status">{{ order.status }}</span>
            </div>
          </div>
          <div v-else class="no-data">
            Нет заказов
          </div>
        </div>
      </div>

      <div class="revenue-chart" v-if="revenueStats">
        <h3>Выручка</h3>
        <div class="chart-placeholder">
          <!-- Здесь можно добавить график, например Chart.js -->
          <div class="bar-chart">
            <div v-for="(item, index) in revenueStats" :key="index" class="bar-item">
              <div class="bar" :style="{ height: getBarHeight(item.revenue) + 'px' }"></div>
              <span class="bar-label">{{ formatDate(item.date) }}</span>
              <span class="bar-value">{{ formatPrice(item.revenue) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import adminService from '../services/admin';

const stats = ref(null);
const revenueStats = ref([]);
const loading = ref(true);
const period = ref('month');

const mainStats = computed(() => {
  if (!stats.value) return [];
  
  return [
    { icon: '👥', label: 'Пользователей', value: stats.value.total_users || 0 },
    { icon: '📦', label: 'Продуктов', value: stats.value.total_products || 0 },
    { icon: '🛒', label: 'Заказов', value: stats.value.total_orders || 0 },
    { icon: '📥', label: 'Скачиваний', value: stats.value.total_downloads || 0 },
    { icon: '💰', label: 'Выручка', value: formatPrice(stats.value.total_revenue || 0) }
  ];
});

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(price / 100);
};

const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('ru-RU', { 
    day: 'numeric', 
    month: 'short' 
  });
};

const getBarHeight = (revenue) => {
  if (!revenueStats.value.length) return 20;
  const max = Math.max(...revenueStats.value.map(r => r.revenue));
  return max ? (revenue / max) * 150 : 20;
};

const loadStats = async () => {
  loading.value = true;
  try {
    stats.value = await adminService.getDashboardStats();
    revenueStats.value = await adminService.getRevenueStats(period.value);
  } catch (error) {
    console.error('Error loading stats:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadStats();
});
</script>

<style scoped>
.admin-stats {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.stats-header h2 {
  color: #1a2634;
  font-size: 1.5rem;
  font-weight: 600;
}

.period-select {
  padding: 0.5rem 2rem 0.5rem 1rem;
  border: 1px solid #e0e7ed;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1rem;
}

.period-select:focus {
  outline: none;
  border-color: #2ecc71;
}

.loading-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #eaeef2;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(46, 204, 113, 0.1);
  border-color: #2ecc71;
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2ecc71;
  line-height: 1.2;
}

.stat-label {
  color: #4a5568;
  font-size: 0.9rem;
}

.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart-container {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #eaeef2;
}

.chart-container h3 {
  margin-bottom: 1rem;
  color: #1a2634;
  font-size: 1.1rem;
}

.popular-list,
.orders-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.popular-item,
.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
  transition: background 0.2s;
}

.popular-item:hover,
.order-item:hover {
  background: #e8f5e9;
}

.rank {
  font-weight: 600;
  color: #94a3b8;
  min-width: 30px;
}

.product-name {
  flex: 1;
  color: #1a2634;
  font-weight: 500;
}

.product-count {
  color: #2ecc71;
  font-weight: 600;
}

.order-id {
  color: #4a5568;
  font-size: 0.9rem;
}

.order-amount {
  font-weight: 600;
  color: #1a2634;
}

.order-status {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  text-transform: capitalize;
}

.order-status.completed {
  background: #e8f5e9;
  color: #2ecc71;
}

.order-status.pending {
  background: #fff3e0;
  color: #f39c12;
}

.order-status.cancelled {
  background: #fee;
  color: #e74c3c;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #94a3b8;
  font-style: italic;
}

.revenue-chart {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #eaeef2;
}

.revenue-chart h3 {
  margin-bottom: 1.5rem;
  color: #1a2634;
}

.chart-placeholder {
  min-height: 200px;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  height: 200px;
  padding: 1rem 0;
}

.bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.bar {
  width: 100%;
  background: linear-gradient(to top, #2ecc71, #27ae60);
  border-radius: 4px 4px 0 0;
  min-height: 20px;
  transition: height 0.3s;
}

.bar-label {
  font-size: 0.8rem;
  color: #4a5568;
  transform: rotate(-45deg);
  white-space: nowrap;
}

.bar-value {
  font-size: 0.8rem;
  font-weight: 600;
  color: #2ecc71;
}
</style>