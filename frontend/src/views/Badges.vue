<template>
  <div class="badges-page">

    <!-- XP Hero card -->
    <div class="xp-hero">
      <div class="xp-hero-left">
        <div class="xp-level-ring">
          <span class="xp-level-num">{{ gamification.profile.level }}</span>
        </div>
        <div class="xp-info">
          <p class="xp-label">Niveau {{ gamification.profile.level }}</p>
          <p class="xp-total">{{ gamification.profile.total_xp }} XP total</p>
          <p class="xp-tasks">{{ gamification.profile.tasks_completed }} tâche(s) terminée(s)</p>
        </div>
      </div>
      <div class="xp-progress-wrap">
        <div class="xp-progress-row">
          <span class="xp-progress-label">Progression vers niveau {{ gamification.profile.level + 1 }}</span>
          <span class="xp-progress-pct">{{ gamification.profile.xp_progress_pct }}%</span>
        </div>
        <div class="xp-progress-track">
          <div class="xp-progress-fill" :style="{ width: gamification.profile.xp_progress_pct + '%' }"></div>
        </div>
        <div class="xp-progress-range">
          <span>{{ gamification.profile.xp_current_level }} XP</span>
          <span>{{ gamification.profile.xp_next_level }} XP</span>
        </div>
      </div>
    </div>

    <!-- Badges section -->
    <div class="section-row">
      <span class="section-dot"></span>
      <h2 class="section-title">Badges Study Quest</h2>
      <span class="section-count">{{ earnedCount }}/{{ gamification.profile.badges.length }} débloqués</span>
    </div>

    <div class="badges-grid">
      <div
        v-for="badge in gamification.profile.badges"
        :key="badge.key"
        :class="['badge-card', badge.earned ? 'badge-card--earned' : 'badge-card--locked']"
        :style="badge.earned ? { '--bc': badge.color, '--bg': badge.color + '22' } : {}"
      >
        <!-- Icon -->
        <div class="badge-icon" :class="{ 'badge-icon--locked': !badge.earned }">
          {{ badge.earned ? badge.icon : '🔒' }}
        </div>

        <!-- Info -->
        <div class="badge-info">
          <div class="badge-name-row">
            <p class="badge-name">{{ badge.name }}</p>
            <div v-if="badge.earned" class="badge-check" :style="{ background: badge.color }">✓</div>
          </div>
          <p class="badge-desc">{{ badge.description }}</p>

          <!-- Progress for Organisé -->
          <template v-if="badge.key === 'organise' && !badge.earned && badge.progress">
            <div class="badge-progress">
              <div class="badge-progress-row">
                <span class="badge-progress-label">{{ badge.progress.current }}/{{ badge.progress.target }} tâches terminées</span>
                <span class="badge-progress-pct">{{ Math.round(badge.progress.current / badge.progress.target * 100) }}%</span>
              </div>
              <div class="badge-progress-track">
                <div
                  class="badge-progress-fill fill--organise"
                  :style="{ width: Math.min(100, Math.round(badge.progress.current / badge.progress.target * 100)) + '%' }"
                ></div>
              </div>
            </div>
          </template>

          <!-- Hints for deadline-based badges -->
          <template v-if="(badge.key === 'rapide' || badge.key === 'survivant') && !badge.earned">
            <p class="badge-hint" v-if="badge.key === 'rapide'">
              💡 Terminer une tâche <strong>avant</strong> sa date limite
            </p>
            <p class="badge-hint" v-if="badge.key === 'survivant'">
              💡 Terminer une tâche <strong>le jour même</strong> de sa date limite
            </p>
          </template>

          <p v-if="badge.earned && badge.earned_at" class="badge-date">
            Obtenu le {{ formatDate(badge.earned_at) }}
          </p>
        </div>
      </div>
    </div>

    <!-- XP rules -->
    <div class="section-row" style="margin-top: 28px;">
      <span class="section-dot dot--muted"></span>
      <h2 class="section-title" style="color: var(--muted)">Comment gagner des XP</h2>
    </div>
    <div class="xp-table">
      <div class="xp-row" v-for="row in xpRules" :key="row.label">
        <span class="xp-rule-label">{{ row.label }}</span>
        <span class="xp-rule-val">{{ row.val }}</span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useGamificationStore } from '../store/gamificationStore'

const gamification = useGamificationStore()

onMounted(() => gamification.fetchProfile())

const earnedCount = computed(() =>
  gamification.profile.badges.filter(b => b.earned).length
)

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

const xpRules = [
  { label: 'Tâche terminée (base)', val: '+100 XP' },
  { label: 'Priorité urgente', val: '+100 XP' },
  { label: 'Priorité haute', val: '+50 XP' },
  { label: 'Priorité moyenne', val: '+25 XP' },
  { label: 'Priorité faible', val: '+10 XP' },
  { label: 'Terminée avant la deadline (bonus Rapide)', val: '+50 XP' },
  { label: 'Terminée le jour J de la deadline (bonus Survivant)', val: '+25 XP' },
]
</script>

