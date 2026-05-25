<template>
  <div class="pomo-overlay" @click.self="emit('close')">
    <div class="pomo-modal">

      <button class="pomo-close" @click="emit('close')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" width="14" height="14">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>

      <!-- Header -->
      <div class="pomo-header">
        <div class="pomo-mode-badge" :class="phase === 'work' ? 'badge--work' : 'badge--break'">
          {{ phase === 'work' ? '🎯 Focus' : '☕ Pause' }}
        </div>
        <p class="pomo-task-name">{{ task.title }}</p>
        <p class="pomo-session-count">Session {{ sessionCount }} · {{ phase === 'work' ? '25 min travail' : '5 min pause' }}</p>
      </div>

      <!-- Ring timer -->
      <div class="pomo-ring-wrap">
        <svg class="pomo-ring" viewBox="0 0 200 200">
          <circle class="ring-bg" cx="100" cy="100" r="88"/>
          <circle
            class="ring-fill"
            cx="100" cy="100" r="88"
            :stroke="phase === 'work' ? '#00D4B0' : '#F59E0B'"
            :stroke-dashoffset="ringOffset"
          />
        </svg>
        <div class="pomo-time-display">
          <span class="pomo-time">{{ formattedTime }}</span>
          <span class="pomo-time-label">{{ phase === 'work' ? 'travail' : 'pause' }}</span>
        </div>
      </div>

      <!-- Controls -->
      <div class="pomo-controls">
        <button class="pomo-btn pomo-btn--reset" @click="reset" title="Réinitialiser">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" width="16" height="16">
            <polyline points="1 4 1 10 7 10"/>
            <path d="M3.51 15a9 9 0 102.13-9.36L1 10"/>
          </svg>
        </button>

        <button class="pomo-btn pomo-btn--main" @click="toggleTimer">
          <svg v-if="!running" viewBox="0 0 24 24" fill="currentColor" width="22" height="22">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor" width="22" height="22">
            <rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>
          </svg>
        </button>

        <button class="pomo-btn pomo-btn--skip" @click="skip" title="Passer">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" width="16" height="16">
            <polygon points="5 4 15 12 5 20 5 4"/><line x1="19" y1="5" x2="19" y2="19"/>
          </svg>
        </button>
      </div>

      <!-- Sessions dots -->
      <div class="pomo-sessions">
        <span
          v-for="i in 4" :key="i"
          :class="['pomo-dot', { 'pomo-dot--done': i <= completedSessions }]"
        ></span>
        <span class="pomo-sessions-label">pomodoros</span>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, watch } from 'vue'

const props = defineProps({ task: Object })
const emit = defineEmits(['close'])

const WORK_SECS  = 25 * 60
const BREAK_SECS = 5 * 60
const RING_CIRCUM = 2 * Math.PI * 88

const phase            = ref('work')
const timeLeft         = ref(WORK_SECS)
const running          = ref(false)
const sessionCount     = ref(1)
const completedSessions = ref(0)

let interval = null

const formattedTime = computed(() => {
  const m = Math.floor(timeLeft.value / 60).toString().padStart(2, '0')
  const s = (timeLeft.value % 60).toString().padStart(2, '0')
  return `${m}:${s}`
})

const totalSecs = computed(() => phase.value === 'work' ? WORK_SECS : BREAK_SECS)

const ringOffset = computed(() => {
  const pct = timeLeft.value / totalSecs.value
  return RING_CIRCUM * (1 - pct)
})

function toggleTimer() {
  if (running.value) {
    clearInterval(interval)
    running.value = false
  } else {
    running.value = true
    interval = setInterval(tick, 1000)
  }
}

function tick() {
  if (timeLeft.value <= 0) {
    phaseEnd()
    return
  }
  timeLeft.value--
}

function phaseEnd() {
  clearInterval(interval)
  running.value = false
  playBeep()

  if (phase.value === 'work') {
    completedSessions.value++
    phase.value = 'break'
    timeLeft.value = BREAK_SECS
  } else {
    sessionCount.value++
    phase.value = 'work'
    timeLeft.value = WORK_SECS
  }
}

function skip() {
  clearInterval(interval)
  running.value = false
  phaseEnd()
}

