<template>
  <div class="admin-users">
    <div class="page-header">
      <h2>Управление пользователями</h2>
      <div class="header-actions">
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Поиск по имени или email..."
            @input="debouncedSearch"
          >
          <span class="search-icon">🔍</span>
        </div>
        <select v-model="roleFilter" @change="loadUsers" class="filter-select">
          <option value="">Все роли</option>
          <option value="user">Пользователь</option>
          <option value="developer">Разработчик</option>
          <option value="manager">Менеджер</option>
          <option value="admin">Админ</option>
          <option value="superuser">Суперпользователь</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка пользователей...</p>
    </div>

    <div v-else class="users-table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Пользователь</th>
            <th>Email</th>
            <th>Роль</th>
            <th>Статус</th>
            <th>Дата регистрации</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>#{{ user.id }}</td>
            <td class="user-cell">
              <div class="user-avatar">{{ user.full_name?.[0] || user.username[0] }}</div>
              <div>
                <div class="user-name">{{ user.full_name || '—' }}</div>
                <div class="user-username">{{ user.username }}</div>
              </div>
            </td>
            <td>{{ user.email }}</td>
            <td>
              <select 
                v-model="user.role" 
                @change="updateUserRole(user)"
                class="role-select"
                :class="getRoleClass(user.role)"
              >
                <option value="user">👤 Пользователь</option>
                <option value="developer">👨‍💻 Разработчик</option>
                <option value="manager">📊 Менеджер</option>
                <option value="admin">👑 Админ</option>
                <option value="superuser">⭐ Суперпользователь</option>
              </select>
            </td>
            <td>
              <span class="status-badge" :class="user.is_active ? 'active' : 'inactive'">
                {{ user.is_active ? 'Активен' : 'Заблокирован' }}
              </span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td class="actions">
              <button 
                class="action-btn edit" 
                @click="editUser(user)"
                title="Редактировать"
              >
                ✏️
              </button>
              <button 
                class="action-btn delete" 
                @click="confirmDeleteUser(user)"
                title="Удалить"
                :disabled="user.role === 'superuser'"
              >
                🗑️
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button 
          :disabled="currentPage === 1" 
          @click="currentPage--; loadUsers()"
        >
          ←
        </button>
        <span>Стр. {{ currentPage }} из {{ totalPages }}</span>
        <button 
          :disabled="currentPage === totalPages" 
          @click="currentPage++; loadUsers()"
        >
          →
        </button>
      </div>
    </div>

    <!-- Модальное окно редактирования пользователя -->
    <div v-if="editingUser" class="modal">
      <div class="modal-content">
        <h3>Редактирование пользователя</h3>
        
        <div class="form-group">
          <label>Полное имя</label>
          <input v-model="editForm.full_name" type="text">
        </div>
        
        <div class="form-group">
          <label>Email</label>
          <input v-model="editForm.email" type="email">
        </div>
        
        <div class="form-group">
          <label>Роль</label>
          <select v-model="editForm.role">
            <option value="user">Пользователь</option>
            <option value="developer">Разработчик</option>
            <option value="manager">Менеджер</option>
            <option value="admin">Админ</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>
            <input type="checkbox" v-model="editForm.is_active">
            Активен
          </label>
        </div>
        
        <div class="modal-actions">
          <button class="save-btn" @click="saveUserEdit">Сохранить</button>
          <button class="cancel-btn" @click="editingUser = null">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления -->
    <div v-if="deletingUser" class="modal">
      <div class="modal-content confirm-delete">
        <h3>Подтверждение удаления</h3>
        <p>Вы уверены, что хотите удалить пользователя <strong>{{ deletingUser.username }}</strong>?</p>
        <p class="warning">Это действие нельзя отменить!</p>
        
        <div class="modal-actions">
          <button class="delete-btn" @click="deleteUser">Удалить</button>
          <button class="cancel-btn" @click="deletingUser = null">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import adminService from '../services/admin';
import debounce from 'lodash/debounce';

const users = ref([]);
const loading = ref(true);
const currentPage = ref(1);
const totalPages = ref(1);
const searchQuery = ref('');
const roleFilter = ref('');
const editingUser = ref(null);
const deletingUser = ref(null);

const editForm = ref({
  full_name: '',
  email: '',
  role: '',
  is_active: true
});

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
};

const getRoleClass = (role) => {
  const classes = {
    user: 'role-user',
    developer: 'role-developer',
    manager: 'role-manager',
    admin: 'role-admin',
    superuser: 'role-superuser'
  };
  return classes[role] || '';
};

