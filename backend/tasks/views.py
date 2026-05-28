from datetime import date
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer
from accounts.models import UserProfile

# XP gagnés selon la priorité de la tâche
XP_BASE = 100
XP_PAR_PRIORITE = {
    'urgente': 100,
    'haute': 50,
    'moyenne': 25,
    'faible': 10,
}


def calculer_xp(tache):
    xp = XP_BASE + XP_PAR_PRIORITE.get(tache.priority, 25)
    aujourd_hui = date.today()
    if tache.deadline:
        if aujourd_hui < tache.deadline:
            xp += 50   # bonus si terminée avant la deadline
        elif aujourd_hui == tache.deadline:
            xp += 25   # bonus si terminée le jour même
    return xp


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'subject']
    search_fields = ['title', 'description', 'subject']
    ordering_fields = ['created_at', 'deadline', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        # Chaque utilisateur voit uniquement ses propres tâches
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # La tâche est liée à l'utilisateur connecté
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        tache = self.get_object()
        ancien_statut = tache.status
        nouveau_statut = request.data.get('status', ancien_statut)

        serializer = self.get_serializer(tache, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        xp_gagne = 0
        xp_perdu = 0

        # La tâche passe à "terminée"
        if ancien_statut != 'terminée' and nouveau_statut == 'terminée':
            # Si la tâche avait déjà des XP (re-complétion), on les retire d'abord
            if tache.xp_awarded > 0 and request.user.is_authenticated:
                profil, _ = UserProfile.objects.get_or_create(user=request.user)
                profil.total_xp = max(0, profil.total_xp - tache.xp_awarded)
                profil.tasks_completed = max(0, profil.tasks_completed - 1)
                profil.save()

            serializer.save(completed_at=date.today(), xp_awarded=0)

            if request.user.is_authenticated:
                profil, _ = UserProfile.objects.get_or_create(user=request.user)
                xp_gagne = calculer_xp(serializer.instance)
                profil.total_xp = max(0, profil.total_xp + xp_gagne)
                profil.tasks_completed += 1
                profil.save()

                serializer.instance.xp_awarded = xp_gagne
                serializer.instance.save(update_fields=['xp_awarded'])

        # La tâche quitte le statut "terminée"
        elif ancien_statut == 'terminée' and nouveau_statut != 'terminée':
            if request.user.is_authenticated and tache.xp_awarded > 0:
                profil, _ = UserProfile.objects.get_or_create(user=request.user)
                xp_perdu = tache.xp_awarded
                profil.total_xp = max(0, profil.total_xp - xp_perdu)
                profil.tasks_completed = max(0, profil.tasks_completed - 1)
                profil.save()
            serializer.save(completed_at=None, xp_awarded=0)

        else:
            serializer.save()

        donnees = dict(serializer.data)
        donnees['xp_earned'] = xp_gagne
        donnees['xp_subtracted'] = xp_perdu
        return Response(donnees)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        toutes = Task.objects.filter(user=request.user)
        return Response({
            'total': toutes.count(),
            'todo': toutes.filter(status='à faire').count(),
            'doing': toutes.filter(status='en cours').count(),
            'done': toutes.filter(status='terminée').count(),
            'urgent': toutes.filter(priority='urgente').exclude(status='terminée').count(),
        })
