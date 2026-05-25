from datetime import date
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer
from .gamification import award_task_completion, revoke_task_completion


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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_status = instance.status
        new_status = request.data.get('status', old_status)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        gamification_data = {'xp_earned': 0, 'xp_subtracted': 0, 'new_badges': []}

        if old_status != 'terminée' and new_status == 'terminée':
            # ── Complétion ──────────────────────────────────────────────────
            # Si la tâche avait déjà des XP (re-complétion après annulation),
            # on les retire d'abord pour repartir proprement
            if instance.xp_awarded > 0:
                revoke_task_completion(instance, request.user)

            serializer.save(completed_at=date.today(), xp_awarded=0)

            result = award_task_completion(serializer.instance, request.user)

            serializer.instance.xp_awarded = result['xp_earned']
            serializer.instance.save(update_fields=['xp_awarded'])

            gamification_data['xp_earned'] = result['xp_earned']
            gamification_data['new_badges'] = result['new_badges']

        elif old_status == 'terminée' and new_status != 'terminée':
            # ── Annulation de complétion ─────────────────────────────────────
            result = revoke_task_completion(instance, request.user)
            serializer.save(completed_at=None, xp_awarded=0)
            gamification_data['xp_subtracted'] = result['xp_subtracted']

        else:
            # ── Changement de statut neutre (ex: à faire → en cours) ─────────
            serializer.save()

        response_data = dict(serializer.data)
        response_data.update(gamification_data)
        return Response(response_data)

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
