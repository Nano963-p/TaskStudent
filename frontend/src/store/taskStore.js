import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { taskService } from '../services/taskService'

export const useTaskStore = defineStore('tasks', () => {
  const tasks = ref([])
  const stats = ref({ total: 0, todo: 0, doing: 0, done: 0, urgent: 0 })
  const loading = ref(false)
  const error = ref(null)

  function setApiError(e, fallback) {
    if (e.response?.status === 404) error.value = 'Ressource introuvable.'
    else if (e.response?.status >= 500) error.value = 'Erreur serveur. Réessayez plus tard.'
    else error.value = fallback
  }

  // Getters
  const urgentTasks = computed(() =>
    tasks.value.filter(t => t.priority === 'urgente' && t.status !== 'terminée')
  )
  const overdueTasks = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return tasks.value.filter(t => t.deadline && t.deadline < today && t.status !== 'terminée')
  })
  const soonDueTasks = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    const in3   = new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    return tasks.value.filter(t =>
      t.deadline && t.deadline >= today && t.deadline <= in3 && t.status !== 'terminée'
    )
  })

  // Actions
  async function fetchTasks(params = {}) {
    loading.value = true
    error.value = null
    try {
      const res = await taskService.getAll(params)
      tasks.value = res.data.results || res.data
    } catch (e) {
      setApiError(e, 'Erreur lors du chargement des tâches.')
    } finally {
      loading.value = false
    }
  }

  async function fetchStats() {
    try {
      const res = await taskService.getStats()
      stats.value = res.data
    } catch (e) {
      setApiError(e, 'Erreur lors du chargement des statistiques.')
    }
  }

  async function createTask(data) {
    try {
      const res = await taskService.create(data)
      tasks.value.unshift(res.data)
      await fetchStats()
      return res.data
    } catch (e) {
      setApiError(e, 'Erreur lors de la création de la tâche.')
      throw e
    }
  }

  async function updateTask(id, data) {
    try {
      const res = await taskService.update(id, data)
      const idx = tasks.value.findIndex(t => t.id === id)
      if (idx !== -1) tasks.value[idx] = res.data
      await fetchStats()
      return res.data
    } catch (e) {
      setApiError(e, 'Erreur lors de la modification de la tâche.')
      throw e
    }
  }

  async function patchTask(id, data) {
    try {
      const res = await taskService.patch(id, data)
      const idx = tasks.value.findIndex(t => t.id === id)
      if (idx !== -1) tasks.value[idx] = res.data
      await fetchStats()
      return res.data
    } catch (e) {
      setApiError(e, 'Erreur lors de la modification de la tâche.')
      throw e
    }
  }

  async function deleteTask(id) {
    try {
      await taskService.delete(id)
      tasks.value = tasks.value.filter(t => t.id !== id)
      await fetchStats()
    } catch (e) {
      setApiError(e, 'Erreur lors de la suppression de la tâche.')
      throw e
    }
  }

  return {
    tasks, stats, loading, error,
    urgentTasks, overdueTasks, soonDueTasks,
    fetchTasks, fetchStats, createTask, updateTask, patchTask, deleteTask,
  }
})
