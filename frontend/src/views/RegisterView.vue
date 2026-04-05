<template>
  <div class="register-page">
    <div class="register-container">
      <h2>Регистрация</h2>
      
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">Имя пользователя *</label>
          <input 
            type="text" 
            id="username"
            v-model="form.username"
            required
          >
        </div>
        
        <div class="form-group">
          <label for="email">Email *</label>
          <input 
            type="email" 
            id="email"
            v-model="form.email"
            required
          >
        </div>
        
        <div class="form-group">
          <label for="full_name">Полное имя</label>
          <input 
            type="text" 
            id="full_name"
            v-model="form.full_name"
          >
        </div>
        
        <div class="form-group">
          <label for="password">Пароль *</label>
          <input 
            type="password" 
            id="password"
            v-model="form.password"
            required
            minlength="6"
          >
        </div>
        
        <div class="form-group">
          <label for="role">Роль *</label>
          <select id="role" v-model="form.role" required>
            <option value="developer">Разработчик</option>
            <option value="manager">Менеджер</option>
          </select>
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div v-if="success" class="success-message">
          Регистрация успешна! Перенаправление на вход...
        </div>
        
        <button type="submit" :disabled="loading">
          {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>
      </form>
      
      <p class="login-link">
        Уже есть аккаунт? 
        <router-link to="/login">Войти</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const form = ref({
  username: '',
  email: '',
  full_name: '',
  password: '',
  role: 'developer'
});

const error = ref('');
const success = ref(false);
const loading = ref(false);

const handleRegister = async () => {
  loading.value = true;
  error.value = '';
  
  const result = await authStore.register(form.value);
  
  if (result.success) {
    success.value = true;
    setTimeout(() => {
      router.push('/login');
    }, 2000);
  } else {
    error.value = result.message;
  }
  
  loading.value = false;
};
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background-color: #f9f9f9;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.register-container {
  background-color: white;
  padding: 3rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}

.register-container h2 {
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
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #2ecc71;
}

button {
  width: 100%;
  padding: 1rem;
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover:not(:disabled) {
  background-color: #27ae60;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
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

.login-link {
  text-align: center;
  margin-top: 1.5rem;
  color: #666;
}

.login-link a {
  color: #2ecc71;
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>