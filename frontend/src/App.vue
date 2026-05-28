<template>

  <!-- Pages login / register -->
  <template v-if="!auth.isAuthenticated">
    <RouterView/>
  </template>

  <!-- Application principale -->
  <div v-else class="layout">

    <!-- Barre latérale -->
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
        <!-- XP -->
        <div class="xp-block">
          <div class="xp-block-row">
            <div class="xp-level-pill">Niv. {{ gamification.profile.level }}</div>
            <span class="xp-amount">{{ gamification.profile.total_xp }} XP</span>
          </div>
          <div class="xp-track">
            <div class="xp-fill" :style="{ width: gamification.profile.xp_progress_pct + '%' }"></div>
          </div>
        </div>

        <!-- Utilisateur -->
        <div class="user-block">
          <div class="user-avatar">{{ userInitial }}</div>
          <div class="user-info">
            <span class="user-name">{{ auth.user?.username || 'Utilisateur' }}</span>
            <button class="logout-btn" @click="logout">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="13" height="13">
                <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
              Déconnexion
            </button>
          </div>
        </div>

        <div class="progress-block">
          <div class="progress-row">
            <span class="progress-label">Progression globale</span>
            <span class="progress-pct">{{ tauxCompletion }}%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: tauxCompletion + '%' }"></div>
          </div>
        </div>
        <span class="version">v1.2 · TaskStudent</span>
      </div>
    </aside>

    <!-- Contenu principal -->
    <div class="main">
      <header class="topbar">
        <div class="topbar-info">
          <h1 class="topbar-title">{{ titrePage }}</h1>
          <p class="topbar-sub">{{ sousTitrePage }}</p>
        </div>
        <button class="btn-new" @click="ouvrirModal(null)">
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
          <RouterView :key="route.path" @edit="ouvrirModal"/>
        </Transition>
      </main>
    </div>

    <!-- Toast (notification) -->
    <Transition name="toast">
      <div v-if="toast.visible" :class="['toast', `toast--${toast.type}`]">
        <span class="toast-icon">{{ iconeToast }}</span>
        {{ toast.message }}
      </div>
    </Transition>

    <!-- Modal de création/édition de tâche -->
    <TaskModal v-if="modal.ouvert" :task="modal.tache" @close="modal.ouvert = false" @saved="onSaved"/>

    <!-- Timer Pomodoro -->
    <PomodoroTimer
      v-if="gamification.focusedTask"
      :task="gamification.focusedTask"
      @close="gamification.stopFocus()"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, provide, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTaskStore } from './store/taskStore'
import { useAuthStore } from './store/authStore'
import { useGamificationStore } from './store/gamificationStore'
import TaskModal from './components/TaskModal.vue'
import PomodoroTimer from './components/PomodoroTimer.vue'

const route  = useRoute()
const router = useRouter()
const store  = useTaskStore()
const auth   = useAuthStore()
const gamification = useGamificationStore()

// Toast (notification temporaire)
const toast = reactive({ visible: false, message: '', type: 'success' })
let timerToast = null

function afficherToast(message, type = 'success') {
  clearTimeout(timerToast)
  Object.assign(toast, { message, type, visible: true })
  timerToast = setTimeout(() => { toast.visible = false }, 3200)
}
provide('showToast', afficherToast)

const iconeToast = computed(() => {
  if (toast.type === 'success') return '✓'
  if (toast.type === 'badge')   return '🏅'
  return '✕'
})

// Modal
const modal = reactive({ ouvert: false, tache: null })

function ouvrirModal(tache = null) {
  modal.tache = tache || null
  modal.ouvert = true
}

async function onSaved(estEdition) {
  modal.ouvert = false
  await Promise.all([store.fetchTasks(), store.fetchStats()])
  afficherToast(estEdition ? 'Tâche mise à jour ✦' : 'Tâche créée ✦', 'success')
}

// Titre de la page selon la route
const titrePage = computed(() => {
  if (route.path.startsWith('/tasks')) return 'Toutes les tâches'
  return 'Tableau de bord'
})

const sousTitrePage = computed(() => {
  if (route.path.startsWith('/tasks'))
    return `${store.stats.total} tâche(s) enregistrée(s)`
  return `${store.stats.urgent} urgente(s)  ·  ${store.stats.todo} à faire`
})

const tauxCompletion = computed(() => {
  const total = store.stats.total
  if (total === 0) return 0
  return Math.round((store.stats.done / total) * 100)
})

const userInitial = computed(() => {
  const nom = auth.user?.username || 'U'
  return nom.charAt(0).toUpperCase()
})

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  if (auth.isAuthenticated) {
    store.fetchTasks()
    store.fetchStats()
    gamification.fetchProfile()
  }
})
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

/* Barre latérale */
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

.nav-section-label {
  font-size: 9.5px;
  font-weight: 700;
  letter-spacing: 1.4px;
  text-transform: uppercase;
  color: var(--muted);
  padding: 0 8px;
  margin-bottom: 6px;
}

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
}

/* Pied de la sidebar */
.sidebar-footer {
  border-top: 1px solid var(--border);
  padding-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.xp-block {
  background: rgba(0,212,176,0.05);
  border: 1px solid rgba(0,212,176,0.14);
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.xp-block-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.xp-level-pill {
  background: rgba(0,212,176,0.18);
  color: var(--accent-light);
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 9px;
  border-radius: 20px;
}
.xp-amount { font-size: 11px; font-weight: 600; color: var(--text2); }
.xp-track {
  height: 4px;
  background: var(--surface3);
  border-radius: 4px;
  overflow: hidden;
}
.xp-fill {
  height: 100%;
  background: linear-gradient(90deg, #00D4B0, #0288C4);
  border-radius: 4px;
  transition: width 0.7s ease;
}

.user-block {
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: var(--accent-dim);
  border: 1px solid rgba(0,212,176,0.28);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--accent-light);
  flex-shrink: 0;
}
.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}
.user-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.logout-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: var(--muted);
  font-size: 11px;
  padding: 0;
  transition: color 0.15s;
}
.logout-btn:hover { color: #FCA5A5; }

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
  transition: width 0.7s ease;
}
.version { font-size: 10px; color: var(--muted); text-align: center; }

/* Zone principale */
.main {
  flex: 1;
  margin-left: var(--sidebar-w);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

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
  transition: all 0.22s;
  box-shadow: 0 2px 12px var(--accent-glow);
}
.btn-new:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px var(--accent-glow);
}

.content {
  flex: 1;
  padding: 28px 32px;
  max-width: 900px;
}

/* Toast */
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
}
.toast--danger {
  background: rgba(239,68,68,0.11);
  border: 1px solid rgba(239,68,68,0.24);
  color: #FCA5A5;
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

/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.18s, transform 0.18s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(6px); }

.toast-enter-active, .toast-leave-active { transition: opacity 0.22s, transform 0.22s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(12px); }
</style>
