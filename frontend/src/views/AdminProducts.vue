<template>
  <div class="admin-products">
    <div class="page-header">
      <h2>Управление продуктами</h2>
      <div class="header-actions">
        <button class="add-btn" @click="openCreateModal">
          ➕ Добавить продукт
        </button>
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Поиск по названию..."
            @input="debouncedSearch"
          >
          <span class="search-icon">🔍</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка продуктов...</p>
    </div>

    <div v-else class="products-grid">
      <div v-for="product in products" :key="product.id" class="product-card">
        <div class="product-header">
          <h3>{{ product.name }}</h3>
          <span class="category-badge">{{ product.category }}</span>
        </div>
        
        <p class="product-description">{{ product.description }}</p>
        
        <div class="product-meta">
          <div class="meta-row">
            <span>👤 {{ product.developer?.full_name || product.developer?.username || 'Нет' }}</span>
            <span>📥 {{ product.downloads_count || 0 }}</span>
          </div>
          <div class="meta-row">
            <span>⚙️ v{{ product.version || '1.0' }}</span>
            <span>💾 {{ formatFileSize(product.file_size) }}</span>
          </div>
        </div>
        
        <div class="product-footer">
          <span class="price">{{ formatPrice(product.price) }}</span>
          <div class="status-toggle">
            <label class="switch">
              <input 
                type="checkbox" 
                :checked="product.is_active"
                @change="toggleProductStatus(product)"
              >
              <span class="slider"></span>
            </label>
            <span :class="['status-text', product.is_active ? 'active' : 'inactive']">
              {{ product.is_active ? 'Активен' : 'Неактивен' }}
            </span>
          </div>
        </div>
        
        <div class="product-actions">
          <button class="edit-btn" @click="editProduct(product)">
            ✏️ Редактировать
          </button>
          <button class="delete-btn" @click="confirmDeleteProduct(product)">
            🗑️ Удалить
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно создания/редактирования продукта -->
    <div v-if="showProductModal" class="modal">
      <div class="modal-content large">
        <h3>{{ editingProduct ? 'Редактировать' : 'Создать' }} продукт</h3>
        
        <form @submit.prevent="saveProduct">
          <div class="form-row">
            <div class="form-group">
              <label>Название *</label>
              <input v-model="productForm.name" required>
            </div>
            
            <div class="form-group">
              <label>Категория *</label>
              <select v-model="productForm.category" required>
                <option value="">Выберите категорию</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.name">
                  {{ cat.name }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>Описание *</label>
            <textarea v-model="productForm.description" rows="4" required></textarea>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Цена (руб) *</label>
              <input type="number" v-model="productForm.priceRub" min="0" required>
            </div>
            
            <div class="form-group">
              <label>Размер (МБ)</label>
              <input type="number" v-model="productForm.file_size" min="0">
            </div>
            
            <div class="form-group">
              <label>Версия</label>
              <input v-model="productForm.version" placeholder="1.0.0">
            </div>
          </div>
          
          <div class="form-group">
            <label>URL для скачивания *</label>
            <input v-model="productForm.download_url" type="url" required>
          </div>
          
          <div class="form-checkbox">
            <label>
              <input type="checkbox" v-model="productForm.is_active">
              Активен (показывать в магазине)
            </label>
          </div>
          
          <div class="modal-actions">
            <button type="submit" class="save-btn" :disabled="saving">
              {{ saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
            <button type="button" class="cancel-btn" @click="closeModal">
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import adminService from '../services/admin';
import debounce from 'lodash/debounce';

const products = ref([]);
const categories = ref([]);
const loading = ref(true);
const saving = ref(false);
const searchQuery = ref('');
const showProductModal = ref(false);
const editingProduct = ref(null);

const productForm = ref({
  name: '',
  description: '',
  category: '',
  priceRub: 0,
  file_size: null,
  version: '',
  download_url: '',
  is_active: true
});

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(price / 100);
};

const formatFileSize = (mb) => {
  if (!mb) return '—';
  if (mb < 1000) return `${mb} МБ`;
  return `${(mb / 1024).toFixed(1)} ГБ`;
};

const loadProducts = async () => {
  loading.value = true;
  try {
    const params = {
      search: searchQuery.value
    };
    products.value = await adminService.getProducts(params);
  } catch (error) {
    console.error('Error loading products:', error);
  } finally {
    loading.value = false;
  }
};

const loadCategories = async () => {
  try {
    categories.value = await adminService.getCategories();
  } catch (error) {
    console.error('Error loading categories:', error);
  }
};

const debouncedSearch = debounce(() => {
  loadProducts();
}, 300);

const toggleProductStatus = async (product) => {
  try {
    await adminService.toggleProductStatus(product.id);
    product.is_active = !product.is_active;
  } catch (error) {
    console.error('Error toggling product status:', error);
  }
};

const openCreateModal = () => {
  editingProduct.value = null;
  productForm.value = {
    name: '',
    description: '',
    category: '',
    priceRub: 0,
    file_size: null,
    version: '',
    download_url: '',
    is_active: true
  };
  showProductModal.value = true;
};

const editProduct = (product) => {
  editingProduct.value = product;
  productForm.value = {
    name: product.name,
    description: product.description,
    category: product.category,
    priceRub: product.price / 100,
    file_size: product.file_size,
    version: product.version || '',
    download_url: product.download_url,
    is_active: product.is_active
  };
  showProductModal.value = true;
};

const saveProduct = async () => {
  saving.value = true;
  try {
    const productData = {
      name: productForm.value.name,
      description: productForm.value.description,
      category: productForm.value.category,
      price: productForm.value.priceRub * 100,
      file_size: productForm.value.file_size || null,
      version: productForm.value.version || null,
      download_url: productForm.value.download_url,
      is_active: productForm.value.is_active
    };
    
    if (editingProduct.value) {
      await adminService.updateProduct(editingProduct.value.id, productData);
    } else {
      await adminService.createProduct(productData);
    }
    
    closeModal();
    await loadProducts();
  } catch (error) {
    console.error('Error saving product:', error);
  } finally {
    saving.value = false;
  }
};

const confirmDeleteProduct = (product) => {
  if (confirm(`Вы уверены, что хотите удалить продукт "${product.name}"?`)) {
    deleteProduct(product.id);
  }
};

const deleteProduct = async (productId) => {
  try {
    await adminService.deleteProduct(productId);
    await loadProducts();
  } catch (error) {
    console.error('Error deleting product:', error);
  }
};

const closeModal = () => {
  showProductModal.value = false;
  editingProduct.value = null;
};

onMounted(() => {
  loadProducts();
  loadCategories();
});
</script>

<style scoped>
.admin-products {
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
  color: #1a2634;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.add-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
}

.search-box {
  position: relative;
  min-width: 250px;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #e0e7ed;
  border-radius: 8px;
  font-size: 0.95rem;
}

.search-box input:focus {
  outline: none;
  border-color: #2ecc71;
  box-shadow: 0 0 0 3px rgba(46, 204, 113, 0.1);
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
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

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.product-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #eaeef2;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(46, 204, 113, 0.1);
  border-color: #2ecc71;
}

.product-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.product-header h3 {
  font-size: 1.2rem;
  color: #1a2634;
  font-weight: 600;
  margin: 0;
}

.category-badge {
  padding: 0.25rem 0.75rem;
  background: #e8f5e9;
  color: #2ecc71;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

.product-description {
  color: #4a5568;
  font-size: 0.95rem;
  line-height: 1.5;
  margin-bottom: 1rem;
  flex: 1;
}

.product-meta {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  color: #4a5568;
  font-size: 0.9rem;
}

.meta-row:first-child {
  margin-bottom: 0.5rem;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.price {
  font-size: 1.3rem;
  font-weight: 700;
  color: #2ecc71;
}

.status-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #e74c3c;
  transition: .3s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: .3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #2ecc71;
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.status-text {
  font-size: 0.85rem;
  font-weight: 500;
}

.status-text.active {
  color: #2ecc71;
}

.status-text.inactive {
  color: #e74c3c;
}

.product-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.edit-btn, .delete-btn {
  flex: 1;
  padding: 0.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-btn {
  background: #f1f5f9;
  color: #4a5568;
}

.edit-btn:hover {
  background: #e2e8f0;
}

.delete-btn {
  background: #fee;
  color: #e74c3c;
}

.delete-btn:hover {
  background: #fdd;
}

/* Модальное окно */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content.large {
  max-width: 700px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-checkbox {
  margin: 1rem 0;
}

.form-checkbox label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4a5568;
  cursor: pointer;
}
</style>