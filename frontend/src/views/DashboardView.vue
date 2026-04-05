<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Личный кабинет разработчика</h1>
      <button class="add-btn" @click="showProductForm = true">
        + Добавить ПО
      </button>
    </div>

    <div class="products-list">
      <h2>Мои продукты</h2>
      
      <div v-if="productsStore.loading" class="loading">
        Загрузка...
      </div>
      
      <div v-else-if="productsStore.myProducts.length === 0" class="no-products">
        <p>У вас пока нет добавленных продуктов</p>
        <button class="add-first-btn" @click="showProductForm = true">
          Добавить первый продукт
        </button>
      </div>
      
      <div v-else class="products-grid">
        <div v-for="product in productsStore.myProducts" :key="product.id" class="product-item">
          <div class="product-info">
            <h3>{{ product.name }}</h3>
            <p class="product-category">{{ product.category }}</p>
            <p class="product-price">{{ formatPrice(product.price) }}</p>
          </div>
          <div class="product-actions">
            <button class="edit-btn" @click="editProduct(product)">✏️</button>
            <button class="delete-btn" @click="deleteProduct(product.id)">🗑️</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно для добавления/редактирования продукта -->
    <div v-if="showProductForm" class="modal">
      <div class="modal-content">
        <h2>{{ editingProduct ? 'Редактировать' : 'Добавить' }} продукт</h2>
        
        <form @submit.prevent="saveProduct">
          <div class="form-group">
            <label>Название *</label>
            <input v-model="productForm.name" required>
          </div>
          
          <div class="form-group">
            <label>Описание *</label>
            <textarea v-model="productForm.description" required rows="4"></textarea>
          </div>
          
          <div class="form-group">
            <label>Категория *</label>
            <input v-model="productForm.category" required>
          </div>
          
          <div class="form-group">
            <label>Цена (в рублях) *</label>
            <input 
              type="number" 
              v-model="productForm.priceRub" 
              required 
              min="0"
            >
          </div>
          
          <div class="form-group">
            <label>URL для скачивания *</label>
            <input v-model="productForm.download_url" required>
          </div>
          
          <div class="form-group">
            <label>URL логотипа</label>
            <input v-model="productForm.logo_url">
          </div>
          
          <div v-if="formError" class="error-message">
            {{ formError }}
          </div>
          
          <div class="modal-actions">
            <button type="submit" :disabled="formLoading">
              {{ formLoading ? 'Сохранение...' : 'Сохранить' }}
            </button>
            <button type="button" class="cancel-btn" @click="closeForm">
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
import { useAuthStore } from '../stores/auth';
import { useProductsStore } from '../stores/products';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const productsStore = useProductsStore();
const router = useRouter();

const showProductForm = ref(false);
const editingProduct = ref(null);
const productForm = ref({
  name: '',
  description: '',
  category: '',
  priceRub: 0,
  download_url: '',
  logo_url: ''
});
const formError = ref('');
const formLoading = ref(false);

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(price / 100);
};

const resetForm = () => {
  productForm.value = {
    name: '',
    description: '',
    category: '',
    priceRub: 0,
    download_url: '',
    logo_url: ''
  };
  editingProduct.value = null;
  formError.value = '';
};

const closeForm = () => {
  showProductForm.value = false;
  resetForm();
};

const editProduct = (product) => {
  editingProduct.value = product;
  productForm.value = {
    name: product.name,
    description: product.description,
    category: product.category,
    priceRub: product.price / 100,
    download_url: product.download_url,
    logo_url: product.logo_url || ''
  };
  showProductForm.value = true;
};

const saveProduct = async () => {
  formLoading.value = true;
  formError.value = '';
  
  const productData = {
    name: productForm.value.name,
    description: productForm.value.description,
    category: productForm.value.category,
    price: productForm.value.priceRub * 100,
    download_url: productForm.value.download_url,
    logo_url: productForm.value.logo_url || null
  };
  
  let result;
  if (editingProduct.value) {
    result = await productsStore.updateProduct(editingProduct.value.id, productData);
  } else {
    result = await productsStore.createProduct(productData);
  }
  
  if (result.success) {
    closeForm();
    await productsStore.fetchMyProducts();
  } else {
    formError.value = result.message;
  }
  
  formLoading.value = false;
};

const deleteProduct = async (productId) => {
  if (confirm('Вы уверены, что хотите удалить этот продукт?')) {
    const result = await productsStore.deleteProduct(productId);
    if (result.success) {
      await productsStore.fetchMyProducts();
    } else {
      alert(result.message);
    }
  }
};

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  
  if (!authStore.isDeveloper && !authStore.isSuperuser) {
    router.push('/');
    return;
  }
  
  productsStore.fetchMyProducts();
});
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #f9f9f9;
  padding: 2rem;
}

.dashboard-header {
  max-width: 1200px;
  margin: 0 auto 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dashboard-header h1 {
  color: #333;
}

.add-btn {
  padding: 0.75rem 1.5rem;
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.add-btn:hover {
  background-color: #27ae60;
}

.products-list {
  max-width: 1200px;
  margin: 0 auto;
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.products-list h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

.products-grid {
  display: grid;
  gap: 1rem;
}

.product-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.product-item:hover {
  background-color: #f9f9f9;
}

.product-info h3 {
  margin-bottom: 0.25rem;
  color: #333;
}

.product-category {
  color: #2ecc71;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.product-price {
  font-weight: bold;
  color: #333;
}

.product-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-btn,
.delete-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
}

.edit-btn {
  background-color: #f39c12;
  color: white;
}

.edit-btn:hover {
  background-color: #e67e22;
}

.delete-btn {
  background-color: #e74c3c;
  color: white;
}

.delete-btn:hover {
  background-color: #c0392b;
}

.loading,
.no-products {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.add-first-btn {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* Модальное окно */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2ecc71;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.modal-actions button {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.modal-actions button[type="submit"] {
  background-color: #2ecc71;
  color: white;
}

.modal-actions button[type="submit"]:hover {
  background-color: #27ae60;
}

.cancel-btn {
  background-color: #e0e0e0;
  color: #666;
}

.cancel-btn:hover {
  background-color: #d0d0d0;
}

.error-message {
  background-color: #fee;
  color: #e74c3c;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}
</style>