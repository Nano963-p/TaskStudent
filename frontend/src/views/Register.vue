<template>
  <div class="auth-page">
    <div class="auth-card">

      <!-- Brand -->
      <div class="auth-brand">
        <div class="brand-mark">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="3" width="18" height="18" rx="4" stroke="url(#lg-reg)" stroke-width="1.8"/>
            <path d="M8 12l3 3 5-5" stroke="url(#lg-reg)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
            <defs>
              <linearGradient id="lg-reg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#00D4B0"/>
                <stop offset="100%" stop-color="#0288C4"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
        <span class="brand-text">Task<span class="brand-accent">Student</span></span>
      </div>

      <h2 class="auth-title">Créer un compte</h2>
      <p class="auth-sub">Rejoignez TaskStudent et organisez vos études</p>

      <form @submit.prevent="submit" class="auth-form">
        <div class="field">
          <label class="field-label">Nom d'utilisateur</label>
          <input
            v-model="form.username"
            type="text"
            class="field-input"
            :class="{ 'field-input--err': errors.username }"
            placeholder="votre_nom"
            required
            autocomplete="username"
          />
          <span v-if="errors.username" class="field-err">{{ errors.username }}</span>
        </div>

        <div class="field">
          <label class="field-label">Adresse e-mail <span class="optional">(optionnel)</span></label>
          <input
            v-model="form.email"
            type="email"
            class="field-input"
            placeholder="vous@exemple.com"
            autocomplete="email"
          />
        </div>

        <div class="field">
          <label class="field-label">Mot de passe</label>
          <div class="input-wrap">
            <input
              v-model="form.password"
              :type="showPwd ? 'text' : 'password'"
              class="field-input"
              :class="{ 'field-input--err': errors.password }"
              placeholder="6 caractères minimum"
              required
              autocomplete="new-password"
            />
            <button type="button" class="eye-btn" @click="showPwd = !showPwd" tabindex="-1">
              <svg v-if="!showPwd" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
          <span v-if="errors.password" class="field-err">{{ errors.password }}</span>
        </div>

        <div class="field">
          <label class="field-label">Confirmer le mot de passe</label>
          <div class="input-wrap">
            <input
              v-model="form.password2"
              :type="showPwd2 ? 'text' : 'password'"
              class="field-input"
              :class="{ 'field-input--err': errors.password2 }"
              placeholder="••••••••"
              required
              autocomplete="new-password"
            />
            <button type="button" class="eye-btn" @click="showPwd2 = !showPwd2" tabindex="-1">
              <svg v-if="!showPwd2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
          <span v-if="errors.password2" class="field-err">{{ errors.password2 }}</span>
        </div>

        <p v-if="globalError" class="auth-error">{{ globalError }}</p>

        <button type="submit" class="btn-submit" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Créer le compte</span>
        </button>
      </form>

      <p class="auth-switch">
        Déjà un compte ?
        <RouterLink to="/login" class="auth-link">Se connecter</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/authStore'

const router      = useRouter()
const auth        = useAuthStore()
const form        = reactive({ username: '', email: '', password: '', password2: '' })
const errors      = reactive({})
const globalError = ref('')
const loading     = ref(false)
const showPwd     = ref(false)
const showPwd2    = ref(false)

async function submit() {
  Object.keys(errors).forEach(k => delete errors[k])
  globalError.value = ''
  loading.value = true
  try {
    await auth.register(form)
    router.push('/dashboard')
  } catch (e) {
    const data = e.response?.data
    if (data && typeof data === 'object') {
      Object.assign(errors, data)
      if (data.non_field_errors) globalError.value = data.non_field_errors[0]
    } else {
      globalError.value = 'Une erreur est survenue. Veuillez réessayer.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  position: relative;
  z-index: 1;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: rgba(12, 19, 32, 0.85);
  border: 1px solid var(--border2);
  border-radius: 20px;
  padding: 40px 36px;
  backdrop-filter: blur(32px);
  -webkit-backdrop-filter: blur(32px);
  box-shadow: 0 24px 80px rgba(0,0,0,0.40), 0 0 0 1px rgba(0,212,176,0.06);
  animation: fadeUp 0.32s cubic-bezier(0.22, 1, 0.36, 1);
}

.auth-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 28px;
}
.brand-mark {
  width: 36px; height: 36px;
  background: rgba(0,212,176,0.10);
  border: 1px solid rgba(0,212,176,0.22);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}
.brand-mark svg { width: 18px; height: 18px; }
.brand-text {
  font-family: var(--font-h);
  font-size: 18px;
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

.auth-title {
  font-family: var(--font-h);
  font-size: 24px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.5px;
  margin-bottom: 4px;
}
.auth-sub {
  font-size: 13px;
  color: var(--muted);
  margin-bottom: 28px;
}

.auth-form { display: flex; flex-direction: column; gap: 16px; }

.field { display: flex; flex-direction: column; gap: 6px; }
.field-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text2);
  letter-spacing: 0.2px;
}
.optional { color: var(--muted); font-weight: 400; }

.input-wrap { position: relative; }
.field-input {
  width: 100%;
  padding: 11px 14px;
  background: var(--surface2);
  border: 1px solid var(--border2);
  border-radius: var(--radius-sm);
  color: var(--text);
  font-size: 14px;
  outline: none;
  transition: border-color 0.18s, box-shadow 0.18s;
}
.input-wrap .field-input { padding-right: 42px; }
.field-input::placeholder { color: var(--muted); }
.field-input:focus {
  border-color: rgba(0,212,176,0.45);
  box-shadow: 0 0 0 3px rgba(0,212,176,0.10);
}
.field-input--err {
  border-color: rgba(239,68,68,0.50) !important;
}
.field-err {
  font-size: 11.5px;
  color: #FCA5A5;
}

.eye-btn {
  position: absolute;
  right: 12px; top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--muted);
  display: flex; align-items: center;
  padding: 4px;
  transition: color 0.15s;
}
.eye-btn:hover { color: var(--text2); }
.eye-btn svg { width: 16px; height: 16px; }

.auth-error {
  font-size: 12.5px;
  color: #FCA5A5;
  background: rgba(239,68,68,0.10);
  border: 1px solid rgba(239,68,68,0.22);
  border-radius: var(--radius-xs);
  padding: 9px 12px;
}

.btn-submit {
  width: 100%;
  padding: 12px;
  background: var(--grad);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: -0.1px;
  box-shadow: 0 2px 14px var(--accent-glow);
  transition: all 0.22s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 4px;
}
.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px var(--accent-glow);
}
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.auth-switch {
  text-align: center;
  font-size: 13px;
  color: var(--muted);
  margin-top: 22px;
}
.auth-link {
  color: var(--accent-light);
  font-weight: 600;
  margin-left: 4px;
  transition: opacity 0.15s;
}
.auth-link:hover { opacity: 0.8; }
</style>
