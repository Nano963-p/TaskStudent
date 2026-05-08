<template>
  <div class="layout">

    <!-- ── SIDEBAR ─────────────────────────── -->
    <aside class="sidebar">

      <div class="brand">
        <div class="brand-mark">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="3" width="18" height="18" rx="4" stroke="url(#lg-brand)" stroke-width="1.8"/>
            <path d="M8 12l3 3 5-5" stroke="url(#lg-brand)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
            <defs>
              <linearGradient id="lg-brand" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#00D4B0"/>
                <stop offset="100%" stop-color="#0288C4"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <span class="brand-text">Task<span class="brand-accent">Student</span></span>
      </div>

      <p class="nav-section-label">Navigation</p>

      <nav class="nav">
        <RouterLink to="/dashboard" class="nav-item" active-class="nav-item--active">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="7" height="7" rx="1.5"/>
              <rect x="14" y="3" width="7" height="7" rx="1.5"/>
              <rect x="3" y="14" width="7" height="7" rx="1.5"/>
              <rect x="14" y="14" width="7" height="7" rx="1.5"/>
            </svg>
          </span>
          <span class="nav-label">Tableau de bord</span>
        </RouterLink>

        <RouterLink to="/tasks" class="nav-item" active-class="nav-item--active">
          <span class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 11l3 3 8-8"/>
              <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V6a2 2 0 012-2h9"/>
            </svg>
          </span>
          <span class="nav-label">Toutes les tâches</span>
          <span v-if="store.stats.total" class="nav-count">{{ store.stats.total }}</span>
        </RouterLink>
      </nav>

      <div class="sidebar-footer">
        <div class="progress-block">
          <div class="progress-row">
            <span class="progress-label">Progression globale</span>
            <span class="progress-pct">{{ completionRate }}%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: completionRate + '%' }"></div>
          </div>
        </div>
        <span class="version">v1.0 · TaskStudent</span>
      </div>
    </aside>

    <!-- ── MAIN ───────────────────────────── -->
    <div class="main">
      <header class="topbar">
        <div class="topbar-info">
          <h1 class="topbar-title">{{ pageTitle }}</h1>
          <p class="topbar-sub">{{ pageSub }}</p>
        </div>
        <button class="btn-new" @click="openModal(null)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8"
               stroke-linecap="round" width="13" height="13">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Nouvelle tâche
        </button>
      </header>

      <main class="content">
        <Transition name="fade" mode="out-in">
          <RouterView :key="route.path" @edit="openModal"/>
        </Transition>
      </main>
    </div>

    <!-- ── TOAST ──────────────────────────── -->
    <Transition name="toast">
      <div v-if="toast.visible" :class="['toast', `toast--${toast.type}`]">
        <span class="toast-icon">{{ toast.type === 'success' ? '✓' : '✕' }}</span>
        {{ toast.message }}
      </div>
    </Transition>

    <!-- ── MODAL ──────────────────────────── -->
    <TaskModal v-if="modal.open" :task="modal.task" @close="modal.open = false" @saved="onSaved"/>
  </div>
</template>

<script setup>
import { ref, reactive, computed, provide, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTaskStore } from './store/taskStore'
import TaskModal from './components/TaskModal.vue'

const route = useRoute()
const store = useTaskStore()

const toast = reactive({ visible: false, message: '', type: 'success' })
let toastTimer = null

function showToast(message, type = 'success') {
  clearTimeout(toastTimer)
  Object.assign(toast, { message, type, visible: true })
  toastTimer = setTimeout(() => { toast.visible = false }, 3200)
}
provide('showToast', showToast)

const modal = reactive({ open: false, task: null })
function openModal(task = null) { modal.task = task || null; modal.open = true }

async function onSaved(wasEdit) {
  modal.open = false
  await Promise.all([store.fetchTasks(), store.fetchStats()])
  showToast(wasEdit ? 'Tâche mise à jour ✦' : 'Tâche créée ✦', 'success')
}

const pageTitle = computed(() => route.path.startsWith('/tasks') ? 'Toutes les tâches' : 'Tableau de bord')
const pageSub   = computed(() => route.path.startsWith('/tasks')
  ? `${store.stats.total} tâche(s) enregistrée(s)`
  : `${store.stats.urgent} urgente(s)  ·  ${store.stats.todo} à faire`)

const completionRate = computed(() => {
  const t = store.stats.total
  return t ? Math.round((store.stats.done / t) * 100) : 0
})

