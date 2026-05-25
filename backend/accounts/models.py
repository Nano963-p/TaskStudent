from django.db import models
from django.contrib.auth.models import User


BADGE_DEFINITIONS = {
    'organise': {
        'name': 'Organisé',
        'description': '5 tâches terminées',
        'icon': '📋',
        'color': '#00D4B0',
    },
    'rapide': {
        'name': 'Rapide',
        'description': 'Tâche terminée avant la deadline',
        'icon': '⚡',
        'color': '#F59E0B',
    },
    'survivant': {
        'name': 'Survivant',
        'description': 'Tâche terminée le dernier jour',
        'icon': '🔥',
        'color': '#EF4444',
    },
}

LEVEL_THRESHOLDS = [0, 200, 500, 1000, 2000, 3500, 5000]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_xp = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)

    @property
    def level(self):
        for i in range(len(LEVEL_THRESHOLDS) - 1, -1, -1):
            if self.total_xp >= LEVEL_THRESHOLDS[i]:
                return i + 1
        return 1

    @property
    def xp_current_level(self):
        lvl = self.level
        return LEVEL_THRESHOLDS[lvl - 1] if lvl - 1 < len(LEVEL_THRESHOLDS) else 0

    @property
    def xp_next_level(self):
        lvl = self.level
        if lvl < len(LEVEL_THRESHOLDS):
            return LEVEL_THRESHOLDS[lvl]
        return self.total_xp + 1000

    @property
    def xp_progress_pct(self):
        current = self.xp_current_level
        next_lvl = self.xp_next_level
        if next_lvl <= current:
            return 100
        return round((self.total_xp - current) / (next_lvl - current) * 100)

    class Meta:
        verbose_name = 'Profil utilisateur'


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge_key = models.CharField(max_length=50)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge_key')
        verbose_name = 'Badge utilisateur'