<style scoped>
.badges-page { display: flex; flex-direction: column; gap: 20px; }

/* XP Hero */
.xp-hero {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px 28px;
  display: flex;
  align-items: center;
  gap: 28px;
}
.xp-hero-left { display: flex; align-items: center; gap: 16px; flex-shrink: 0; }

.xp-level-ring {
  width: 64px; height: 64px;
  border-radius: 50%;
  background: rgba(0,212,176,0.1);
  border: 2px solid rgba(0,212,176,0.4);
  box-shadow: 0 0 20px rgba(0,212,176,0.2);
  display: flex; align-items: center; justify-content: center;
}
.xp-level-num {
  font-size: 26px; font-weight: 800;
  background: linear-gradient(135deg, #00D4B0, #0288C4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.xp-info { display: flex; flex-direction: column; gap: 2px; }
.xp-label { font-size: 15px; font-weight: 700; color: var(--text); }
.xp-total { font-size: 12px; color: var(--accent-light); font-weight: 600; }
.xp-tasks { font-size: 11px; color: var(--muted); }

.xp-progress-wrap { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.xp-progress-row { display: flex; justify-content: space-between; align-items: center; }
.xp-progress-label { font-size: 11.5px; color: var(--muted); }
.xp-progress-pct { font-size: 11.5px; font-weight: 700; color: var(--accent-light); }
.xp-progress-track {
  height: 8px;
  background: var(--surface3);
  border-radius: 8px;
  overflow: hidden;
}
.xp-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00D4B0, #0288C4);
  border-radius: 8px;
  transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1);
  box-shadow: 0 0 10px rgba(0,212,176,0.4);
}
.xp-progress-range { display: flex; justify-content: space-between; font-size: 10px; color: var(--muted); }

/* Section */
.section-row { display: flex; align-items: center; gap: 8px; }
.section-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #00D4B0;
  box-shadow: 0 0 8px rgba(0,212,176,0.5);
  flex-shrink: 0;
}
.dot--muted { background: var(--muted); box-shadow: none; }
.section-title {
  font-size: 12.5px; font-weight: 700;
  color: var(--text2);
  text-transform: uppercase;
  letter-spacing: 0.6px;
  flex: 1;
}
.section-count { font-size: 11px; color: var(--muted); }

/* Badge cards */
.badges-grid { display: flex; flex-direction: column; gap: 10px; }

.badge-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 18px 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  position: relative;
  transition: all 0.2s;
}
.badge-card--earned {
  border-color: var(--bc, rgba(0,212,176,0.3));
  background: var(--bg, rgba(0,212,176,0.05));
  box-shadow: 0 0 24px var(--bg, rgba(0,212,176,0.05));
}
.badge-card--locked { opacity: 0.65; }

.badge-icon {
  font-size: 32px;
  width: 54px; height: 54px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  flex-shrink: 0;
}
.badge-icon--locked { filter: grayscale(1); opacity: 0.4; }

.badge-info { flex: 1; display: flex; flex-direction: column; gap: 5px; }

.badge-name-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.badge-name { font-size: 14px; font-weight: 700; color: var(--text); }
.badge-desc { font-size: 12px; color: var(--text2); }
.badge-hint {
  font-size: 11.5px;
  color: var(--muted);
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 6px;
  padding: 6px 10px;
  margin-top: 2px;
}
.badge-hint strong { color: var(--text2); }
.badge-date { font-size: 10.5px; color: var(--muted); margin-top: 2px; }

.badge-check {
  width: 20px; height: 20px;
  border-radius: 50%;
  color: #fff;
  font-size: 10px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 0 10px currentColor;
}

/* Badge progress bar (Organisé) */
.badge-progress { margin-top: 4px; display: flex; flex-direction: column; gap: 6px; }
.badge-progress-row { display: flex; justify-content: space-between; align-items: center; }
.badge-progress-label { font-size: 11px; color: var(--muted); }
.badge-progress-pct { font-size: 11px; font-weight: 700; color: var(--accent-light); }
.badge-progress-track {
  height: 5px;
  background: var(--surface3);
  border-radius: 5px;
  overflow: hidden;
}
.badge-progress-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.7s cubic-bezier(0.22, 1, 0.36, 1);
}
.fill--organise { background: linear-gradient(90deg, #00D4B0, #0288C4); }

/* XP table */
.xp-table {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  overflow: hidden;
}
.xp-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 11px 18px;
  font-size: 12.5px;
  border-bottom: 1px solid var(--border);
}
.xp-row:last-child { border-bottom: none; }
.xp-rule-label { color: var(--text2); }
.xp-rule-val { font-weight: 700; color: var(--accent-light); }
</style>
