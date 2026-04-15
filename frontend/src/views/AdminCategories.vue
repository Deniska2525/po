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

    <div v-else class="categories-table-container">
      <table class="categories-table">
        <thead>
          <tr>
            <th style="width: 10%">ID</th>
            <th style="width: 15%">Иконка</th>
            <th style="width: 25%">Название</th>
            <th style="width: 35%">Описание</th>
            <th style="width: 15%">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="category in categories" :key="category.id">
            <td class="category-id">#{{ category.id }}</td>
            <td class="category-icon">{{ category.icon || '📁' }}</td>
            <td class="category-name">{{ category.name }}</td>
            <td class="category-description">{{ category.description || '—' }}</td>
            <td class="actions">
              <button class="edit-btn" @click="editCategory(category)" title="Редактировать">
                ✏️
              </button>
              <button 
                class="delete-btn" 
                @click="confirmDeleteCategory(category)"
                title="Удалить"
                :disabled="category.product_count > 0"
              >
                🗑️
              </button>
            </td>
          </tr>
        </tbody>
       </table>
    </div>

    <!-- Модальное окно создания/редактирования -->
    <div v-if="showModal" class="modal">
      <div class="modal-content">
        <h3>{{ editingCategory ? 'Редактировать' : 'Создать' }} категорию</h3>
        
        <div class="form-group">
          <label>Название *</label>
          <input v-model="form.name" required>
        </div>
        
        <div class="form-group">
          <label>Описание</label>
          <textarea v-model="form.description" rows="3"></textarea>
        </div>
        
        <div class="form-group">
          <label>Иконка (эмодзи)</label>
          <input v-model="form.icon" placeholder="📁">
        </div>
        
        <div class="modal-actions">
          <button class="save-btn" @click="saveCategory" :disabled="saving">
            {{ saving ? 'Сохранение...' : 'Сохранить' }}
          </button>
          <button class="cancel-btn" @click="closeModal">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import adminService from '../services/admin'

const categories = ref([])
const loading = ref(true)
const saving = ref(false)
const showModal = ref(false)
const editingCategory = ref(null)

const form = ref({
  name: '',
  description: '',
  icon: '📁'
})

const loadCategories = async () => {
  loading.value = true
  try {
    categories.value = await adminService.getCategories()
  } catch (error) {
    console.error('Error loading categories:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingCategory.value = null
  form.value = {
    name: '',
    description: '',
    icon: '📁'
  }
  showModal.value = true
}

const editCategory = (category) => {
  editingCategory.value = category
  form.value = {
    name: category.name,
    description: category.description || '',
    icon: category.icon || '📁'
  }
  showModal.value = true
}

const saveCategory = async () => {
  if (!form.value.name.trim()) {
    alert('Введите название категории')
    return
  }
  
  saving.value = true
  try {
    if (editingCategory.value) {
      // Обновление категории
      await adminService.updateCategory(editingCategory.value.id, form.value)
    } else {
      // Создание новой
      await adminService.createCategory(form.value)
    }
    closeModal()
    await loadCategories()
  } catch (error) {
    console.error('Error saving category:', error)
    alert(error.response?.data?.detail || 'Ошибка при сохранении')
  } finally {
    saving.value = false
  }
}

const confirmDeleteCategory = (category) => {
  if (category.product_count > 0) {
    alert(`Нельзя удалить категорию "${category.name}", так как в ней есть продукты`)
    return
  }
  
  if (confirm(`Удалить категорию "${category.name}"?`)) {
    deleteCategory(category.id)
  }
}

const deleteCategory = async (categoryId) => {
  try {
    await adminService.deleteCategory(categoryId)
    await loadCategories()
  } catch (error) {
    console.error('Error deleting category:', error)
    alert(error.response?.data?.detail || 'Ошибка при удалении')
  }
}

const closeModal = () => {
  showModal.value = false
  editingCategory.value = null
}

onMounted(() => {
  loadCategories()
})
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
  flex-wrap: wrap;
  gap: 1rem;
}

.page-header h2 {
  color: var(--text-primary);
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
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
}

.categories-table-container {
  background: var(--card-bg);
  border-radius: 16px;
  border: 1px solid var(--border-color);
  overflow-x: auto;
}

.categories-table {
  width: 100%;
  border-collapse: collapse;
}

.categories-table th {
  text-align: left;
  padding: 1rem;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.85rem;
  border-bottom: 1px solid var(--border-color);
}

.categories-table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  vertical-align: middle;
}

.categories-table tr:hover {
  background: var(--hover-bg);
}

.category-id {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.category-icon {
  font-size: 1.5rem;
}

.category-name {
  font-weight: 600;
}

.category-description {
  color: var(--text-secondary);
  font-size: 0.9rem;
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

.delete-btn:hover:not(:disabled) {
  background: #fdd;
  transform: scale(1.05);
}

.delete-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
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
  max-width: 450px;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid var(--border-color);
}

.modal-content h3 {
  margin-bottom: 1.5rem;
  color: var(--text-primary);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--input-bg);
  color: var(--text-primary);
  font-size: 1rem;
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

@media (max-width: 768px) {
  .categories-table-container {
    overflow-x: scroll;
  }
  
  .categories-table {
    min-width: 600px;
  }
}
</style>
