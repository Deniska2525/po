<template>
  <div class="admin-categories">
    <div class="page-header">
      <h2>Управление категориями</h2>
      <button class="add-btn" @click="openCreateModal">
        ➕ Добавить категорию
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка категорий...</p>
    </div>

    <div v-else class="categories-grid">
      <div v-for="category in categories" :key="category.id" class="category-card">
        <div class="category-icon">{{ category.icon || '📁' }}</div>
        <div class="category-info">
          <h3>{{ category.name }}</h3>
          <p>{{ category.description || 'Нет описания' }}</p>
          <span class="product-count">{{ category.product_count || 0 }} продуктов</span>
        </div>
        <button class="delete-category" @click="confirmDeleteCategory(category)" title="Удалить">
          🗑️
        </button>
      </div>
    </div>

    <!-- Модальное окно создания категории -->
    <div v-if="showCreateModal" class="modal">
      <div class="modal-content">
        <h3>Создать категорию</h3>
        
        <div class="form-group">
          <label>Название *</label>
          <input v-model="newCategory.name" required>
        </div>
        
        <div class="form-group">
          <label>Описание</label>
          <textarea v-model="newCategory.description" rows="3"></textarea>
        </div>
        
        <div class="form-group">
          <label>Иконка (эмодзи)</label>
          <input v-model="newCategory.icon" placeholder="📁">
        </div>
        
        <div class="modal-actions">
          <button class="save-btn" @click="createCategory" :disabled="saving">
            {{ saving ? 'Создание...' : 'Создать' }}
          </button>
          <button class="cancel-btn" @click="showCreateModal = false">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import adminService from '../services/admin';

const categories = ref([]);
const loading = ref(true);
const saving = ref(false);
const showCreateModal = ref(false);
const newCategory = ref({
  name: '',
  description: '',
  icon: '📁'
});

const loadCategories = async () => {
  loading.value = true;
  try {
    categories.value = await adminService.getCategories();
  } catch (error) {
    console.error('Error loading categories:', error);
  } finally {
    loading.value = false;
  }
};

const openCreateModal = () => {
  newCategory.value = {
    name: '',
    description: '',
    icon: '📁'
  };
  showCreateModal.value = true;
};

const createCategory = async () => {
  if (!newCategory.value.name) return;
  
  saving.value = true;
  try {
    await adminService.createCategory(newCategory.value);
    showCreateModal.value = false;
    await loadCategories();
  } catch (error) {
    console.error('Error creating category:', error);
  } finally {
    saving.value = false;
  }
};

const confirmDeleteCategory = (category) => {
  if (category.product_count > 0) {
    alert(`Нельзя удалить категорию "${category.name}", так как в ней есть продукты`);
    return;
  }
  
  if (confirm(`Удалить категорию "${category.name}"?`)) {
    deleteCategory(category.id);
  }
};

const deleteCategory = async (categoryId) => {
  try {
    await adminService.deleteCategory(categoryId);
    await loadCategories();
  } catch (error) {
    console.error('Error deleting category:', error);
  }
};

onMounted(() => {
  loadCategories();
});
</script>

<style scoped>
.admin-categories {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h2 {
  color: #1a2634;
  font-size: 1.5rem;
  font-weight: 600;
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

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.category-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #eaeef2;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s;
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(46, 204, 113, 0.1);
  border-color: #2ecc71;
}

.category-icon {
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

.category-info {
  flex: 1;
}

.category-info h3 {
  margin: 0 0 0.25rem 0;
  color: #1a2634;
  font-size: 1.1rem;
}

.category-info p {
  margin: 0 0 0.5rem 0;
  color: #4a5568;
  font-size: 0.9rem;
}

.product-count {
  font-size: 0.85rem;
  color: #94a3b8;
}

.delete-category {
  width: 36px;
  height: 36px;
  border: none;
  background: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  opacity: 0.5;
  transition: all 0.2s;
}

.delete-category:hover {
  opacity: 1;
  background: #fee;
}

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

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.modal-content h3 {
  margin-bottom: 1.5rem;
  color: #1a2634;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #4a5568;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e0e7ed;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2ecc71;
  box-shadow: 0 0 0 3px rgba(46, 204, 113, 0.1);
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
  transition: all 0.2s;
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
  background: #f1f5f9;
  color: #4a5568;
}

.cancel-btn:hover {
  background: #e2e8f0;
}
</style>