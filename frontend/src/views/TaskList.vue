<template>
  <div class="task-list-view">

    <!-- ── FILTER BAR ──────────────────────────── -->
    <div class="filter-bar">

      <!-- Top row: title + search -->
      <div class="filter-head">
        <div class="filter-title-row">
          <span class="filter-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                 stroke-linecap="round" width="13" height="13">
              <line x1="4" y1="6" x2="20" y2="6"/>
              <line x1="8" y1="12" x2="16" y2="12"/>
              <line x1="11" y1="18" x2="13" y2="18"/>
            </svg>
          </span>
          <span class="filter-title">Filtres</span>
          <span v-if="activeFilterCount" class="filter-badge">{{ activeFilterCount }}</span>
        </div>

        <div class="search-wrap" :class="{ 'search-focused': searchFocused }">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" width="13" height="13">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            ref="searchInput"
            class="search-input"
            v-model="search"
            placeholder="Rechercher une tâche..."
            @focus="searchFocused = true"
            @blur="searchFocused = false"
          />
          <kbd v-if="!search && !searchFocused" class="search-hint">/</kbd>
          <button v-if="search" class="search-clear" @click="search = ''; searchInput.focus()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
                 stroke-linecap="round" width="11" height="11">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>

      <div class="filter-divider"></div>

      <!-- Status segmented control -->
      <div class="filter-row">
        <span class="row-label">Statut</span>
        <div class="seg-control">
          <button
            v-for="s in statusOptions"
            :key="s.value"
            :class="['seg-btn', { 'seg-btn--active': filterStatus === s.value }]"
            @click="filterStatus = s.value"
          >
            <span class="seg-indicator" :style="`--ic: ${s.color}`"></span>
            {{ s.label }}
          </button>
        </div>
      </div>

      <!-- Priority pills -->
      <div class="filter-row">
        <span class="row-label">Priorité</span>
        <div class="prio-row">
          <button
            v-for="p in priorityOptions"
            :key="p.value"
            :class="['prio-pill', { 'prio-pill--active': filterPriority === p.value }]"
            :style="filterPriority === p.value ? `--pc:${p.color || 'var(--accent)'};--pg:${p.glow || 'var(--accent-glow)'}` : ''"
            @click="filterPriority = p.value"
          >
            <span class="prio-dot" :style="`background:${p.color || 'var(--muted)'}`"></span>
            {{ p.label }}
          </button>
        </div>
      </div>

    </div>

    <!-- ── RESULT BAR ──────────────────────────── -->
    <div class="result-bar" v-if="!store.loading">
      <div class="result-left">
        <span class="result-num">{{ filteredTasks.length }}</span>
        <span class="result-text">tâche{{ filteredTasks.length !== 1 ? 's' : '' }} trouvée{{ filteredTasks.length !== 1 ? 's' : '' }}</span>
      </div>
      <Transition name="clear-fade">
        <button v-if="hasActiveFilters" class="clear-btn" @click="clearFilters">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
               stroke-linecap="round" width="10" height="10">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
          Effacer les filtres
        </button>
      </Transition>
    </div>

    <!-- ── TASK LIST ──────────────────────────── -->
    <div v-if="store.loading" class="state-loading">
      <div class="spinner"></div>
      <span>Chargement...</span>
    </div>

    <template v-else-if="filteredTasks.length">
      <TaskCard
        v-for="task in filteredTasks"
        :key="task.id"
        :task="task"
        @edit="emit('edit', task)"
        @deleted="onDeleted"
        @statusChanged="onStatusChanged"
      />
    </template>

    <div v-else class="state-empty">
      <div class="empty-glow"></div>
      <div class="empty-icon">🔍</div>
      <p class="empty-title">Aucune tâche trouvée</p>
      <p class="empty-sub">Modifiez vos filtres ou créez une nouvelle tâche</p>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, inject, onMounted, onUnmounted } from 'vue'
import { useTaskStore } from '../store/taskStore'
import TaskCard from '../components/TaskCard.vue'

const store      = useTaskStore()
const showToast  = inject('showToast')
const emit       = defineEmits(['edit'])

const filterStatus   = ref('all')
const filterPriority = ref('all')
const search         = ref('')
const searchFocused  = ref(false)
const searchInput    = ref(null)

