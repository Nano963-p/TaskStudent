from rest_framework import serializers
from .models import Task
from django.utils import timezone


class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'subject', 'description',
            'deadline', 'priority', 'status', 'completed_at', 'xp_awarded',
            'created_at', 'updated_at', 'is_overdue'
        ]
        read_only_fields = ['id', 'completed_at', 'xp_awarded', 'created_at', 'updated_at', 'is_overdue']

    def get_is_overdue(self, obj):
        """Retourne True si la tâche est en retard (deadline dépassée et pas terminée)."""
        if obj.deadline and obj.status != 'terminée':
            return obj.deadline < timezone.now().date()
        return False

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Le titre doit contenir au moins 3 caractères."
            )
        return value.strip()

    def validate_deadline(self, value):
        if value and value < timezone.now().date():
            # On autorise les dates passées (tâches déjà en retard)
            # mais on pourrait lever une erreur ici si souhaité
            pass
        return value
