<template>
  <div class="overlay" @click.self="emit('close')">
    <div class="modal">

      <!-- Header -->
      <div class="modal-head">
        <div class="modal-icon">
          <svg viewBox="0 0 24 24" fill="none">
            <rect x="3" y="3" width="18" height="18" rx="4" stroke="url(#mh-grad)" stroke-width="1.8"/>
            <path d="M8 12l3 3 5-5" stroke="url(#mh-grad)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
            <defs>
              <linearGradient id="mh-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#00D4B0"/>
                <stop offset="100%" stop-color="#0288C4"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div class="modal-head-text">
          <h2 class="modal-title">{{ task ? 'Modifier la tâche' : 'Nouvelle tâche' }}</h2>
          <p class="modal-sub">{{ task ? 'Modifier les informations' : 'Ajouter une tâche à votre liste' }}</p>
        </div>
        <button class="btn-close" @click="emit('close')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
               stroke-linecap="round" width="14" height="14">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Body -->
      <div class="modal-body">

        <!-- Title -->
        <div class="field">
          <label class="field-lbl">Titre <span class="req">*</span></label>
          <input
            class="field-inp"
            v-model="form.title"
            placeholder="Ex : Réviser le chapitre 3 d'algorithmique"
            :class="{ 'field-inp--error': errors.title }"
          />
          <span v-if="errors.title" class="field-err">{{ errors.title }}</span>
        </div>

        <div class="field-row">
          <div class="field">
            <label class="field-lbl">Matière <span class="req">*</span></label>
            <select class="field-inp" v-model="form.subject">
              <option v-for="s in SUBJECTS" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div class="field">
            <label class="field-lbl">Date limite</label>
            <input class="field-inp" type="date" v-model="form.deadline" :min="today"/>
            <span v-if="form.deadline && form.deadline < today" class="field-warn">
              ⚠ Date dans le passé — les badges Rapide/Survivant ne se déclencheront pas.
            </span>
          </div>
        </div>

        <!-- Priority selector -->
        <div class="field">
          <label class="field-lbl">Priorité</label>
          <div class="prio-grid">
            <button
              v-for="p in PRIORITIES"
              :key="p.value"
              :class="['prio-btn', { 'prio-btn--active': form.priority === p.value }]"
              :style="form.priority === p.value ? `--pc:${p.color};--pg:${p.glow}` : ''"
              @click="form.priority = p.value"
            >
              <span class="prio-dot" :style="`background:${p.color}`"></span>
              {{ p.label }}
            </button>
          </div>
        </div>

        <!-- Status -->
        <div class="field">
          <label class="field-lbl">Statut</label>
          <div class="status-pills">
            <button
              v-for="s in STATUSES"
              :key="s.value"
              :class="['status-pill', { 'status-pill--active': form.status === s.value }]"
              :style="form.status === s.value ? `--sc:${s.color};--sg:${s.glow}` : ''"
              @click="form.status = s.value"
            >{{ s.label }}</button>
          </div>
        </div>

        <!-- Description -->
        <div class="field">
          <label class="field-lbl">Description <span class="opt">(optionnel)</span></label>
          <textarea
            class="field-inp field-ta"
            v-model="form.description"
            placeholder="Notes, détails, ressources utiles..."
          ></textarea>
        </div>

      </div>

      <!-- Footer -->
      <div class="modal-foot">
        <button class="btn-cancel" @click="emit('close')">Annuler</button>
        <button class="btn-save" :disabled="saving" @click="save">
          <span v-if="saving" class="btn-spinner"></span>
          {{ saving ? 'Enregistrement...' : (task ? 'Sauvegarder' : 'Créer la tâche') }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useTaskStore } from '../store/taskStore'

const today = new Date().toISOString().split('T')[0]

const props = defineProps({ task: Object })
const emit  = defineEmits(['close', 'saved'])
const store = useTaskStore()

const SUBJECTS = [
  'Informatique','Mathématiques','Physique','Algorithmique',
  'Réseaux','Bases de données','Anglais','Français','Électronique','Gestion',
]
const PRIORITIES = [
  { value: 'urgente', label: 'Urgente', color: '#EF4444', glow: 'rgba(239,68,68,0.28)' },
  { value: 'haute',   label: 'Haute',   color: '#F59E0B', glow: 'rgba(245,158,11,0.22)' },
  { value: 'moyenne', label: 'Moyenne', color: '#00D4B0', glow: 'rgba(0,212,176,0.28)' },
  { value: 'faible',  label: 'Faible',  color: '#6A6884', glow: 'rgba(106,104,132,0.18)' },
]
const STATUSES = [
  { value: 'à faire',  label: 'À faire',   color: '#F59E0B', glow: 'rgba(245,158,11,0.22)' },
  { value: 'en cours', label: 'En cours',  color: '#8B5CF6', glow: 'rgba(139,92,246,0.28)' },
  { value: 'terminée', label: 'Terminée',  color: '#10B981', glow: 'rgba(16,185,129,0.25)' },
]

const form = reactive({
  title:       props.task?.title       || '',
  subject:     props.task?.subject     || SUBJECTS[0],
  deadline:    props.task?.deadline    || '',
  priority:    props.task?.priority    || 'moyenne',
  status:      props.task?.status      || 'à faire',
  description: props.task?.description || '',
})

const errors = reactive({})
const saving = ref(false)

function validate() {
  errors.title = form.title.trim().length < 3 ? 'Le titre doit contenir au moins 3 caractères.' : ''
  return !errors.title
}

