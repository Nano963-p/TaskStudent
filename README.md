# TaskStudent

TaskStudent est une application web de gestion des tâches étudiantes. Elle permet à chaque utilisateur de créer, organiser, modifier, supprimer et terminer ses tâches scolaires, avec un tableau de bord, des filtres, une validation des deadlines et une progression XP dynamique.

Le projet est construit avec un backend Django REST Framework et un frontend Vue.js 3.

## Sommaire

- [Technologies](#technologies)
- [Fonctionnalités](#fonctionnalités)
- [Structure du projet](#structure-du-projet)
- [Installation et lancement](#installation-et-lancement)
- [Tests](#tests)
- [API REST](#api-rest)
- [Modèles principaux](#modèles-principaux)
- [Système XP](#système-xp)
- [Conformité au cahier des charges](#conformité-au-cahier-des-charges)

## Technologies

### Backend

| Technologie | Rôle |
|---|---|
| Django | Framework backend |
| Django REST Framework | Création de l'API REST |
| SimpleJWT | Authentification par JWT |
| django-cors-headers | Communication entre Vue et Django |
| django-filter | Filtrage des tâches |
| SQLite | Base de données locale |

### Frontend

| Technologie | Rôle |
|---|---|
| Vue.js 3 | Interface utilisateur |
| Vite | Serveur de développement et build |
| Pinia | Gestion d'état |
| Vue Router | Navigation SPA |
| Axios | Requêtes HTTP vers l'API |

## Fonctionnalités

- Authentification utilisateur avec JWT.
- Création, lecture, modification et suppression des tâches.
- Bouton `Terminer` pour finaliser une tâche rapidement.
- Calcul automatique des XP lors de la finalisation.
- Barre de progression XP dynamique dans la sidebar.
- Tableau de bord avec statistiques et tâches urgentes.
- Liste complète des tâches avec recherche et filtres.
- Validation des deadlines : impossible de choisir une date avant aujourd'hui.
- Isolation des données : chaque utilisateur voit uniquement ses propres tâches.
- Interface moderne en thème sombre.

## Structure du projet

```text
TaskStudent/
├── backend/
│   ├── accounts/              # Authentification, profil utilisateur, XP
│   ├── tasks/                 # Modèle Task, CRUD, validation, statistiques
│   ├── taskstudent/           # Configuration Django
│   ├── init_db.bat            # Initialisation Windows
│   ├── init_db.sh             # Initialisation Linux/macOS
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/        # TaskModal, TaskCard, PomodoroTimer
│   │   ├── router/            # Routes Vue
│   │   ├── services/          # Services Axios
│   │   ├── store/             # Stores Pinia
│   │   ├── views/             # Login, Register, Dashboard, TaskList
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
└── README.md
```

La structure reste volontairement simple : une partie backend, une partie frontend, deux applications Django principales et des dossiers Vue classiques.

## Installation et lancement

### Prérequis

- Python 3.10 ou plus
- Node.js 20 ou plus
- npm

### 1. Lancer le backend

Ouvrir un terminal dans le dossier du projet, puis exécuter :

```powershell
cd backend
python -m venv ..\env
..\env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

L'API sera disponible sur :

```text
http://127.0.0.1:8000
```

Pour créer un compte administrateur Django :

```powershell
python manage.py createsuperuser
```

### 2. Lancer le frontend

Ouvrir un deuxième terminal, puis exécuter :

```powershell
cd frontend
npm install
npm run dev
```

L'interface sera disponible sur :

```text
http://localhost:5173
```

Important : `npm install` doit être lancé dans `frontend`, pas dans la racine `TaskStudent`, car le fichier `package.json` se trouve dans `frontend`.

### Variables d'environnement optionnelles

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

## Tests

### Backend

```powershell
cd backend
..\env\Scripts\activate
python manage.py test tasks
```

Les tests backend couvrent notamment :

- création d'une tâche ;
- isolation des tâches par utilisateur ;
- refus des deadlines passées ;
- attribution des XP lors de la finalisation.

### Frontend

```powershell
cd frontend
npm run build
```

## API REST

### Authentification

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Créer un compte |
| POST | `/api/auth/login/` | Se connecter et recevoir `access` + `refresh` |
| POST | `/api/auth/refresh/` | Rafraîchir le token d'accès |
| GET | `/api/auth/me/` | Récupérer l'utilisateur connecté |
| GET | `/api/auth/profile/` | Récupérer le profil et la progression XP |

### Tâches

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/api/tasks/` | Lister les tâches de l'utilisateur connecté |
| POST | `/api/tasks/` | Créer une tâche |
| GET | `/api/tasks/{id}/` | Afficher le détail d'une tâche |
| PUT | `/api/tasks/{id}/` | Modifier complètement une tâche |
| PATCH | `/api/tasks/{id}/` | Modifier partiellement une tâche |
| DELETE | `/api/tasks/{id}/` | Supprimer une tâche |
| GET | `/api/tasks/stats/` | Récupérer les statistiques du tableau de bord |

### Filtres disponibles

```http
GET /api/tasks/?status=à faire
GET /api/tasks/?priority=urgente
GET /api/tasks/?subject=Informatique
GET /api/tasks/?search=chapitre
```

### Exemple de création d'une tâche

```json
{
  "title": "Réviser le chapitre 3",
  "subject": "Informatique",
  "description": "Préparer les exercices avant le TP.",
  "deadline": "2026-06-15",
  "priority": "urgente",
  "status": "à faire"
}
```

### Finaliser une tâche

Le bouton `Terminer` du frontend envoie une requête `PATCH` :

```json
{
  "status": "terminée"
}
```

Le backend retourne ensuite les informations de la tâche avec les champs de progression, notamment `xp_earned` ou `xp_subtracted`.

## Modèles principaux

### Task

| Champ | Type | Description |
|---|---|---|
| `user` | ForeignKey | Propriétaire de la tâche |
| `title` | CharField | Titre de la tâche |
| `subject` | CharField | Matière concernée |
| `description` | TextField | Description optionnelle |
| `deadline` | DateField | Date limite |
| `priority` | CharField | `urgente`, `haute`, `moyenne`, `faible` |
| `status` | CharField | `à faire`, `en cours`, `terminée` |
| `completed_at` | DateField | Date de finalisation |
| `xp_awarded` | IntegerField | XP attribués à la tâche |
| `is_overdue` | Boolean | Indique si la tâche est en retard |

### UserProfile

| Champ | Type | Description |
|---|---|---|
| `user` | OneToOneField | Utilisateur associé |
| `total_xp` | IntegerField | XP total cumulé |
| `tasks_completed` | IntegerField | Nombre de tâches terminées |
| `niveau` | Propriété calculée | Niveau actuel |
| `xp_progress_pct` | Propriété calculée | Pourcentage de progression XP |

## Système XP

Chaque tâche terminée rapporte des XP selon la formule suivante :

```text
XP = 100
   + bonus priorité
   + bonus deadline
```

Bonus de priorité :

| Priorité | Bonus |
|---|---:|
| urgente | +100 XP |
| haute | +50 XP |
| moyenne | +25 XP |
| faible | +10 XP |

Bonus de deadline :

| Condition | Bonus |
|---|---:|
| Tâche terminée avant la deadline | +50 XP |
| Tâche terminée le jour de la deadline | +25 XP |
| Tâche terminée après la deadline | +0 XP |

Si une tâche repasse de `terminée` vers un autre statut, les XP associés sont retirés. Si elle est terminée à nouveau, les XP sont recalculés.

## Conformité au cahier des charges

| Exigence | État | Réalisation |
|---|---|---|
| CRUD complet | Respectée | API REST et interface Vue pour gérer les tâches |
| Backend Django REST | Respectée | ViewSet, serializers, routes DRF |
| Frontend Vue.js | Respectée | SPA Vue 3 avec router, composants et stores |
| Requêtes JSON | Respectée | Axios et endpoints REST |
| Validation client/serveur | Respectée | Formulaire Vue + `TaskSerializer` |
| Table dynamique | Respectée | Page `Toutes les tâches` avec recherche et filtres |
| Sécurité | Respectée | JWT, routes protégées, isolation par utilisateur |
| Base de données | Respectée | SQLite, migrations Django, scripts `init_db` |
| Documentation | Respectée | README avec installation, API, tests et modèles |

## Livrables

- Backend Django : `backend/`
- Frontend Vue.js : `frontend/`
- Scripts d'initialisation : `backend/init_db.bat` et `backend/init_db.sh`
- Documentation : `README.md`
- Migrations Django : `backend/accounts/migrations/` et `backend/tasks/migrations/`
- Tests backend : `backend/tasks/tests.py`

## Notes importantes

- Ne pas lancer `npm install` dans la racine du projet.
- Ne pas versionner `env/`, `node_modules/`, `db.sqlite3` ou les fichiers de cache.
- Après un nettoyage du projet, il faut recréer l'environnement Python et réinstaller les dépendances frontend.
- Les deadlines passées sont interdites côté interface et côté API.
