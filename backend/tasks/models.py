from django.db import models


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

    title = models.CharField(max_length=200, verbose_name='Titre')
    subject = models.CharField(
        max_length=100,
        choices=SUBJECT_CHOICES,
        verbose_name='Matière'
    )
    description = models.TextField(blank=True, verbose_name='Description')
    deadline = models.DateField(null=True, blank=True, verbose_name='Date limite')
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='moyenne',
        verbose_name='Priorité'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='à faire',
        verbose_name='Statut'
    )
    completed_at = models.DateField(null=True, blank=True, verbose_name='Terminée le')
    xp_awarded = models.IntegerField(default=0, verbose_name='XP accordés')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créée le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifiée le')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tâche'
        verbose_name_plural = 'Tâches'

    def __str__(self):
        return f"[{self.priority.upper()}] {self.title} — {self.subject}"
