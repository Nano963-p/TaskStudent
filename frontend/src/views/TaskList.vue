<template>
  <div class="task-list-view">
    <div class="filter-bar">
      <div class="filter-head">
        <strong>Liste des tâches</strong>
        <input
          ref="searchInput"
          class="search-input"
          v-model="search"
          placeholder="Rechercher une tâche..."
          @focus="searchFocused = true"
          @blur="searchFocused = false"
        />
      </div>

      <div class="filter-row">
        <div class="filter-group">
          <span class="filter-label">Statut</span>
          <div class="select-wrap">
            <select class="filter-select" v-model="filterStatus">
              <option v-for="s in statusOptions" :key="s.value" :value="s.value">{{ s.label }}</option>
            </select>
          </div>
        </div>

        <div class="filter-group">
          <span class="filter-label">Priorité</span>
          <div class="select-wrap">
            <select class="filter-select" v-model="filterPriority">
              <option v-for="p in priorityOptions" :key="p.value" :value="p.value">{{ p.label }}</option>
            </select>
          </div>
        </div>

        <button v-if="hasActiveFilters" class="btn-secondary" @click="clearFilters">Effacer</button>
      </div>
    </div>

    <div class="result-bar" v-if="!store.loading">
      {{ filteredTasks.length }} tâche{{ filteredTasks.length !== 1 ? 's' : '' }} trouvée{{ filteredTasks.length !== 1 ? 's' : '' }}
    </div>

    <div v-if="store.loading" class="state-loading">
      <div class="spinner"></div>
      <span>Chargement...</span>
    </div>

    <div v-else-if="store.error" class="state-error">
      {{ store.error }}
    </div>

    <div v-else-if="filteredTasks.length" class="table-wrap">
      <table class="task-table">
        <thead>
          <tr>
            <th>Titre</th>
            <th>Matière</th>
            <th>Priorité</th>
            <th>Statut</th>
            <th>Deadline</th>
            <th class="actions-col">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in filteredTasks" :key="task.id" :class="{ overdue: task.is_overdue }">
            <td>
              <span :class="{ done: task.status === 'terminée' }">{{ task.title }}</span>
            </td>
            <td>{{ task.subject }}</td>
            <td>
              <span :class="['badge', `priority-${task.priority}`]">{{ task.priority }}</span>
            </td>
            <td>
              <span :class="['status-badge', statusClass(task.status)]">{{ statusLabel(task.status) }}</span>
            </td>
            <td>{{ task.deadline ? formatDate(task.deadline) : '-' }}</td>
            <td class="actions">
              <button
                v-if="task.status !== 'terminée'"
                class="btn-finish"
                @click="finishTask(task)"
              >
                Terminer
              </button>
              <button class="btn-secondary" @click="emit('edit', task)">Modifier</button>
              <template v-if="deleteConfirmId === task.id">
                <span class="confirm-text">Supprimer ?</span>
                <button class="btn-confirm-yes" @click="deleteTask(task)">Oui</button>
                <button class="btn-confirm-no" @click="deleteConfirmId = null">Non</button>
              </template>
              <button v-else class="btn-danger" @click="deleteConfirmId = task.id">Supprimer</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="state-empty">
      <p class="empty-title">Aucune tâche trouvée</p>
      <p class="empty-sub">Modifiez les filtres ou créez une nouvelle tâche.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted, onUnmounted } from 'vue'
import { useTaskStore } from '../store/taskStore'
import { useGamificationStore } from '../store/gamificationStore'

const store = useTaskStore()
const gamification = useGamificationStore()
const showToast = inject('showToast')
const emit = defineEmits(['edit'])

const filterStatus = ref('all')
const filterPriority = ref('all')
const search = ref('')
const searchFocused = ref(false)
const searchInput = ref(null)
const deleteConfirmId = ref(null)

