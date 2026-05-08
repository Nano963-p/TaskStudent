<template>
  <div
    :class="['task-card', `p-${task.priority}`]"
    :style="{ '--pc': priorityColor, '--pg': priorityGlow }"
    @mouseenter="hover = true"
    @mouseleave="hover = false; showConfirm = false"
  >

    <!-- Status circle -->
    <button
      :class="['status-circle', `s-${statusKey}`]"
      @click="cycleStatus"
      :title="`Cliquer pour passer à : ${nextStatusLabel}`"
    >
      <span v-if="statusKey === 'done'" class="check">✓</span>
      <span v-else-if="statusKey === 'doing'" class="dot-pulse"></span>
    </button>

    <!-- Body -->
    <div class="card-body">
      <div :class="['card-title', { 'card-title--done': statusKey === 'done' }]">{{ task.title }}</div>
      <div class="card-tags">
        <span class="tag tag-subject">{{ task.subject }}</span>
        <span :class="['tag', `tag-${statusKey}`]">{{ statusLabel }}</span>
        <span v-if="task.priority === 'urgente'" class="tag tag-urgent">URGENT</span>
        <span v-if="task.deadline" :class="['tag', 'tag-date', { 'tag-overdue': task.is_overdue }]">
          {{ task.is_overdue ? '⚠ ' : '📅 ' }}{{ formatDate(task.deadline) }}
        </span>
      </div>
    </div>

    <!-- Hover actions -->
    <Transition name="slide-in">
      <div v-if="hover && !showConfirm" class="card-actions">
        <button class="act-btn act-edit" @click="emit('edit', task)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" width="11" height="11">
            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          Éditer
        </button>
        <button class="act-btn act-delete" @click="showConfirm = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
               stroke-linecap="round" width="12" height="12">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
          </svg>
        </button>
      </div>
    </Transition>

    <!-- Delete confirm -->
    <Transition name="confirm-pop">
      <div v-if="showConfirm" class="delete-confirm">
        <span class="confirm-text">Supprimer ?</span>
        <button class="confirm-yes" @click="doDelete">Oui</button>
        <button class="confirm-no"  @click="showConfirm = false">Non</button>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useTaskStore } from '../store/taskStore'

const props = defineProps({ task: Object })
const emit  = defineEmits(['edit', 'deleted', 'statusChanged'])
const store = useTaskStore()

const hover       = ref(false)
const showConfirm = ref(false)

const CYCLE = { 'à faire': 'en cours', 'en cours': 'terminée', 'terminée': 'à faire' }
const KEY   = { 'à faire': 'todo', 'en cours': 'doing', 'terminée': 'done' }
const LABEL = { 'à faire': 'À faire', 'en cours': 'En cours', 'terminée': 'Terminée' }

const statusKey       = computed(() => KEY[props.task.status])
const statusLabel     = computed(() => LABEL[props.task.status])
const nextStatusLabel = computed(() => LABEL[CYCLE[props.task.status]])

const PCOLORS = { urgente: '#EF4444', haute: '#F59E0B', moyenne: '#00D4B0', faible: '#6A6884' }
const PGLOWS  = { urgente: 'rgba(239,68,68,0.22)', haute: 'rgba(245,158,11,0.18)', moyenne: 'rgba(0,212,176,0.18)', faible: 'transparent' }
const priorityColor = computed(() => PCOLORS[props.task.priority] || '#8B5CF6')
const priorityGlow  = computed(() => PGLOWS[props.task.priority]  || 'transparent')

function formatDate(d) {
  return new Date(d + 'T00:00:00').toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
}

async function cycleStatus() {
  await store.patchTask(props.task.id, { status: CYCLE[props.task.status] })
  emit('statusChanged')
}
async function doDelete() {
  await store.deleteTask(props.task.id)
  emit('deleted')
}
</script>

<style scoped>
.task-card {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 13px 15px;
  margin-bottom: 6px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--pc);
  border-radius: var(--radius-sm);
  position: relative;
  overflow: hidden;
  transition: all 0.22s cubic-bezier(0.22, 1, 0.36, 1);
  cursor: default;
}
.task-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, var(--pg) 0%, transparent 40%);
  opacity: 0;
  transition: opacity 0.22s;
  pointer-events: none;
}
.task-card:hover {
  border-color: var(--border2);
  border-left-color: var(--pc);
  background: var(--surface2);
  transform: translateX(3px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.18);
}
.task-card:hover::before { opacity: 1; }

