from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    
    est_urgente = serializers.SerializerMethodField()

    class Meta:
        model  = Task
        fields = '__all__'

    def get_est_urgente(self, obj):
        return obj.est_urgente()