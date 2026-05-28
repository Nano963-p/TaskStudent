# TaskStudent

Application web de gestion des tâches étudiantes avec système de XP.

**Stack :** Django REST Framework (backend) + Vue.js 3 / Vite (frontend)

---

## Structure du projet

```
TaskStudent/
├── backend/
│   ├── taskstudent/
│   │   ├── settings.py       ← Configuration Django (JWT, CORS, base de données)
│   │   └── urls.py           ← Routes principales
│   ├── accounts/
│   │   ├── models.py         ← UserProfile (XP, niveau)
│   │   ├── views.py          ← register, me, profile
│   │   ├── serializers.py    ← Validation inscription
│   │   ├── urls.py
│   │   └── migrations/
│   ├── tasks/
│   │   ├── models.py         ← Modèle Task
│   │   ├── views.py          ← TaskViewSet (CRUD + stats + XP)
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── migrations/
│   ├── manage.py
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.vue                ← Layout principal (sidebar, topbar, toasts)
        ├── main.js                ← Point d'entrée Vue + Pinia + Router
        ├── style.css              ← Styles globaux et variables CSS
        ├── router/
        │   └── index.js           ← Routes protégées par JWT
        ├── store/
        │   ├── authStore.js       ← Authentification (login, register, token)
        │   ├── taskStore.js       ← Gestion des tâches (CRUD)
        │   └── gamificationStore.js ← XP, niveau, timer focus
        ├── services/
        │   ├── authService.js     ← Appels API d'authentification
        │   └── taskService.js     ← Instance axios avec intercepteur JWT
        ├── views/
        │   ├── Login.vue
        │   ├── Register.vue
        │   ├── Dashboard.vue      ← Tableau de bord avec statistiques
        │   └── TaskList.vue       ← Liste avec filtres et recherche
        └── components/
            ├── TaskCard.vue       ← Carte de tâche (statut, actions)
            ├── TaskModal.vue      ← Formulaire création / modification
            └── PomodoroTimer.vue  ← Timer Pomodoro (25 min / 5 min)
```

---

## Installation

### Prérequis

- Python 3.10+
- Node.js 20+

### Backend

```bash
cd backend

# Créer l'environnement virtuel
python -m venv ../env

# Activer (Windows)
..\env\Scripts\activate

# Activer (Linux / macOS)
source ../env/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Créer la base de données
python manage.py migrate

# Lancer le serveur
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
| POST | `/api/auth/refresh/` | Rafraîchir le token |
| GET | `/api/auth/me/` | Utilisateur connecté |
| GET | `/api/auth/profile/` | XP, niveau, progression |

### Tâches

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/tasks/` | Liste des tâches de l'utilisateur |
| POST | `/api/tasks/` | Créer une tâche |
| GET | `/api/tasks/{id}/` | Détail d'une tâche |
| PUT | `/api/tasks/{id}/` | Modifier une tâche |
| PATCH | `/api/tasks/{id}/` | Modifier partiellement |
| DELETE | `/api/tasks/{id}/` | Supprimer |
| GET | `/api/tasks/stats/` | Statistiques du tableau de bord |

#### Filtres disponibles

```
GET /api/tasks/?status=à faire
GET /api/tasks/?priority=urgente
GET /api/tasks/?search=algorithme
```

#### Exemple de corps JSON

```json
{
  "title": "Réviser le chapitre 3",
  "subject": "Algorithmique",
  "deadline": "2026-06-15",
  "priority": "urgente",
  "status": "à faire"
}
```

---

## Modèles

### Task

| Champ | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey | Propriétaire de la tâche |
| `title` | CharField | Min. 3 caractères |
| `subject` | CharField | Matière scolaire |
| `description` | TextField | Optionnel |
| `deadline` | DateField | Optionnel |
| `priority` | CharField | `urgente` · `haute` · `moyenne` · `faible` |
| `status` | CharField | `à faire` · `en cours` · `terminée` |
| `completed_at` | DateField | Rempli automatiquement à la complétion |
| `xp_awarded` | IntegerField | XP accordés (lecture seule) |
| `is_overdue` | Boolean | Calculé — deadline dépassée et tâche non terminée |

### UserProfile

| Champ | Type | Description |
|-------|------|-------------|
| `total_xp` | IntegerField | XP total cumulé |
| `tasks_completed` | IntegerField | Nombre de tâches terminées |
| `niveau` | Calculé | Déduit du total XP |

---

## Système de XP

Chaque tâche terminée rapporte des XP :

```
XP = 100 (base)
   + bonus priorité  → urgente +100 · haute +50 · moyenne +25 · faible +10
   + bonus deadline  → terminée avant deadline +50 · terminée le jour J +25
```

Si une tâche repasse de `terminée` à un autre statut, les XP sont **retirés**. Une re-complétion recalcule les XP.

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

---

## Fonctionnalités

- **Gestion des tâches** — créer, modifier, supprimer, changer le statut d'un clic
- **Isolation par utilisateur** — chaque utilisateur voit uniquement ses propres tâches
- **Filtres & recherche** — par statut, priorité, matière ou mot-clé
- **Tableau de bord** — statistiques en temps réel (total, à faire, en cours, terminées, urgentes)
- **Alertes visuelles** — tâches en retard et deadlines proches (J-3)
- **Système de XP** — XP gagnés/perdus selon la priorité et la deadline
- **Timer Pomodoro** — 25 min de travail / 5 min de pause, accessible depuis chaque tâche
- **Authentification JWT** — token d'accès 2 h, refresh 7 jours, guard de route

---

## Dépendances

### Backend

| Package | Rôle |
|---------|------|
| `Django` | Framework web |
| `djangorestframework` | API REST |
| `django-cors-headers` | CORS pour le frontend |
| `django-filter` | Filtres sur les querysets |
| `djangorestframework-simplejwt` | Authentification JWT |

### Frontend

| Package | Rôle |
|---------|------|
| `vue` | Framework UI |
| `vue-router` | Navigation SPA |
| `pinia` | Gestion d'état |
| `axios` | Requêtes HTTP |
| `vite` | Serveur de développement / bundler |
