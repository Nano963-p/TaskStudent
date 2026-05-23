import axios from 'axios'

const api = axios.create({
  baseURL: '/api/auth',
  headers: { 'Content-Type': 'application/json' },
})

export const authService = {
  register(data) { return api.post('/register/', data) },
  login(data)    { return api.post('/login/', data) },
  refresh(data)  { return api.post('/refresh/', data) },
}