const statusOptions = [
  { value: 'all', label: 'Tous', key: 'all' },
  { value: 'à faire', label: 'À faire', key: 'todo' },
  { value: 'en cours', label: 'En cours', key: 'doing' },
  { value: 'terminée', label: 'Terminée', key: 'done' },
]

const priorityOptions = [
  { value: 'all', label: 'Toutes', key: 'all' },
  { value: 'urgente', label: 'Urgente', key: 'urgent' },
  { value: 'haute', label: 'Haute', key: 'high' },
  { value: 'moyenne', label: 'Moyenne', key: 'medium' },
  { value: 'faible', label: 'Faible', key: 'low' },
]

const filteredTasks = computed(() =>
  store.tasks.filter(task => {
    if (filterStatus.value !== 'all' && task.status !== filterStatus.value) return false
    if (filterPriority.value !== 'all' && task.priority !== filterPriority.value) return false
    if (!search.value) return true

    const q = search.value.toLowerCase()
    return (
      task.title.toLowerCase().includes(q) ||
      task.subject.toLowerCase().includes(q) ||
      (task.description || '').toLowerCase().includes(q)
    )
  })
)

const hasActiveFilters = computed(() =>
  filterStatus.value !== 'all' || filterPriority.value !== 'all' || search.value !== ''
)

function clearFilters() {
  filterStatus.value = 'all'
  filterPriority.value = 'all'
  search.value = ''
}

function formatDate(date) {
  return new Date(`${date}T00:00:00`).toLocaleDateString('fr-FR')
}

function statusLabel(status) {
  const labels = {
    'à faire': 'À faire',
    'en cours': 'En cours',
    'terminée': 'Terminée',
  }
  return labels[status] || status
}

function statusClass(status) {
  if (status === 'terminée') return 'status-badge--done'
  if (status === 'en cours') return 'status-badge--doing'
  return 'status-badge--todo'
}

async function changeStatus(task, status) {
  try {
    const res = await store.patchTask(task.id, { status })
    if (res.xp_earned > 0) {
      gamification.applyXpChange(res.xp_earned, 1)
      showToast(`+${res.xp_earned} XP · Tâche terminée`, 'success')
      await gamification.fetchProfile()
    } else if (res.xp_subtracted > 0) {
      gamification.applyXpChange(-res.xp_subtracted, -1)
      showToast(`-${res.xp_subtracted} XP · Tâche remise en attente`, 'danger')
      await gamification.fetchProfile()
    } else {
      showToast('Statut mis à jour', 'success')
    }
  } catch {
    showToast('Impossible de modifier le statut.', 'danger')
  }
}

async function finishTask(task) {
  await changeStatus(task, 'terminée')
}

async function deleteTask(task) {
  try {
    await store.deleteTask(task.id)
    deleteConfirmId.value = null
    showToast('Tâche supprimée', 'danger')
  } catch {
    showToast('Impossible de supprimer la tâche.', 'danger')
  }
}

function handleSlash(event) {
  if (event.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) {
    event.preventDefault()
    searchInput.value?.focus()
  }
}

onMounted(() => window.addEventListener('keydown', handleSlash))
onUnmounted(() => window.removeEventListener('keydown', handleSlash))
</script>

