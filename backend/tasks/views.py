from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD complet pour les tâches étudiantes.

    Endpoints disponibles :
      GET    /api/tasks/           — Liste toutes les tâches
      POST   /api/tasks/           — Crée une nouvelle tâche
      GET    /api/tasks/{id}/      — Détail d'une tâche
      PUT    /api/tasks/{id}/      — Modifie une tâche (tous les champs)
      PATCH  /api/tasks/{id}/      — Modifie une tâche (champs partiels)
      DELETE /api/tasks/{id}/      — Supprime une tâche
      GET    /api/tasks/stats/     — Statistiques du tableau de bord
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'subject']
    search_fields = ['title', 'description', 'subject']
    ordering_fields = ['created_at', 'deadline', 'priority']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Retourne les statistiques pour le tableau de bord."""
        qs = Task.objects.all()
        data = {
            'total': qs.count(),
            'todo': qs.filter(status='à faire').count(),
            'doing': qs.filter(status='en cours').count(),
            'done': qs.filter(status='terminée').count(),
            'urgent': qs.filter(priority='urgente').exclude(status='terminée').count(),
        }
        return Response(data)
