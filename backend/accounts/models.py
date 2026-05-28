from django.db import models
from django.contrib.auth.models import User

# XP nécessaires pour passer au niveau suivant
NIVEAUX = [0, 200, 500, 1000, 2000, 3500, 5000]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_xp = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)

    def get_niveau(self):
        niveau = 1
        for i, xp_requis in enumerate(NIVEAUX):
            if self.total_xp >= xp_requis:
                niveau = i + 1
        return niveau

    def get_xp_niveau_actuel(self):
        n = self.get_niveau()
        if n - 1 < len(NIVEAUX):
            return NIVEAUX[n - 1]
        return 0

    def get_xp_prochain_niveau(self):
        n = self.get_niveau()
        if n < len(NIVEAUX):
            return NIVEAUX[n]
        return self.total_xp + 1000

    def get_progression_pct(self):
        actuel = self.get_xp_niveau_actuel()
        prochain = self.get_xp_prochain_niveau()
        if prochain <= actuel:
            return 100
        return round((self.total_xp - actuel) / (prochain - actuel) * 100)
