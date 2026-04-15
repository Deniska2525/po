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

    <div v-else class="products-table-container">
      <table class="products-table">
        <thead>
          <tr>
            <th style="width: 5%">ID</th>
            <th style="width: 25%">Название</th>
            <th style="width: 30%">Описание</th>
            <th style="width: 10%">Категория</th>
            <th style="width: 10%">Цена</th>
            <th style="width: 10%">Статус</th>
            <th style="width: 10%">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id">
            <td class="product-id">#{{ product.id }}</td>
            <td class="product-name">
              <div class="product-title">{{ product.name }}</div>
              <div class="product-meta-info">
                <span>📥 {{ product.downloads_count || 0 }}</span>
                <span>⚙️ v{{ product.version || '1.0' }}</span>
                <span>💾 {{ formatFileSize(product.file_size) }}</span>
              </div>
            </td>
            <td class="product-description">
              {{ truncateDescription(product.description) }}
            </td>
            <td>
              <span class="category-badge">{{ product.category }}</span>
            </td>
            <td class="product-price">{{ formatPrice(product.price) }}</td>
            <td>
              <div class="status-control">
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
            </td>
            <td class="actions">
              <button class="edit-btn" @click="editProduct(product)" title="Редактировать">
                ✏️
              </button>
              <button class="delete-btn" @click="confirmDeleteProduct(product)" title="Удалить">
                🗑️
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Модальное окно создания/редактирования -->
    <div v-if="showProductModal" class="modal">
      <div class="modal-content">
        <h3>{{ editingProduct ? 'Редактировать' : 'Создать' }} продукт</h3>
        
        <form @submit.prevent="saveProduct">
          <div class="form-group">
            <label>Название *</label>
            <input v-model="productForm.name" required>
          </div>
          
          <div class="form-group">
            <label>Категория *</label>
            <select v-model="productForm.category" required>
              <option value="">Выберите категорию</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.name">
                {{ cat.icon }} {{ cat.name }}
              </option>
            </select>
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
              <input type="number" v-model="productForm.file_size" min="0" step="0.1">
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
import { ref, onMounted } from 'vue'
import adminService from '../services/admin'
import debounce from 'lodash/debounce'

const products = ref([])
const categories = ref([])
const loading = ref(true)
const saving = ref(false)
const searchQuery = ref('')
const showProductModal = ref(false)
const editingProduct = ref(null)

const productForm = ref({
  name: '',
  description: '',
  category: '',
  priceRub: 0,
  file_size: null,
  version: '',
  download_url: '',
  is_active: true
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

const truncateDescription = (desc) => {
  if (!desc) return ''
  return desc.length > 100 ? desc.slice(0, 100) + '...' : desc
}

const loadProducts = async () => {
  loading.value = true
  try {
    const params = {
      limit: 100,
      search: searchQuery.value || undefined,
      include_inactive: true
    }
    products.value = await adminService.getProducts(params)
  } catch (error) {
    console.error('Error loading products:', error)
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    categories.value = await adminService.getCategories()
  } catch (error) {
    console.error('Error loading categories:', error)
  }
}

const debouncedSearch = debounce(() => {
  loadProducts()
}, 300)

const toggleProductStatus = async (product) => {
  try {
    const result = await adminService.toggleProductStatus(product.id)
    product.is_active = result.is_active
  } catch (error) {
    console.error('Error toggling product status:', error)
  }
}

const openCreateModal = () => {
  editingProduct.value = null
  productForm.value = {
    name: '',
    description: '',
    category: '',
    priceRub: 0,
    file_size: null,
    version: '',
    download_url: '',
    is_active: true
  }
  showProductModal.value = true
}

const editProduct = (product) => {
  editingProduct.value = product
  productForm.value = {
    name: product.name,
    description: product.description,
    category: product.category,
    priceRub: product.price / 100,
    file_size: product.file_size,
    version: product.version || '',
    download_url: product.download_url,
    is_active: product.is_active
  }
  showProductModal.value = true
}

const saveProduct = async () => {
  saving.value = true
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
    }
    
    if (editingProduct.value) {
      await adminService.updateProduct(editingProduct.value.id, productData)
    } else {
      await adminService.createProduct(productData)
    }
    
    closeModal()
    await loadProducts()
  } catch (error) {
    console.error('Error saving product:', error)
  } finally {
    saving.value = false
  }
}

const confirmDeleteProduct = (product) => {
  if (confirm(`Вы уверены, что хотите удалить продукт "${product.name}"?`)) {
    deleteProduct(product.id)
  }
}

const deleteProduct = async (productId) => {
  try {
    await adminService.deleteProduct(productId)
    await loadProducts()
  } catch (error) {
    console.error('Error deleting product:', error)
  }
}

const closeModal = () => {
  showProductModal.value = false
  editingProduct.value = null
}

onMounted(() => {
  loadProducts()
  loadCategories()
})
</script>

<style scoped>
.admin-products {
  max-width: 1400px;
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
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--input-bg);
  color: var(--text-primary);
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
}

.products-table-container {
  background: var(--card-bg);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  overflow-x: auto;
}

.products-table {
  width: 100%;
  border-collapse: collapse;
}

.products-table th {
  text-align: left;
  padding: 1rem;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.85rem;
  border-bottom: 1px solid var(--border-color);
}

.products-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  vertical-align: middle;
}

.products-table tr:hover {
  background: var(--hover-bg);
}

.product-id {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.product-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.product-meta-info {
  display: flex;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.product-description {
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.4;
}

.category-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: var(--success-bg);
  color: var(--success-text);
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.product-price {
  font-weight: 700;
  color: #2ecc71;
  font-size: 1rem;
  white-space: nowrap;
}

.status-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 22px;
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
  transition: 0.3s;
  border-radius: 22px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #2ecc71;
}

input:checked + .slider:before {
  transform: translateX(22px);
}

.status-text {
  font-size: 0.8rem;
  font-weight: 500;
}

.status-text.active {
  color: #2ecc71;
}

.status-text.inactive {
  color: #e74c3c;
}

.actions {
  display: flex;
  gap: 0.5rem;
  white-space: nowrap;
}

.edit-btn, .delete-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.edit-btn {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.edit-btn:hover {
  background: var(--border-color);
  transform: scale(1.05);
}

.delete-btn {
  background: var(--danger-bg);
  color: var(--danger-text);
}

.delete-btn:hover {
  background: #fdd;
  transform: scale(1.05);
}

.loading-state {
  text-align: center;
  padding: 3rem;
  background: var(--card-bg);
  border-radius: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 1rem;
  border: 3px solid var(--border-color);
  border-top-color: #2ecc71;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Модальное окно */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--card-bg);
  padding: 2rem;
  border-radius: 16px;
  width: 90%;
  max-width: 550px;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid var(--border-color);
}

.modal-content h3 {
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-checkbox {
  margin: 1rem 0;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.modal-actions button {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.save-btn {
  background: #2ecc71;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #27ae60;
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cancel-btn {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

@media (max-width: 1024px) {
  .products-table th,
  .products-table td {
    padding: 0.75rem;
  }
  
  .product-description {
    max-width: 200px;
  }
}

@media (max-width: 768px) {
  .products-table-container {
    overflow-x: scroll;
  }
  
  .products-table {
    min-width: 800px;
  }
}
</style>
