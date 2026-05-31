import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/taskService'

const LEVELS = [0, 200, 500, 1000, 2000, 3500, 5000]

export const useGamificationStore = defineStore('gamification', () => {
  const profile = ref({
    total_xp: 0,
    level: 1,
    tasks_completed: 0,
    xp_current_level: 0,
    xp_next_level: 200,
    xp_progress_pct: 0,
  })

  const focusedTask = ref(null)

  function buildProfile(totalXp, tasksCompleted = profile.value.tasks_completed) {
    const total = Math.max(0, totalXp)
    let level = 1

    LEVELS.forEach((requiredXp, index) => {
      if (total >= requiredXp) level = index + 1
    })

    const currentLevelXp = LEVELS[level - 1] ?? 0
    const nextLevelXp = LEVELS[level] ?? total + 1000
    const progress = nextLevelXp <= currentLevelXp
      ? 100
      : Math.round(((total - currentLevelXp) / (nextLevelXp - currentLevelXp)) * 100)

    return {
      total_xp: total,
      level,
      tasks_completed: Math.max(0, tasksCompleted),
      xp_current_level: currentLevelXp,
      xp_next_level: nextLevelXp,
      xp_progress_pct: progress,
    }
  }

  function applyXpChange(delta, completedDelta = 0) {
    if (!delta && !completedDelta) return
    profile.value = buildProfile(
      profile.value.total_xp + delta,
      profile.value.tasks_completed + completedDelta
    )
  }

  async function fetchProfile() {
    try {
      const res = await api.get('/auth/profile/')
      profile.value = res.data
    } catch (e) {
      console.error('Erreur profil:', e)
    }
  }

  function startFocus(task) {
    focusedTask.value = task
  }

  function stopFocus() {
    focusedTask.value = null
  }

  return { profile, focusedTask, fetchProfile, applyXpChange, startFocus, stopFocus }
})
