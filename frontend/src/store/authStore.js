import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '../services/authService'

export const useAuthStore = defineStore('auth', () => {
  const accessToken  = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const user         = ref(JSON.parse(localStorage.getItem('auth_user') || 'null'))

  const isAuthenticated = computed(() => !!accessToken.value)

  function _persist(access, refresh, u) {
    accessToken.value  = access
    refreshToken.value = refresh
    user.value         = u
    localStorage.setItem('access_token',  access)
    localStorage.setItem('refresh_token', refresh)
    localStorage.setItem('auth_user',     JSON.stringify(u))
  }

  async function login(credentials) {
    const res = await authService.login(credentials)
    _persist(res.data.access, res.data.refresh, {
      username: credentials.username,
    })
    return res.data
  }

  async function register(data) {
    const res = await authService.register(data)
    _persist(res.data.access, res.data.refresh, res.data.user)
    return res.data
  }

  function logout() {
    accessToken.value  = null
    refreshToken.value = null
    user.value         = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('auth_user')
  }

  return { accessToken, refreshToken, user, isAuthenticated, login, register, logout }
})
