import axios from 'axios'

// En développement : /api (proxy Vite → http://127.0.0.1:8000)
// En production   : VITE_API_URL défini dans les variables d'environnement Vercel
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// On 401, clear session and redirect to login
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('auth_user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const taskService = {
  getAll(params = {})  { return api.get('/tasks/', { params }) },
  getById(id)          { return api.get(`/tasks/${id}/`) },
  create(data)         { return api.post('/tasks/', data) },
  update(id, data)     { return api.put(`/tasks/${id}/`, data) },
  patch(id, data)      { return api.patch(`/tasks/${id}/`, data) },
  delete(id)           { return api.delete(`/tasks/${id}/`) },
  getStats()           { return api.get('/tasks/stats/') },
}

export default api
