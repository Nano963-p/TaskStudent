# TaskStudent 🎓

Application web CRUD de gestion des tâches étudiantes — Django REST Framework + Vue.js 3.

---

## Architecture

```
taskstudent/
├── backend/              ← Django + DRF
│   ├── taskstudent/      ← Config du projet (settings, urls)
│   ├── tasks/            ← App Django (model, serializer, views, urls)
│   ├── manage.py
│   └── requirements.txt
└── frontend/             ← Vue.js 3 (Vite)
    └── src/
        ├── App.vue           ← Layout principal (sidebar, topbar, toast)
        ├── router/           ← Vue Router
        ├── store/            ← Pinia (état global des tâches)
        ├── services/         ← Axios (appels API)
        ├── views/
        │   ├── Dashboard.vue ← Tableau de bord
        │   └── TaskList.vue  ← Liste avec filtres
        └── components/
            ├── TaskCard.vue  ← Carte d'une tâche
            └── TaskModal.vue ← Formulaire ajout/modification
```

---

## Installation

### Backend Django

```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows

# Installer les dépendances
pip install -r requirements.txt

# Créer la base de données
python manage.py makemigrations
python manage.py migrate

# (Optionnel) Créer un superuser pour l'admin
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

Le backend sera disponible sur : http://127.0.0.1:8000

### Frontend Vue.js

```bash
cd frontend

npm install
npm run dev
```

Le frontend sera disponible sur : http://localhost:5173

---

## API Endpoints

| Méthode | URL                   | Description                        |
|---------|-----------------------|------------------------------------|
| GET     | /api/tasks/           | Liste toutes les tâches            |
| POST    | /api/tasks/           | Créer une nouvelle tâche           |
| GET     | /api/tasks/{id}/      | Détail d'une tâche                 |
| PUT     | /api/tasks/{id}/      | Modifier une tâche (complet)       |
| PATCH   | /api/tasks/{id}/      | Modifier une tâche (partiel)       |
| DELETE  | /api/tasks/{id}/      | Supprimer une tâche                |
| GET     | /api/tasks/stats/     | Statistiques (dashboard)           |

### Filtres disponibles (query params)

```
GET /api/tasks/?status=à+faire
GET /api/tasks/?priority=urgente
GET /api/tasks/?subject=Informatique
GET /api/tasks/?search=algorithmique
GET /api/tasks/?ordering=-deadline
```

### Exemple de corps JSON (POST/PUT)

```json
{
  "title": "Réviser algorithmique",
  "subject": "Algorithmique",
  "description": "Revoir tri rapide et arbres binaires",
  "deadline": "2026-05-10",
  "priority": "urgente",
  "status": "à faire"
}
```

---

## Modèle de données

| Champ        | Type        | Valeurs possibles                                                   |
|--------------|-------------|---------------------------------------------------------------------|
| title        | CharField   | Texte libre (min. 3 caractères)                                     |
| subject      | CharField   | Informatique, Mathématiques, Physique, Algorithmique, Réseaux, ...  |
| description  | TextField   | Texte libre (optionnel)                                             |
| deadline     | DateField   | Date ISO (optionnel)                                                |
| priority     | CharField   | urgente, haute, moyenne, faible                                     |
| status       | CharField   | à faire, en cours, terminée                                         |
| created_at   | DateTimeField | Auto (lecture seule)                                              |
| updated_at   | DateTimeField | Auto (lecture seule)                                              |
| is_overdue   | Boolean     | Calculé (lecture seule) — True si deadline dépassée et non terminée |

---

## Fonctionnalités

- ✅ CRUD complet (Créer, Lire, Modifier, Supprimer)
- ✅ Filtres par statut, priorité, matière
- ✅ Recherche par titre ou matière
- ✅ Tableau de bord avec statistiques
- ✅ Alertes tâches urgentes et en retard
- ✅ Changement de statut rapide (clic sur le cercle)
- ✅ Validation côté client (Vue) et serveur (Django)
- ✅ Notifications toast
- ✅ Interface responsive et moderne
