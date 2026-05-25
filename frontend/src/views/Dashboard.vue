<template>
  <div class="dashboard">

    <!-- ── STATS ──────────────────────────── -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-strip stat-strip--warn"></div>
        <div class="stat-icon-wrap stat-icon-wrap--warn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/>
          </svg>
        </div>
        <div class="stat-value" style="color:var(--warn)">{{ store.stats.todo }}</div>
        <div class="stat-name">À faire</div>
        <div class="stat-hint">tâches en attente</div>
      </div>

      <div class="stat-card">
        <div class="stat-strip stat-strip--accent"></div>
        <div class="stat-icon-wrap stat-icon-wrap--accent">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
        </div>
        <div class="stat-value" style="color:var(--accent-light)">{{ store.stats.doing }}</div>
        <div class="stat-name">En cours</div>
        <div class="stat-hint">tâches actives</div>
      </div>

      <div class="stat-card">
        <div class="stat-strip stat-strip--success"></div>
        <div class="stat-icon-wrap stat-icon-wrap--success">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <div class="stat-value" style="color:var(--success)">{{ store.stats.done }}</div>
        <div class="stat-name">Terminées</div>
        <div class="stat-hint">tâches complètes</div>
      </div>
    </div>

    <!-- ── SOON ALERT (≤ 3 jours) ──────────── -->
    <Transition name="alert">
      <div v-if="store.soonDueTasks.length" class="alert-bar alert-bar--warn">
        <span class="alert-pip alert-pip--warn"></span>
        <span class="alert-body">
          <strong>{{ store.soonDueTasks.length }} tâche(s) à rendre dans moins de 3 jours</strong>
          <span class="alert-names alert-names--warn">
            <span v-for="(t, i) in store.soonDueTasks.slice(0, 3)" :key="t.id">
              {{ t.title }}<template v-if="i < Math.min(store.soonDueTasks.length, 3) - 1">, </template>
            </span>
            <span v-if="store.soonDueTasks.length > 3"> +{{ store.soonDueTasks.length - 3 }}</span>
          </span>
        </span>
      </div>
    </Transition>

    <!-- ── OVERDUE ALERT ──────────────────── -->
    <Transition name="alert">
      <div v-if="store.overdueTasks.length" class="alert-bar">
        <span class="alert-pip"></span>
        <span class="alert-body">
          <strong>{{ store.overdueTasks.length }} tâche(s) en retard</strong>
          <span class="alert-names">
            <span v-for="(t, i) in store.overdueTasks.slice(0, 3)" :key="t.id">
              {{ t.title }}<template v-if="i < Math.min(store.overdueTasks.length, 3) - 1">, </template>
            </span>
            <span v-if="store.overdueTasks.length > 3"> +{{ store.overdueTasks.length - 3 }}</span>
          </span>
        </span>
      </div>
    </Transition>

    <!-- ── URGENT ─────────────────────────── -->
    <template v-if="store.urgentTasks.length">
      <div class="section-row">
        <span class="section-dot dot--danger"></span>
        <h2 class="section-title">Tâches urgentes</h2>
        <span class="section-badge badge--danger">{{ store.urgentTasks.length }}</span>
      </div>
      <TaskCard
        v-for="task in store.urgentTasks"
        :key="task.id"
        :task="task"
        @edit="emit('edit', task)"
        @deleted="onDeleted"
        @statusChanged="onStatusChanged"
      />
    </template>

    <!-- ── ACTIVE ─────────────────────────── -->
    <div class="section-row" :style="{ marginTop: store.urgentTasks.length ? '28px' : '4px' }">
      <span class="section-dot dot--accent"></span>
      <h2 class="section-title">Tâches actives</h2>
      <span v-if="activeTasks.length" class="section-count">{{ activeTasks.length }} affichée(s)</span>
    </div>

    <div v-if="store.loading" class="state-loading">
      <div class="spinner"></div>
      <span>Chargement...</span>
    </div>

    <template v-else-if="activeTasks.length">
      <TaskCard
        v-for="task in activeTasks"
        :key="task.id"
        :task="task"
        @edit="emit('edit', task)"
        @deleted="onDeleted"
        @statusChanged="onStatusChanged"
      />
    </template>

    <div v-else class="state-empty">
      <div class="empty-glow"></div>
      <div class="empty-icon">📭</div>
      <p class="empty-title">Aucune tâche active</p>
      <p class="empty-sub">Créez votre première tâche pour commencer</p>
    </div>

  </div>