<style scoped>
.task-list-view {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.filter-bar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-head,
.result-bar,
.state-loading {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-head {
  justify-content: space-between;
}

.filter-row {
  display: flex;
  align-items: flex-end;
  gap: 14px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.filter-label {
  color: var(--muted);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.8px;
  text-transform: uppercase;
}

.select-wrap {
  position: relative;
  min-width: 210px;
}

.select-wrap::after {
  content: '';
  position: absolute;
  right: 14px;
  top: 50%;
  width: 8px;
  height: 8px;
  border-right: 2px solid var(--accent-light);
  border-bottom: 2px solid var(--accent-light);
  transform: translateY(-65%) rotate(45deg);
  pointer-events: none;
}

.search-input,
.filter-select {
  background: var(--surface2);
  border: 1px solid var(--border2);
  border-radius: var(--radius-xs);
  color: var(--text);
  font-size: 13px;
  outline: none;
}

.search-input {
  width: 260px;
  padding: 9px 12px;
}

.filter-select {
  width: 100%;
  appearance: none;
  color-scheme: dark;
  padding: 10px 42px 10px 13px;
  cursor: pointer;
  font-weight: 700;
}

.filter-select option {
  background: #111827;
  color: #E8EEF8;
  font-weight: 700;
}

.filter-select option:checked {
  background: #0F766E;
  color: #FFFFFF;
}

.search-input:focus,
.filter-select:focus {
  border-color: rgba(0,212,176,0.50);
  box-shadow: 0 0 0 3px rgba(0,212,176,0.10);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}

.status-badge--todo {
  background: var(--warn-dim);
  color: var(--warn);
}

.status-badge--doing {
  background: var(--accent-dim);
  color: var(--accent-light);
}

.status-badge--done {
  background: var(--success-dim);
  color: var(--success);
}

.result-bar {
  color: var(--muted);
  font-size: 13px;
}

.table-wrap {
  width: 100%;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
}

.task-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 760px;
}

.task-table th,
.task-table td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border);
  text-align: left;
  font-size: 13px;
  vertical-align: middle;
}

.task-table th {
  color: var(--muted);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

.task-table tr:last-child td {
  border-bottom: none;
}

.task-table tbody tr:hover {
  background: var(--surface2);
}

.task-table .overdue td {
  background: rgba(239,68,68,0.05);
}

.done {
  color: var(--muted);
  text-decoration: line-through;
}

.badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 3px 9px;
  font-size: 11px;
  font-weight: 700;
}

.priority-urgente { color: #FCA5A5; background: var(--danger-dim); }
.priority-haute { color: var(--warn); background: var(--warn-dim); }
.priority-moyenne { color: var(--accent-light); background: var(--accent-dim); }
.priority-faible { color: var(--text2); background: var(--surface3); }

.actions-col {
  width: 280px;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-finish,
.btn-secondary,
.btn-danger,
.btn-confirm-yes,
.btn-confirm-no {
  border: 1px solid var(--border2);
  border-radius: var(--radius-xs);
  padding: 7px 10px;
  color: var(--text);
  background: var(--surface2);
  font-size: 12px;
}

.btn-finish {
  color: var(--accent-light);
  background: var(--accent-dim);
  border-color: rgba(0,212,176,0.28);
}

.btn-finish:hover {
  background: rgba(0,212,176,0.20);
}

.btn-secondary:hover {
  border-color: rgba(0,212,176,0.35);
  color: var(--accent-light);
}

.btn-danger {
  color: #FCA5A5;
  background: var(--danger-dim);
  border-color: rgba(239,68,68,0.25);
}

.btn-danger:hover {
  background: rgba(239,68,68,0.20);
}

.confirm-text {
  align-self: center;
  color: var(--text2);
  font-size: 12px;
  font-weight: 700;
}

.btn-confirm-yes {
  color: #fff;
  background: var(--danger);
  border-color: rgba(239,68,68,0.55);
}

.btn-confirm-yes:hover {
  background: #DC2626;
}

.btn-confirm-no {
  color: var(--text2);
  background: var(--surface3);
}

.btn-confirm-no:hover {
  color: var(--text);
  border-color: var(--border3);
}

.state-loading,
.state-error,
.state-empty {
  padding: 34px 0;
  color: var(--muted);
  font-size: 13px;
}

.state-error {
  color: #FCA5A5;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--border2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

.empty-title {
  color: var(--text2);
  font-weight: 700;
  margin-bottom: 6px;
}

@media (max-width: 720px) {
  .filter-head,
  .filter-row {
    align-items: stretch;
    flex-direction: column;
  }

  .search-input,
  .filter-group,
  .select-wrap {
    width: 100%;
  }
}
</style>
