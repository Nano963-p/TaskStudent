from datetime import date
from accounts.models import UserProfile, UserBadge, BADGE_DEFINITIONS

XP_BASE = 100
XP_PRIORITY = {'urgente': 100, 'haute': 50, 'moyenne': 25, 'faible': 10}


def _calculate_xp(task):
    """Calcule les XP à accorder pour une tâche donnée selon son état actuel."""
    xp = XP_BASE + XP_PRIORITY.get(task.priority, 25)
    today = date.today()
    if task.deadline:
        if today < task.deadline:
            xp += 50
        elif today == task.deadline:
            xp += 25
    return xp


def award_task_completion(task, user):
    """Accorde les XP et vérifie les badges quand une tâche passe à terminée."""
    if not user or not user.is_authenticated:
        return {'xp_earned': 0, 'new_badges': []}

    profile, _ = UserProfile.objects.get_or_create(user=user)

    xp = _calculate_xp(task)
    new_badge_keys = []
    today = date.today()

    if task.deadline:
        if today < task.deadline:
            _, created = UserBadge.objects.get_or_create(user=user, badge_key='rapide')
            if created:
                new_badge_keys.append('rapide')
        elif today == task.deadline:
            _, created = UserBadge.objects.get_or_create(user=user, badge_key='survivant')
            if created:
                new_badge_keys.append('survivant')

    profile.total_xp = max(0, profile.total_xp + xp)
    profile.tasks_completed += 1
    profile.save()

    if profile.tasks_completed >= 5:
        _, created = UserBadge.objects.get_or_create(user=user, badge_key='organise')
        if created:
            new_badge_keys.append('organise')

    new_badges = [
        {'key': k, **BADGE_DEFINITIONS[k]}
        for k in new_badge_keys
        if k in BADGE_DEFINITIONS
    ]

    return {'xp_earned': xp, 'new_badges': new_badges}


def revoke_task_completion(task, user):
    """Retire les XP accordés quand une tâche quitte le statut terminée."""
    if not user or not user.is_authenticated:
        return {'xp_subtracted': 0}

    if task.xp_awarded <= 0:
        return {'xp_subtracted': 0}

    profile, _ = UserProfile.objects.get_or_create(user=user)

    xp_to_remove = task.xp_awarded
    profile.total_xp = max(0, profile.total_xp - xp_to_remove)
    profile.tasks_completed = max(0, profile.tasks_completed - 1)
    profile.save()

    return {'xp_subtracted': xp_to_remove}
