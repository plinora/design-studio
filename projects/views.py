from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project, Task, Portfolio
from .serializers import ProjectSerializer, TaskSerializer, PortfolioSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """API для проектов"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Project.objects.all()
        elif user.is_manager:
            return Project.objects.filter(manager=user)
        elif user.is_designer:
            return user.designer_projects.all()
        elif user.is_client:
            return Project.objects.filter(client=user)
        return Project.objects.none()

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Получить все задачи проекта"""
        project = self.get_object()
        tasks = project.tasks.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    """API для задач"""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Task.objects.all()
        elif user.is_designer:
            return Task.objects.filter(assignee=user)
        elif user.is_manager or user.is_client:
            return Task.objects.filter(project__client=user) if user.is_client else Task.objects.filter(
                project__manager=user)
        return Task.objects.none()

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Изменить статус задачи"""
        task = self.get_object()
        new_status = request.data.get('status')
        if new_status in ['todo', 'in_progress', 'review', 'done']:
            task.status = new_status
            task.save()
            return Response({'status': 'ok', 'new_status': task.get_status_display()})
        return Response({'error': 'Неверный статус'}, status=400)


class PortfolioViewSet(viewsets.ModelViewSet):
    """API для портфолио"""
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]