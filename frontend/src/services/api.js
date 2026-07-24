import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Access-токен держим только в памяти (не в localStorage — его может
// прочитать любой XSS-скрипт). Сессия восстанавливается через refresh-токен
// в httpOnly cookie (см. stores/auth.js -> init()).
let accessToken = null

export function setAccessToken(token) {
  accessToken = token
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

api.interceptors.request.use(config => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

// При 401 пробуем один раз обновить access-токен через refresh-cookie
// и повторить исходный запрос. Если refresh тоже не сработал — сессия истекла.
let refreshPromise = null

api.interceptors.response.use(
  response => response,
  async error => {
    const original = error.config
    const isAuthUrl = original?.url?.includes('/users/login')
      || original?.url?.includes('/users/refresh')
      || original?.url?.includes('/users/logout')

    if (error.response?.status === 401 && original && !original._retried && !isAuthUrl) {
      original._retried = true
      try {
        if (!refreshPromise) {
          refreshPromise = api.post('/users/refresh').finally(() => { refreshPromise = null })
        }
        const { data } = await refreshPromise
        setAccessToken(data.access_token)
        return api(original)
      } catch {
        setAccessToken(null)
      }
    }
    return Promise.reject(error)
  }
)

export default api
