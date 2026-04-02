import axios from 'axios'

// В Docker контейнере API доступен через прокси Nginx по пути /api/
// Для локальной разработки используем localhost
const API_URL = import.meta.env.PROD ? '/api' : 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api