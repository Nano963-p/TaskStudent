# TaskStudent

Application web de gestion des tâches étudiantes avec système de gamification.  
**Stack :** Django REST Framework (backend) + Vue.js 3 / Vite (frontend)

---

## Structure du projet

```
TaskStudent/
├── backend/                        ← API Django REST
│   ├── taskstudent/                ← Configuration du projet Django
│   │   ├── settings.py             ← Paramètres (JWT, CORS, DRF, BDD)
│   │   └── urls.py                 ← Routes racine
│   ├── accounts/                   ← App authentification & gamification
│   │   ├── models.py               ← UserProfile, UserBadge, BADGE_DEFINITIONS
│   │   ├── views.py                ← register, me, profile
│   │   ├── serializers.py
│   │   └── migrations/
│   ├── tasks/                      ← App tâches
│   │   ├── models.py               ← Modèle Task (+ xp_awarded, completed_at)
│   │   ├── views.py                ← TaskViewSet (CRUD + stats)
│   │   ├── serializers.py
│   │   ├── gamification.py         ← Logique XP & badges
│   │   └── migrations/
│   ├── manage.py
│   └── requirements.txt
└── frontend/                       ← Interface Vue.js 3
    └── src/
        ├── App.vue                 ← Layout (sidebar, topbar, toasts, Pomodoro overlay)
        ├── main.js                 ← Entrée Vue + Pinia + Router
        ├── style.css               ← Variables CSS globales, thème sombre
        ├── router/
        │   └── index.js            ← Routes (guard JWT)
        ├── store/
        │   ├── authStore.js        ← Auth (login, register, token)
        │   ├── taskStore.js        ← CRUD tâches
        │   └── gamificationStore.js← XP, niveau, badges, focus
        ├── services/
        │   ├── authService.js      ← Appels API auth (axios)
        │   └── taskService.js      ← Instance axios (intercepteur JWT)
        ├── views/
        │   ├── Login.vue
        │   ├── Register.vue
        │   ├── Dashboard.vue       ← Tableau de bord (stats cards)
        │   ├── TaskList.vue        ← Liste avec filtres & recherche
        │   └── Badges.vue          ← Profil XP + grille de badges
        └── components/
            ├── TaskCard.vue        ← Carte tâche (statut, actions hover)
            ├── TaskModal.vue       ← Formulaire création / modification
            └── PomodoroTimer.vue   ← Timer Pomodoro (25 min / 5 min)
```

---

## Installation

### Prérequis

- Python 3.10+
- Node.js 18+

### Backend

```bash
cd backend

# Créer et activer l'environnement virtuel
python -m venv ../env
# Windows :
..\env\Scripts\activate
# Linux / macOS :
source ../env/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Créer la base de données
python manage.py migrate

# (Optionnel) Interface d'administration Django
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver
```

> API disponible sur **http://127.0.0.1:8000**

### Frontend

```bash
cd frontend

npm install
npm run dev
```

> Interface disponible sur **http://localhost:5173**

---

## API — Endpoints

### Authentification

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/auth/register/` | Créer un compte |
| POST | `/api/auth/login/` | Connexion → retourne `access` + `refresh` |
| POST | `/api/auth/token/refresh/` | Rafraîchir le token d'accès |
| GET | `/api/auth/me/` | Profil de l'utilisateur connecté |
| GET | `/api/auth/profile/` | XP, niveau, progression, badges |

### Tâches

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/tasks/` | Liste toutes les tâches |
| POST | `/api/tasks/` | Créer une tâche |
| GET | `/api/tasks/{id}/` | Détail d'une tâche |
| PUT | `/api/tasks/{id}/` | Modifier (tous les champs) |
| PATCH | `/api/tasks/{id}/` | Modifier (champs partiels) |
| DELETE | `/api/tasks/{id}/` | Supprimer |
| GET | `/api/tasks/stats/` | Statistiques du tableau de bord |

#### Filtres & recherche

```
GET /api/tasks/?status=à faire
GET /api/tasks/?priority=urgente
GET /api/tasks/?subject=Informatique
GET /api/tasks/?search=algorithme
GET /api/tasks/?ordering=-deadline
```

#### Exemple de corps JSON

```json
{
  "title": "Réviser le chapitre 3",
  "subject": "Algorithmique",
  "description": "Arbres binaires et tri rapide",
  "deadline": "2026-06-15",
  "priority": "urgente",
  "status": "à faire"
}
```

---

## Modèles de données

### Task

| Champ | Type | Détail |
|-------|------|--------|
| `title` | CharField | Min. 3 caractères |
| `subject` | CharField | Matière scolaire |
| `description` | TextField | Optionnel |
| `deadline` | DateField | Optionnel |
| `priority` | CharField | `urgente` · `haute` · `moyenne` · `faible` |
| `status` | CharField | `à faire` · `en cours` · `terminée` |
| `completed_at` | DateField | Auto-rempli à la complétion (lecture seule) |
| `xp_awarded` | IntegerField | XP accordés pour cette tâche (lecture seule) |
| `is_overdue` | Boolean | Calculé — deadline dépassée et non terminée |
| `created_at` | DateTimeField | Auto (lecture seule) |
| `updated_at` | DateTimeField | Auto (lecture seule) |