</template>

<script setup>
import { computed, inject } from 'vue'
import { useTaskStore } from '../store/taskStore'
import TaskCard from '../components/TaskCard.vue'

const store = useTaskStore()
const showToast = inject('showToast')
const emit = defineEmits(['edit'])

const activeTasks = computed(() =>
  store.tasks.filter(t => t.status !== 'terminée').slice(0, 7)
)

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
.dashboard { display: flex; flex-direction: column; }

/* ── Stats ─────────────────────────────────── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 18px;
}
.stat-card {
  position: relative;
  overflow: hidden;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 20px 18px;
  transition: border-color 0.2s, transform 0.2s;
}
.stat-card:hover { border-color: var(--border2); transform: translateY(-2px); }

.stat-strip {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
}
.stat-strip--warn    { background: linear-gradient(90deg, var(--warn), #fbbf24); }
.stat-strip--accent  { background: linear-gradient(90deg, var(--accent), var(--pink)); }
.stat-strip--success { background: linear-gradient(90deg, var(--success), #34d399); }

.stat-icon-wrap {
  width: 34px; height: 34px;
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 16px;
}
.stat-icon-wrap svg { width: 15px; height: 15px; }
.stat-icon-wrap--warn    { background: var(--warn-dim);    color: var(--warn); }
.stat-icon-wrap--accent  { background: var(--accent-dim);  color: var(--accent-light); }
.stat-icon-wrap--success { background: var(--success-dim); color: var(--success); }

.stat-value {
  font-family: var(--font-h);
  font-size: 40px;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 6px;
  letter-spacing: -1px;
}
.stat-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text2);
  margin-bottom: 2px;
}
.stat-hint { font-size: 11px; color: var(--muted); }

/* ── Alert ─────────────────────────────────── */
.alert-bar {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: rgba(239,68,68,0.07);
  border: 1px solid rgba(239,68,68,0.18);
  border-radius: var(--radius-sm);
  padding: 13px 16px;
  margin-bottom: 10px;
  font-size: 12.5px;
  color: #FCA5A5;
}
.alert-bar--warn {
  background: rgba(245,158,11,0.07);
  border-color: rgba(245,158,11,0.20);
  color: var(--warn);
  margin-bottom: 10px;
}
.alert-pip {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--danger);
  box-shadow: 0 0 8px var(--danger-glow);
  flex-shrink: 0;
  margin-top: 4px;
  animation: pulse-dot 1.6s ease-in-out infinite;
}
.alert-pip--warn {
  background: var(--warn);
  box-shadow: 0 0 8px var(--warn-glow);
}
.alert-body { display: flex; flex-direction: column; gap: 3px; }
.alert-names { color: rgba(252,165,165,0.75); font-size: 12px; }
.alert-names--warn { color: rgba(245,158,11,0.75); }

.alert-bar:last-of-type { margin-bottom: 20px; }

.alert-enter-active, .alert-leave-active { transition: all 0.25s ease; }
.alert-enter-from, .alert-leave-to { opacity: 0; transform: translateY(-6px); }

/* ── Section headers ───────────────────────── */
.section-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}
.section-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot--danger { background: var(--danger); box-shadow: 0 0 8px var(--danger-glow); }
.dot--accent { background: var(--accent); box-shadow: 0 0 8px var(--accent-glow); }
.section-title {
  font-family: var(--font-h);
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text2);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  flex: 1;
}
.section-badge {
  font-size: 10px; font-weight: 700;
  padding: 2px 9px; border-radius: 20px;
}
.badge--danger { background: var(--danger-dim); color: var(--danger); }
.section-count { font-size: 11px; color: var(--muted); }

/* ── States ────────────────────────────────── */
.state-loading {
  display: flex; align-items: center; gap: 10px;
  padding: 36px 0;
  color: var(--muted); font-size: 13px;
}
.spinner {
  width: 16px; height: 16px;
  border: 2px solid var(--border2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

.state-empty {
  position: relative;
  text-align: center;
  padding: 60px 0;
}
.empty-glow {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 180px; height: 180px;
  background: radial-gradient(circle, rgba(0,212,176,0.08) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}
.empty-icon { font-size: 44px; margin-bottom: 14px; opacity: 0.65; }
.empty-title {
  font-family: var(--font-h);
  font-size: 15px; font-weight: 700;
  color: var(--text2); margin-bottom: 6px;
}
.empty-sub { font-size: 13px; color: var(--muted); }
</style>
