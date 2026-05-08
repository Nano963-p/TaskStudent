import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export const taskService = {
  // GET /api/tasks/ — avec filtres optionnels
  getAll(params = {}) {
    return api.get('/tasks/', { params })
  },

  // GET /api/tasks/:id/
  getById(id) {
    return api.get(`/tasks/${id}/`)
  },

  // POST /api/tasks/
  create(data) {
    return api.post('/tasks/', data)
  },

  // PUT /api/tasks/:id/
  update(id, data) {
    return api.put(`/tasks/${id}/`, data)
  },

  // PATCH /api/tasks/:id/  — mise à jour partielle (ex: juste le statut)
  patch(id, data) {
    return api.patch(`/tasks/${id}/`, data)
  },

  // DELETE /api/tasks/:id/
  delete(id) {
    return api.delete(`/tasks/${id}/`)
  },

  // GET /api/tasks/stats/
  getStats() {
    return api.get('/tasks/stats/')
  },
}

export default api