const statusOptions = [
  { value: 'all',      label: 'Toutes',     color: 'var(--accent)' },
  { value: 'à faire',  label: 'À faire',    color: 'var(--warn)' },
  { value: 'en cours', label: 'En cours',   color: 'var(--accent)' },
  { value: 'terminée', label: 'Terminées',  color: 'var(--success)' },
]
const priorityOptions = [
  { value: 'all',     label: 'Toutes',   color: 'var(--accent)',   glow: 'var(--accent-glow)' },
  { value: 'urgente', label: 'Urgente',  color: '#EF4444',         glow: 'rgba(239,68,68,0.30)' },
  { value: 'haute',   label: 'Haute',    color: '#F59E0B',         glow: 'rgba(245,158,11,0.26)' },
  { value: 'moyenne', label: 'Moyenne',  color: '#00D4B0',         glow: 'rgba(0,212,176,0.28)' },
  { value: 'faible',  label: 'Faible',   color: 'var(--muted)',    glow: 'transparent' },
]

const filteredTasks = computed(() =>
  store.tasks.filter(t => {
    if (filterStatus.value   !== 'all' && t.status   !== filterStatus.value)   return false
    if (filterPriority.value !== 'all' && t.priority !== filterPriority.value) return false
    if (search.value) {
      const q = search.value.toLowerCase()
      return t.title.toLowerCase().includes(q) || t.subject.toLowerCase().includes(q)
    }
    return true
  })
)

const hasActiveFilters = computed(() =>
  filterStatus.value !== 'all' || filterPriority.value !== 'all' || search.value !== ''
)
const activeFilterCount = computed(() =>
  (filterStatus.value !== 'all' ? 1 : 0) +
  (filterPriority.value !== 'all' ? 1 : 0) +
  (search.value !== '' ? 1 : 0)
)

function clearFilters() {
  filterStatus.value   = 'all'
  filterPriority.value = 'all'
  search.value         = ''
}

function handleSlash(e) {
  if (e.key === '/' && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
    e.preventDefault()
    searchInput.value?.focus()
  }
}

onMounted(() => window.addEventListener('keydown', handleSlash))
onUnmounted(() => window.removeEventListener('keydown', handleSlash))

async function onDeleted() {
  await store.fetchTasks()
  await store.fetchStats()
  showToast('Tâche supprimée', 'danger')
}
async function onStatusChanged() {
  await store.fetchStats()
}
</script>

<style scoped>
.task-list-view { display: flex; flex-direction: column; }

/* ── Filter bar ──────────────────────────────── */
.filter-bar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 18px;
  margin-bottom: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Head row */
.filter-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.filter-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.filter-icon-wrap {
  width: 26px; height: 26px;
  background: var(--accent-dim);
  border: 1px solid rgba(0,212,176,0.18);
  border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  color: var(--accent);
  flex-shrink: 0;
}
.filter-title {
  font-size: 12px;
  font-weight: 700;
  color: var(--text2);
  letter-spacing: 0.3px;
}
.filter-badge {
  background: var(--grad);
  color: #fff;
  font-size: 9.5px;
  font-weight: 800;
  padding: 1px 6px;
  border-radius: 20px;
  line-height: 1.5;
}

/* Search */
.search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}
.search-icon {
  position: absolute;
  left: 11px;
  color: var(--muted);
  pointer-events: none;
  transition: color 0.18s;
}
.search-focused .search-icon { color: var(--accent); }

.search-input {
  background: var(--surface2);
  border: 1px solid var(--border2);
  border-radius: var(--radius-sm);
  padding: 7px 32px 7px 32px;
  color: var(--text);
  font-size: 12.5px;
  outline: none;
  width: 190px;
  transition: width 0.3s cubic-bezier(0.22,1,0.36,1), border-color 0.18s, box-shadow 0.18s, background 0.18s;
}
.search-focused .search-input {
  width: 250px;
  border-color: rgba(0,212,176,0.45);
  background: rgba(0,212,176,0.05);
  box-shadow: 0 0 0 3px rgba(0,212,176,0.08);
}
.search-input::placeholder { color: var(--muted); }