/* Status circle */
.status-circle {
  width: 20px; height: 20px;
  border-radius: 50%;
  border: 2px solid var(--border2);
  background: transparent;
  flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.18s;
  cursor: pointer;
  position: relative; z-index: 1;
}
.status-circle:hover { border-color: var(--accent); background: var(--accent-dim); }
.s-done { background: var(--success) !important; border-color: var(--success) !important; box-shadow: 0 0 10px var(--success-glow); }
.s-doing { border-color: var(--accent) !important; box-shadow: 0 0 8px var(--accent-glow); }
.check { font-size: 9px; color: #fff; font-weight: 800; }
.dot-pulse {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse-dot 1.6s ease-in-out infinite;
}

/* Body */
.card-body { flex: 1; min-width: 0; position: relative; z-index: 1; }
.card-title {
  font-size: 13.5px; font-weight: 500;
  margin-bottom: 6px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  color: var(--text);
}
.card-title--done { text-decoration: line-through; color: var(--muted); }

/* Tags */
.card-tags { display: flex; gap: 5px; flex-wrap: wrap; align-items: center; }
.tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10.5px; font-weight: 600;
  letter-spacing: 0.15px;
}
.tag-subject  { background: rgba(0,212,176,0.12); color: var(--accent-light); }
.tag-todo     { background: var(--warn-dim);    color: var(--warn); }
.tag-doing    { background: var(--accent-dim);  color: var(--accent-light); }
.tag-done     { background: var(--success-dim); color: var(--success); }
.tag-urgent   { background: var(--danger-dim);  color: var(--danger); font-size: 9.5px; letter-spacing: 0.7px; }
.tag-date     { background: var(--surface3);    color: var(--text2); }
.tag-overdue  { background: var(--danger-dim);  color: #FCA5A5; }

/* Actions */
.card-actions {
  display: flex; gap: 5px;
  flex-shrink: 0;
  position: relative; z-index: 1;
}
.act-btn {
  display: flex; align-items: center; gap: 5px;
  padding: 5px 10px;
  border-radius: var(--radius-xs);
  font-size: 11.5px; font-weight: 500;
  border: 1px solid transparent;
  cursor: pointer; transition: all 0.15s;
}
.act-edit {
  background: var(--accent-dim);
  color: var(--accent-light);
  border-color: rgba(0,212,176,0.2);
}
.act-edit:hover { background: rgba(139,92,246,0.22); }
.act-delete {
  background: var(--danger-dim);
  color: var(--danger);
  border-color: rgba(239,68,68,0.15);
  padding: 5px 8px;
}
.act-delete:hover { background: rgba(239,68,68,0.2); }

/* Delete confirm */
.delete-confirm {
  position: absolute; right: 12px; top: 50%;
  transform: translateY(-50%);
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-radius: var(--radius-sm);
  padding: 8px 12px;
  display: flex; align-items: center; gap: 8px;
  z-index: 20;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
.confirm-text { font-size: 12px; color: var(--text2); white-space: nowrap; }
.confirm-yes, .confirm-no {
  padding: 4px 11px;
  border-radius: 6px;
  font-size: 11px; font-weight: 600;
  border: none; cursor: pointer;
  transition: all 0.15s;
}
.confirm-yes { background: var(--danger); color: #fff; }
.confirm-yes:hover { background: #dc2626; }
.confirm-no  { background: var(--surface3); color: var(--muted); }
.confirm-no:hover  { color: var(--text); }

/* Transitions */
.slide-in-enter-active, .slide-in-leave-active { transition: opacity 0.15s, transform 0.15s; }
.slide-in-enter-from, .slide-in-leave-to { opacity: 0; transform: translateX(8px); }

.confirm-pop-enter-active, .confirm-pop-leave-active { transition: opacity 0.15s, transform 0.15s; }
.confirm-pop-enter-from, .confirm-pop-leave-to { opacity: 0; transform: translateY(-50%) scale(0.94); }
</style>
