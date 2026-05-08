from rest_framework import viewsets, filters
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset         = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ['titre', 'matiere']
    ordering_fields  = ['date_limite', 'priorite']