.search-hint {
  position: absolute;
  right: 10px;
  font-size: 10px;
  color: var(--muted);
  background: var(--surface3);
  border: 1px solid var(--border2);
  border-radius: 4px;
  padding: 1px 5px;
  pointer-events: none;
  font-family: var(--font-b);
  letter-spacing: 0;
}
.search-clear {
  position: absolute;
  right: 10px;
  background: var(--surface3);
  border: 1px solid var(--border2);
  border-radius: 4px;
  width: 18px; height: 18px;
  display: flex; align-items: center; justify-content: center;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.15s;
  padding: 0;
}
.search-clear:hover { color: var(--text); background: var(--border2); }

/* Divider */
.filter-divider {
  height: 1px;
  background: var(--border);
  margin: 0 -2px;
}

/* Filter rows */
.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.row-label {
  font-size: 9.5px;
  font-weight: 700;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 1.1px;
  width: 52px;
  flex-shrink: 0;
}

/* ── Segmented control ─────────────────────── */
.seg-control {
  display: inline-flex;
  background: rgba(0,0,0,0.22);
  border: 1px solid var(--border);
  border-radius: 11px;
  padding: 3px;
  gap: 1px;
}
.seg-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 6px 16px;
  border-radius: 9px;
  font-size: 12.5px;
  font-weight: 500;
  border: none;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.22,1,0.36,1);
  white-space: nowrap;
  position: relative;
}
.seg-btn:hover:not(.seg-btn--active) { color: var(--text2); background: var(--surface2); }
.seg-btn--active {
  background: var(--grad);
  color: #fff;
  box-shadow: 0 2px 12px var(--accent-glow);
}

.seg-indicator {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--ic, var(--muted));
  opacity: 0.7;
  transition: opacity 0.2s;
  flex-shrink: 0;
}
.seg-btn--active .seg-indicator { background: rgba(255,255,255,0.6); opacity: 1; }

/* ── Priority pills ────────────────────────── */
.prio-row { display: flex; gap: 6px; flex-wrap: wrap; }
.prio-pill {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 6px 13px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--muted);
  cursor: pointer;
  transition: all 0.18s;
  white-space: nowrap;
}
.prio-pill:hover:not(.prio-pill--active) {
  border-color: var(--border2);
  color: var(--text2);
  background: var(--surface2);
}
.prio-pill--active {
  background: var(--surface2);
  border-color: var(--pc);
  color: var(--pc);
  box-shadow: 0 0 0 1px var(--pc), 0 0 14px var(--pg);
}
.prio-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 0 4px currentColor;
}
.prio-pill--active .prio-dot { box-shadow: 0 0 8px var(--pc); }

/* ── Result bar ────────────────────────────── */
.result-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  min-height: 24px;
}
.result-left { display: flex; align-items: baseline; gap: 5px; }
.result-num {
  font-family: var(--font-h);
  font-size: 18px;
  font-weight: 700;
  background: var(--grad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}
.result-text { font-size: 12px; color: var(--muted); }

.clear-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  font-weight: 500;
  color: var(--muted);
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 4px 10px;
  cursor: pointer;
  transition: all 0.15s;
}
.clear-btn:hover { color: var(--danger); border-color: rgba(239,68,68,0.3); background: rgba(239,68,68,0.06); }

.clear-fade-enter-active, .clear-fade-leave-active { transition: opacity 0.18s, transform 0.18s; }
.clear-fade-enter-from, .clear-fade-leave-to { opacity: 0; transform: translateX(8px); }

/* ── States ────────────────────────────────── */
.state-loading {
  display: flex; align-items: center; gap: 10px;
  padding: 36px 0; color: var(--muted); font-size: 13px;
}
.spinner {
  width: 16px; height: 16px;
  border: 2px solid var(--border2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

.state-empty { position: relative; text-align: center; padding: 60px 0; }
.empty-glow {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 180px; height: 180px;
  background: radial-gradient(circle, rgba(0,212,176,0.07) 0%, transparent 70%);
  border-radius: 50%; pointer-events: none;
}
.empty-icon  { font-size: 44px; margin-bottom: 14px; opacity: 0.6; }
.empty-title { font-family: var(--font-h); font-size: 15px; font-weight: 700; color: var(--text2); margin-bottom: 6px; }
.empty-sub   { font-size: 13px; color: var(--muted); }
</style>