async function save() {
  if (!validate()) return
  saving.value = true
  try {
    const data = {
      title:       form.title.trim(),
      subject:     form.subject,
      deadline:    form.deadline || null,
      priority:    form.priority,
      status:      form.status,
      description: form.description.trim(),
    }
    if (props.task) await store.updateTask(props.task.id, data)
    else            await store.createTask(data)
    emit('saved', !!props.task)
  } catch (e) {
    const d = e.response?.data
    if (d?.title) errors.title = Array.isArray(d.title) ? d.title[0] : d.title
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* Overlay */
.overlay {
  position: fixed; inset: 0;
  background: rgba(4,4,12,0.78);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000;
  padding: 20px;
}

/* Modal */
.modal {
  background: rgba(11,11,20,0.96);
  border: 1px solid var(--border2);
  border-radius: 20px;
  width: 100%; max-width: 490px;
  max-height: 92vh;
  overflow-y: auto;
  box-shadow:
    0 0 0 1px rgba(0,212,176,0.08),
    0 28px 80px rgba(0,0,0,0.55),
    0 0 60px rgba(0,212,176,0.06);
}

/* Head */
.modal-head {
  display: flex; align-items: flex-start; gap: 12px;
  padding: 22px 22px 18px;
  border-bottom: 1px solid var(--border);
  position: relative;
}
.modal-icon {
  width: 42px; height: 42px;
  background: rgba(0,212,176,0.10);
  border: 1px solid rgba(0,212,176,0.20);
  border-radius: 11px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.modal-icon svg { width: 20px; height: 20px; }
.modal-head-text { flex: 1; }
.modal-title {
  font-family: var(--font-h);
  font-size: 16px; font-weight: 700;
  color: var(--text);
}
.modal-sub { font-size: 12px; color: var(--muted); margin-top: 2px; }
.btn-close {
  width: 28px; height: 28px;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  color: var(--muted);
  transition: all 0.15s;
  flex-shrink: 0;
}
.btn-close:hover { background: var(--surface3); color: var(--text); border-color: var(--border2); }

/* Body */
.modal-body {
  padding: 20px 22px;
  display: flex; flex-direction: column; gap: 15px;
}

/* Fields */
.field { display: flex; flex-direction: column; gap: 7px; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.field-lbl {
  font-size: 10.5px; font-weight: 700;
  color: var(--muted);
  text-transform: uppercase; letter-spacing: 0.7px;
}
.req { color: var(--pink); }
.opt { font-size: 9.5px; color: var(--muted); opacity: 0.7; font-weight: 500; text-transform: none; letter-spacing: 0; }

.field-inp {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border2);
  border-radius: var(--radius-sm);
  padding: 10px 13px;
  color: var(--text);
  font-size: 13.5px;
  outline: none;
  width: 100%;
  transition: all 0.18s;
}
.field-inp:focus {
  border-color: rgba(0,212,176,0.50);
  background: rgba(0,212,176,0.05);
  box-shadow: 0 0 0 3px rgba(0,212,176,0.10);
}
.field-inp--error { border-color: rgba(239,68,68,0.50) !important; }
.field-inp::placeholder { color: var(--muted); }
.field-inp option { background: #0C0C1A; color: var(--text); }
.field-ta { resize: vertical; min-height: 84px; line-height: 1.55; }
.field-err  { font-size: 11px; color: var(--danger); }
.field-warn { font-size: 11px; color: var(--warn); }

/* Priority grid */
.prio-grid { display: flex; gap: 6px; flex-wrap: wrap; }
.prio-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 13px;
  border-radius: var(--radius-xs);
  font-size: 12px; font-weight: 500;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.16s;
}
.prio-btn:hover { border-color: var(--border2); color: var(--text2); }
.prio-btn--active {
  border-color: var(--pc);
  color: var(--pc);
  background: var(--surface2);
  box-shadow: 0 0 0 1px var(--pc), 0 0 16px var(--pg);
}
.prio-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* Status pills */
.status-pills { display: flex; gap: 6px; }
.status-pill {
  flex: 1;
  padding: 8px 12px;
  border-radius: var(--radius-xs);
  font-size: 12px; font-weight: 600;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  text-align: center;
  transition: all 0.16s;
}
.status-pill:hover { border-color: var(--border2); color: var(--text2); }
.status-pill--active {
  border-color: var(--sc);
  color: var(--sc);
  background: var(--surface2);
  box-shadow: 0 0 0 1px var(--sc), 0 0 14px var(--sg);
}

/* Footer */
.modal-foot {
  display: flex; gap: 8px; justify-content: flex-end;
  padding: 16px 22px;
  border-top: 1px solid var(--border);
}
.btn-cancel {
  padding: 9px 20px;
  background: transparent;
  border: 1px solid var(--border2);
  border-radius: var(--radius-sm);
  color: var(--muted);
  font-size: 13px; font-weight: 500;
  transition: all 0.15s;
}
.btn-cancel:hover { color: var(--text); border-color: var(--border3); }

.btn-save {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 24px;
  background: var(--grad);
  border: none;
  border-radius: var(--radius-sm);
  color: #fff;
  font-size: 13px; font-weight: 600;
  letter-spacing: -0.1px;
  transition: all 0.22s;
  box-shadow: 0 2px 12px var(--accent-glow);
}
.btn-save:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px var(--accent-glow);
}
.btn-save:disabled { opacity: 0.58; cursor: not-allowed; }

.btn-spinner {
  width: 13px; height: 13px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
</style>
