import axios from 'axios'

const base = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: base + '/auth',
  headers: { 'Content-Type': 'application/json' },
})

export const authService = {
  register(data) { return api.post('/register/', data) },
  login(data)    { return api.post('/login/', data) },
  refresh(data)  { return api.post('/refresh/', data) },
}