const loadUsers = async () => {
  loading.value = true;
  try {
    const params = {
      skip: (currentPage.value - 1) * 10,
      limit: 10,
      search: searchQuery.value || undefined,
      role: roleFilter.value || undefined
    };
    const data = await adminService.getUsers(params);
    users.value = data;
    totalPages.value = Math.ceil(data.length / 10) || 1;
    console.log('Loaded users:', data); // для отладки
  } catch (error) {
    console.error('Error loading users:', error);
  } finally {
    loading.value = false;
  }
};

const debouncedSearch = debounce(() => {
  currentPage.value = 1;
  loadUsers();
}, 300);

const updateUserRole = async (user) => {
  try {
    await adminService.updateUserRole(user.id, user.role);
    // Показываем уведомление об успехе
  } catch (error) {
    console.error('Error updating role:', error);
    // Откатываем изменение при ошибке
    await loadUsers();
  }
};

const editUser = (user) => {
  editingUser.value = user;
  editForm.value = {
    full_name: user.full_name || '',
    email: user.email,
    role: user.role,
    is_active: user.is_active
  };
};

const saveUserEdit = async () => {
  try {
    await adminService.updateUser(editingUser.value.id, editForm.value);
    editingUser.value = null;
    await loadUsers();
  } catch (error) {
    console.error('Error saving user:', error);
  }
};

const confirmDeleteUser = (user) => {
  if (user.role === 'superuser') return;
  deletingUser.value = user;
};

const deleteUser = async () => {
  try {
    await adminService.deleteUser(deletingUser.value.id);
    deletingUser.value = null;
    await loadUsers();
  } catch (error) {
    console.error('Error deleting user:', error);
  }
};

watch(roleFilter, () => {
  currentPage.value = 1;
  loadUsers();
});

onMounted(() => {
  loadUsers();
});
</script>

<style scoped>
.admin-users {
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

.search-box {
  position: relative;
  min-width: 300px;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #e0e7ed;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.2s;
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

.filter-select {
  padding: 0.75rem 2rem 0.75rem 1rem;
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

.filter-select:focus {
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

.users-table-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  overflow: hidden;
  border: 1px solid #eaeef2;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #4a5568;
  font-size: 0.9rem;
  border-bottom: 2px solid #eaeef2;
}

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid #eaeef2;
  color: #1a2634;
}

.users-table tr:hover {
  background: #f8fafc;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
  text-transform: uppercase;
}

.user-name {
  font-weight: 500;
}

.user-username {
  font-size: 0.85rem;
  color: #94a3b8;
}

.role-select {
  padding: 0.4rem 1.5rem 0.4rem 0.75rem;
  border: 1px solid #e0e7ed;
  border-radius: 20px;
  font-size: 0.85rem;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.3rem center;
  background-size: 1rem;
}

.role-select.role-user { background-color: #f1f5f9; color: #4a5568; }
.role-select.role-developer { background-color: #e8f5e9; color: #2ecc71; }
.role-select.role-manager { background-color: #fff3e0; color: #f39c12; }
.role-select.role-admin { background-color: #e3f2fd; color: #2196f3; }
.role-select.role-superuser { background-color: #f3e5f5; color: #9c27b0; }

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-badge.active {
  background: #e8f5e9;
  color: #2ecc71;
}

.status-badge.inactive {
  background: #fee;
  color: #e74c3c;
}

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
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.action-btn.edit:hover {
  background: #e8f5e9;
  color: #2ecc71;
}

.action-btn.delete:hover:not(:disabled) {
  background: #fee;
  color: #e74c3c;
}

.action-btn.delete:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid #eaeef2;
}

.pagination button {
  padding: 0.5rem 1rem;
  border: 1px solid #e0e7ed;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination button:hover:not(:disabled) {
  background: #2ecc71;
  color: white;
  border-color: #2ecc71;
}

.pagination button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* Модальные окна */
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
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.modal-content h3 {
  margin-bottom: 1.5rem;
  color: #1a2634;
  font-size: 1.3rem;
}

.modal-content.confirm-delete {
  text-align: center;
}

.modal-content .warning {
  color: #e74c3c;
  font-size: 0.9rem;
  margin: 1rem 0;
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

.form-group input[type="text"],
.form-group input[type="email"],
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e0e7ed;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #2ecc71;
  box-shadow: 0 0 0 3px rgba(46, 204, 113, 0.1);
}

.form-group input[type="checkbox"] {
  margin-right: 0.5rem;
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

.save-btn:hover {
  background: #27ae60;
}

.delete-btn {
  background: #e74c3c;
  color: white;
}

.delete-btn:hover {
  background: #c0392b;
}

.cancel-btn {
  background: #f1f5f9;
  color: #4a5568;
}

.cancel-btn:hover {
  background: #e2e8f0;
}
</style>