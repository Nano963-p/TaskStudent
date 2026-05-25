import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/taskService'

export const useGamificationStore = defineStore('gamification', () => {
  const profile = ref({
    total_xp: 0,
    level: 1,
    tasks_completed: 0,
    xp_current_level: 0,
    xp_next_level: 200,
    xp_progress_pct: 0,
    badges: [],
  })

  const focusedTask = ref(null)

  async function fetchProfile() {
    try {
      const res = await api.get('/auth/profile/')
      profile.value = res.data
    } catch (e) {
      console.error('Erreur profil gamification:', e)
    }
  }

  function startFocus(task) {
    focusedTask.value = task
  }

  function stopFocus() {
    focusedTask.value = null
  }

  return { profile, focusedTask, fetchProfile, startFocus, stopFocus }
})
