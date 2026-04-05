<template>
  <div class="login-page">
    <div class="login-container">
      <h2>Вход в систему</h2>
      
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Имя пользователя</label>
          <input 
            type="text" 
            id="username"
            v-model="form.username"
            required
          >
        </div>
        
        <div class="form-group">
          <label for="password">Пароль</label>
          <input 
            type="password" 
            id="password"
            v-model="form.password"
            required
          >
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <button type="submit" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>
      
      <p class="register-link">
        Нет аккаунта? 
        <router-link to="/register">Зарегистрироваться</router-link>
      </p>
      
      <div class="demo-accounts">
        <p>Тестовые аккаунты:</p>
        <ul>
          <li>superuser / admin123</li>
          <li>dev_ivan / dev123</li>
          <li>manager_alex / manager123</li>
        </ul>
      </div>
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
  password: ''
});

const error = ref('');
const loading = ref(false);

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  
  const result = await authStore.login(form.value.username, form.value.password);
  
  if (result.success) {
    router.push('/');
  } else {
    error.value = result.message;
  }
  
  loading.value = false;
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background-color: #f9f9f9;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.login-container {
  background-color: white;
  padding: 3rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}

.login-container h2 {
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

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
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

.register-link {
  text-align: center;
  margin-top: 1.5rem;
  color: #666;
}

.register-link a {
  color: #2ecc71;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  text-decoration: underline;
}

.demo-accounts {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
  color: #999;
  font-size: 0.9rem;
}

.demo-accounts ul {
  margin-top: 0.5rem;
  padding-left: 1.5rem;
}
</style>