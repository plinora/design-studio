from rest_framework import serializers
from .models import Project, Task, Portfolio
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'role_display', 'company', 'phone']


class ProjectSerializer(serializers.ModelSerializer):
    """Сериализатор для проекта"""
    client_name = serializers.CharField(source='client.username', read_only=True)
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    designers_names = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_project_type_display', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'project_type', 'type_display',
            'status', 'status_display', 'client', 'client_name',
            'manager', 'manager_name', 'designers', 'designers_names',
            'start_date', 'deadline', 'budget', 'references', 'created_at'
        ]

    def get_designers_names(self, obj):
        return [designer.username for designer in obj.designers.all()]


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задачи"""
    project_title = serializers.CharField(source='project.title', read_only=True)
    assignee_name = serializers.CharField(source='assignee.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'project_title',
            'assignee', 'assignee_name', 'status', 'status_display',
            'deadline', 'created_at'
        ]


class PortfolioSerializer(serializers.ModelSerializer):
    """Сериализатор для портфолио"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Portfolio
        fields = ['id', 'title', 'description', 'category', 'category_display', 'image', 'created_at']