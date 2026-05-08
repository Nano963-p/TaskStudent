from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'priority', 'status', 'deadline', 'created_at']
    list_filter = ['status', 'priority', 'subject']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    list_per_page = 25
