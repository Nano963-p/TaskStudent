from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('urgente', 'Urgente'),
        ('haute', 'Haute'),
        ('moyenne', 'Moyenne'),
        ('faible', 'Faible'),
    ]

    STATUS_CHOICES = [
        ('à faire', 'À faire'),
        ('en cours', 'En cours'),
        ('terminée', 'Terminée'),
    ]

    SUBJECT_CHOICES = [
        ('Informatique', 'Informatique'),
        ('Mathématiques', 'Mathématiques'),
        ('Physique', 'Physique'),
        ('Algorithmique', 'Algorithmique'),
        ('Réseaux', 'Réseaux'),
        ('Bases de données', 'Bases de données'),
        ('Anglais', 'Anglais'),
        ('Français', 'Français'),
        ('Électronique', 'Électronique'),
        ('Gestion', 'Gestion'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100, choices=SUBJECT_CHOICES)
    description = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='moyenne')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='à faire')
    completed_at = models.DateField(null=True, blank=True)
    xp_awarded = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.priority.upper()}] {self.title} — {self.subject}"
