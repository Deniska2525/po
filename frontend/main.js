import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './src/App.vue'
import router from './src/router'
import { useAuthStore } from './src/stores/auth'
import { useThemeStore } from './src/stores/theme'
import './src/assets/main.css'
import './src/assets/components.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Инициализация темы
const themeStore = useThemeStore(pinia)
themeStore.init()

// Загрузка пользователя
const authStore = useAuthStore(pinia)
if (authStore.token) {
  authStore.fetchUser().catch(() => authStore.logout())
}

app.mount('#app')