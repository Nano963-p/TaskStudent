from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import UserProfile
from .models import Task


class TaskApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='password123')
        self.other_user = User.objects.create_user(username='other', password='password123')
        self.client.force_authenticate(user=self.user)

    def task_payload(self, **overrides):
        payload = {
            'title': 'Réviser Django',
            'subject': 'Informatique',
            'description': 'Préparer le mini-projet',
            'deadline': (timezone.localdate() + timedelta(days=2)).isoformat(),
            'priority': 'moyenne',
            'status': 'à faire',
        }
        payload.update(overrides)
        return payload

    def test_create_task(self):
        response = self.client.post('/api/tasks/', self.task_payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.first().user, self.user)

    def test_list_only_current_user_tasks(self):
        Task.objects.create(user=self.user, title='Ma tâche', subject='Informatique')
        Task.objects.create(user=self.other_user, title='Tâche cachée', subject='Mathématiques')

        response = self.client.get('/api/tasks/')
        tasks = response.data['results'] if 'results' in response.data else response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['title'], 'Ma tâche')

    def test_reject_past_deadline(self):
        past_date = (timezone.localdate() - timedelta(days=1)).isoformat()

        response = self.client.post(
            '/api/tasks/',
            self.task_payload(deadline=past_date),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('deadline', response.data)

    def test_finish_task_awards_xp_and_updates_profile(self):
        task = Task.objects.create(
            user=self.user,
            title='Projet API',
            subject='Informatique',
            deadline=timezone.localdate() + timedelta(days=1),
            priority='haute',
            status='à faire',
        )

        response = self.client.patch(
            f'/api/tasks/{task.id}/',
            {'status': 'terminée'},
            format='json',
        )
        profile = UserProfile.objects.get(user=self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['xp_earned'], 0)
        self.assertEqual(profile.tasks_completed, 1)
        self.assertEqual(profile.total_xp, response.data['xp_earned'])