onMounted(() => {
  store.fetchTasks()
  store.fetchStats()
})
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

/* ── SIDEBAR ─────────────────────────────────── */
.sidebar {
  width: var(--sidebar-w);
  flex-shrink: 0;
  position: fixed;
  top: 0; left: 0;
  height: 100vh;
  z-index: 200;
  display: flex;
  flex-direction: column;
  padding: 22px 14px;
  background: rgba(8, 8, 18, 0.80);
  border-right: 1px solid var(--border);
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
}

/* Brand */
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 6px 20px;
  margin-bottom: 18px;
  border-bottom: 1px solid var(--border);
}
.brand-mark {
  width: 36px; height: 36px;
  background: rgba(0,212,176,0.10);
  border: 1px solid rgba(0,212,176,0.22);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.brand-mark svg { width: 18px; height: 18px; }
.brand-text {
  font-family: var(--font-h);
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.2px;
}
.brand-accent {
  background: var(--grad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Section label */
.nav-section-label {
  font-size: 9.5px;
  font-weight: 700;
  letter-spacing: 1.4px;
  text-transform: uppercase;
  color: var(--muted);
  padding: 0 8px;
  margin-bottom: 6px;
}

/* Nav */
.nav {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  color: var(--muted);
  font-size: 13.5px;
  font-weight: 500;
  transition: all 0.18s;
}
.nav-item:hover { background: var(--surface2); color: var(--text2); }
.nav-item--active {
  background: rgba(0,212,176,0.11) !important;
  border-color: rgba(0,212,176,0.22) !important;
  color: var(--accent-light) !important;
}
.nav-icon {
  width: 16px; height: 16px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.nav-icon svg { width: 16px; height: 16px; }
.nav-label { flex: 1; }
.nav-count {
  background: rgba(0,212,176,0.16);
  color: var(--accent-light);
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 20px;
  letter-spacing: 0.2px;
}

/* Footer */
.sidebar-footer {
  border-top: 1px solid var(--border);
  padding-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.progress-block { display: flex; flex-direction: column; gap: 7px; }
.progress-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.progress-label { font-size: 11px; color: var(--muted); }
.progress-pct { font-size: 11px; font-weight: 700; color: var(--accent-light); }
.progress-track {
  height: 4px;
  background: var(--surface3);
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: var(--grad);
  border-radius: 4px;
  transition: width 0.7s cubic-bezier(0.22, 1, 0.36, 1);
  box-shadow: 0 0 8px var(--accent-glow);
}
.version { font-size: 10px; color: var(--muted); text-align: center; }

/* ── MAIN ────────────────────────────────────── */
.main {
  flex: 1;
  margin-left: var(--sidebar-w);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Topbar */
.topbar {
  position: sticky;
  top: 0; z-index: 100;
  height: var(--topbar-h);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  background: rgba(7,7,15,0.82);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
}
.topbar-title {
  font-family: var(--font-h);
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.4px;
}
.topbar-sub {
  font-size: 12px;
  color: var(--muted);
  margin-top: 2px;
}

/* New task button */
.btn-new {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--grad);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: -0.1px;
  transition: all 0.22s;
  box-shadow: 0 2px 12px var(--accent-glow);
}
.btn-new:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px var(--accent-glow), 0 2px 8px var(--pink-glow);
}
.btn-new:active { transform: translateY(0); }

/* Page content */
.content {
  flex: 1;
  padding: 28px 32px;
  max-width: 900px;
}

/* ── TOAST ───────────────────────────────────── */
.toast {
  position: fixed;
  bottom: 28px; right: 28px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  z-index: 3000;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
.toast--success {
  background: rgba(16,185,129,0.11);
  border: 1px solid rgba(16,185,129,0.24);
  color: #6EE7B7;
  box-shadow: 0 4px 24px rgba(16,185,129,0.14);
}
.toast--danger {
  background: rgba(239,68,68,0.11);
  border: 1px solid rgba(239,68,68,0.24);
  color: #FCA5A5;
  box-shadow: 0 4px 24px rgba(239,68,68,0.14);
}
.toast-icon {
  width: 18px; height: 18px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 9px; font-weight: 800;
  flex-shrink: 0;
}
.toast--success .toast-icon { background: rgba(16,185,129,0.22); color: var(--success); }
.toast--danger  .toast-icon { background: rgba(239,68,68,0.22);  color: var(--danger); }
</style>
