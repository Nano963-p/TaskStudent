from django.db import models


class Task(models.Model):

    PRIORITE_CHOICES = [
        ('faible',  'Faible'),
        ('moyenne', 'Moyenne'),
        ('elevee',  'Élevée'),
    ]

    STATUT_CHOICES = [
        ('a_faire',  'À faire'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
    ]

    titre       = models.CharField(max_length=200)
    matiere     = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date_limite = models.DateField()
    priorite    = models.CharField(
                      max_length=10,
                      choices=PRIORITE_CHOICES,
                      default='moyenne'
                  )
    statut      = models.CharField(
                      max_length=10,
                      choices=STATUT_CHOICES,
                      default='a_faire'
                  )
    cree_le     = models.DateTimeField(auto_now_add=True)
    modifie_le  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titre} ({self.matiere})"

    def est_urgente(self):
        from datetime import date
        if self.date_limite:
            delta = self.date_limite - date.today()
            return delta.days <= 3
        return False

    class Meta:
        ordering        = ['date_limite', '-priorite']
        verbose_name    = 'Tâche'
        verbose_name_plural = 'Tâches'