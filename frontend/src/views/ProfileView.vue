<template>
  <div class="profile-page">
    <div class="profile-container">
      <h2>Редактирование профиля</h2>
      
      <form @submit.prevent="handleUpdate">
        <div class="form-group">
          <label for="full_name">Полное имя</label>
          <input 
            type="text" 
            id="full_name"
            v-model="form.full_name"
          >
        </div>
        
        <div class="form-group">
          <label for="email">Email</label>
          <input 
            type="email" 
            id="email"
            v-model="form.email"
            required
          >
        </div>
        
        <div class="form-group">
          <label for="bio">О себе</label>
          <textarea 
            id="bio"
            v-model="form.bio"
            rows="4"
            placeholder="Расскажите о себе..."
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>Роль</label>
          <input 
            type="text" 
            :value="getRoleName(authStore.user?.role)"
            disabled
            class="disabled-input"
          >
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div v-if="success" class="success-message">
          Профиль успешно обновлен!
        </div>
        
        <div class="button-group">
          <button type="submit" :disabled="loading">
            {{ loading ? 'Сохранение...' : 'Сохранить изменения' }}
          </button>
          <button type="button" class="cancel-btn" @click="cancelEdit">
            Отмена
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const form = ref({
  full_name: '',
  email: '',
  bio: ''
});

const error = ref('');
const success = ref(false);
const loading = ref(false);

const getRoleName = (role) => {
  const roles = {
    developer: 'Разработчик',
    manager: 'Менеджер',
    superuser: 'Суперпользователь'
  };
  return roles[role] || role;
};

const loadUserData = () => {
  if (authStore.user) {
    form.value = {
      full_name: authStore.user.full_name || '',
      email: authStore.user.email || '',
      bio: authStore.user.bio || ''
    };
  }
};

const handleUpdate = async () => {
  loading.value = true;
  error.value = '';
  success.value = false;
  
  const result = await authStore.updateUser(form.value);
  
  if (result.success) {
    success.value = true;
    setTimeout(() => {
      success.value = false;
    }, 3000);
  } else {
    error.value = result.message;
  }
  
  loading.value = false;
};

const cancelEdit = () => {
  router.back();
};

onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  loadUserData();
});
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: #f9f9f9;
  padding: 2rem;
}

.profile-container {
  max-width: 600px;
  margin: 0 auto;
  background-color: white;
  padding: 3rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.profile-container h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.form-group {
  margin-bottom: 1.5rem;
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
  transition: border-color 0.3s;
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2ecc71;
}

.disabled-input {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.button-group {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.button-group button {
  flex: 1;
  padding: 1rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.button-group button[type="submit"] {
  background-color: #2ecc71;
  color: white;
}

.button-group button[type="submit"]:hover:not(:disabled) {
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
  text-align: center;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  text-align: center;
}
</style>