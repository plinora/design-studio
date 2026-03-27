from django.contrib import admin
from .models import Project, Task, Portfolio


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'status', 'deadline', 'created_at']
    list_filter = ['status', 'project_type']
    search_fields = ['title', 'client__username']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'assignee', 'status', 'deadline']
    list_filter = ['status']


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at']
    list_filter = ['category']