### UserProfile

| Champ | Type | Détail |
|-------|------|--------|
| `total_xp` | IntegerField | XP total cumulé |
| `tasks_completed` | IntegerField | Nombre de tâches terminées |
| `level` | Property | Calculé depuis `total_xp` |
| `xp_progress_pct` | Property | % de progression vers le niveau suivant |

---

## Système de gamification

### XP — Calcul

Chaque tâche complétée rapporte des XP selon la formule :

```
XP = 100 (base)
   + bonus priorité   → urgente +100 · haute +50 · moyenne +25 · faible +10
   + bonus deadline   → terminée avant la deadline +50 · terminée le jour J +25
```

Les XP sont **flexibles** : si le statut d'une tâche est repassé de `terminée` à un autre statut, les XP accordés sont **retirés** automatiquement. Une re-complétion recalcule les XP depuis zéro.

### Niveaux

| Niveau | XP requis |
|--------|-----------|
| 1 | 0 |
| 2 | 200 |
| 3 | 500 |
| 4 | 1 000 |
| 5 | 2 000 |
| 6 | 3 500 |
| 7 | 5 000 |

### Badges

| Badge | Icône | Condition |
|-------|-------|-----------|
| **Organisé** | 📋 | 5 tâches terminées (compteur en temps réel) |
| **Rapide** | ⚡ | Tâche terminée **avant** sa date limite |
| **Survivant** | 🔥 | Tâche terminée **le jour même** de sa date limite |

> Les badges Rapide et Survivant se déclenchent uniquement si la deadline est **dans le futur ou aujourd'hui** au moment de la complétion. Une deadline passée ne déclenchera pas ces badges.

---

## Fonctionnalités

### Gestion des tâches
- CRUD complet (créer, lire, modifier, supprimer)
- Changement de statut rapide par clic sur le cercle de la carte
- Filtres par statut, priorité, matière
- Recherche par titre / description
- Alertes visuelles : tâches urgentes, en retard (`is_overdue`), deadline proche (J-3)
- Confirmation de suppression inline

### Tableau de bord
- Compteurs en temps réel : total, à faire, en cours, terminées, urgentes
- Barre de progression XP dans la sidebar

### Focus — Timer Pomodoro
- Accessible via le bouton Focus sur chaque carte de tâche
- Cycle : 25 min de travail → 5 min de pause
- Anneau de progression SVG, indicateurs de sessions (4 par cycle)
- Son de fin de phase (AudioContext)
- Overlay plein écran, boutons Start / Pause / Reset / Skip

### Gamification
- Page Badges : profil XP, niveau, progression, grille de badges earned/locked
- Toast lors du déverrouillage d'un badge (icône + nom)
- Toast XP à chaque changement de statut (+XP ou −XP)

### Authentification
- Inscription / Connexion avec JWT (SimpleJWT)
- Token d'accès : 2 h · Refresh : 7 jours (rotation automatique)
- Guard de route côté Vue Router
- Déconnexion avec nettoyage du token

---

## Configuration

### Variables clés — `backend/taskstudent/settings.py`

```python
SECRET_KEY = '...'          # Changer en production
DEBUG = True                # Mettre False en production
ALLOWED_HOSTS = ['*']       # Restreindre en production
CORS_ALLOW_ALL_ORIGINS = True  # Remplacer par CORS_ALLOWED_ORIGINS en production

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

TIME_ZONE = 'Africa/Casablanca'
```

### URL de l'API — `frontend/src/services/taskService.js`

```js
baseURL: 'http://127.0.0.1:8000/api'
```

Modifier si le backend tourne sur un autre port ou domaine.

---

## Commandes utiles

```bash
# Backend — appliquer les migrations
python manage.py migrate

# Backend — créer un superuser pour l'admin (/admin)
python manage.py createsuperuser

# Backend — voir les routes disponibles
python manage.py show_urls   # nécessite django-extensions

# Frontend — build de production
cd frontend && npm run build

# Frontend — aperçu du build
cd frontend && npm run preview
```

---

## Dépendances

### Backend (`requirements.txt`)

| Package | Rôle |
|---------|------|
| `Django` | Framework web |
| `djangorestframework` | API REST |
| `django-cors-headers` | CORS pour le frontend |
| `django-filter` | Filtres sur les querysets |
| `djangorestframework-simplejwt` | Authentification JWT |

### Frontend (`package.json`)

| Package | Rôle |
|---------|------|
| `vue` | Framework UI réactif |
| `vue-router` | Navigation SPA |
| `pinia` | Gestion d'état |
| `axios` | Requêtes HTTP |
| `vite` | Bundler / serveur de dev |