function reset() {
  clearInterval(interval)
  running.value = false
  phase.value = 'work'
  timeLeft.value = WORK_SECS
}

function playBeep() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.connect(gain)
    gain.connect(ctx.destination)
    osc.frequency.value = phase.value === 'work' ? 880 : 440
    gain.gain.setValueAtTime(0.4, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.8)
    osc.start(ctx.currentTime)
    osc.stop(ctx.currentTime + 0.8)
  } catch {}
}

onUnmounted(() => clearInterval(interval))
</script>

<style scoped>
.pomo-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.pomo-modal {
  position: relative;
  background: rgba(12, 12, 26, 0.95);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 24px;
  padding: 36px 40px 32px;
  width: 340px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  box-shadow: 0 24px 80px rgba(0,0,0,0.5), 0 0 0 1px rgba(0,212,176,0.06);
}

.pomo-close {
  position: absolute;
  top: 16px; right: 16px;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  color: rgba(255,255,255,0.4);
  width: 30px; height: 30px;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.pomo-close:hover { background: rgba(239,68,68,0.15); color: #FCA5A5; border-color: rgba(239,68,68,0.25); }

/* Header */
.pomo-header { text-align: center; display: flex; flex-direction: column; align-items: center; gap: 8px; }

.pomo-mode-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.3px;
}
.badge--work  { background: rgba(0,212,176,0.15); color: #00D4B0; border: 1px solid rgba(0,212,176,0.25); }
.badge--break { background: rgba(245,158,11,0.15); color: #F59E0B; border: 1px solid rgba(245,158,11,0.25); }

.pomo-task-name {
  font-size: 15px;
  font-weight: 600;
  color: #e2e8f0;
  max-width: 260px;
  text-align: center;
  line-height: 1.4;
}

.pomo-session-count { font-size: 11px; color: rgba(255,255,255,0.35); }

/* Ring */
.pomo-ring-wrap {
  position: relative;
  width: 200px; height: 200px;
}
.pomo-ring {
  width: 200px; height: 200px;
  transform: rotate(-90deg);
}
.ring-bg {
  fill: none;
  stroke: rgba(255,255,255,0.06);
  stroke-width: 10;
}
.ring-fill {
  fill: none;
  stroke-width: 10;
  stroke-linecap: round;
  stroke-dasharray: 553;
  transition: stroke-dashoffset 1s linear, stroke 0.4s;
}
.pomo-time-display {
  position: absolute;
  inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 4px;
}
.pomo-time {
  font-size: 46px;
  font-weight: 800;
  color: #f1f5f9;
  letter-spacing: -2px;
  font-variant-numeric: tabular-nums;
}
.pomo-time-label { font-size: 11px; color: rgba(255,255,255,0.35); text-transform: uppercase; letter-spacing: 1px; }

/* Controls */
.pomo-controls { display: flex; align-items: center; gap: 16px; }

.pomo-btn {
  display: flex; align-items: center; justify-content: center;
  border: none;
  border-radius: 50%;
  transition: all 0.18s;
}
.pomo-btn--reset, .pomo-btn--skip {
  width: 40px; height: 40px;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.5);
}
.pomo-btn--reset:hover, .pomo-btn--skip:hover {
  background: rgba(255,255,255,0.13);
  color: #fff;
}
.pomo-btn--main {
  width: 60px; height: 60px;
  background: linear-gradient(135deg, #00D4B0, #0288C4);
  color: #fff;
  box-shadow: 0 4px 20px rgba(0,212,176,0.35);
}
.pomo-btn--main:hover {
  transform: scale(1.06);
  box-shadow: 0 8px 32px rgba(0,212,176,0.45);
}
.pomo-btn--main:active { transform: scale(0.97); }

/* Session dots */
.pomo-sessions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.pomo-dot {
  width: 9px; height: 9px;
  border-radius: 50%;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.15);
  transition: all 0.3s;
}
.pomo-dot--done {
  background: #00D4B0;
  border-color: rgba(0,212,176,0.4);
  box-shadow: 0 0 8px rgba(0,212,176,0.4);
}
.pomo-sessions-label { font-size: 11px; color: rgba(255,255,255,0.28); margin-left: 4px; }
</style>
