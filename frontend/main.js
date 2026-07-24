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

// Восстановление сессии через refresh-токен в httpOnly cookie.
// Ждём завершения до монтирования, иначе router guard успеет сработать
// до восстановления сессии и выкинет залогиненного пользователя на /login.
const authStore = useAuthStore(pinia)
authStore.init().finally(() => app.mount('#app'))