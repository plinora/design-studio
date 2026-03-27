from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views
from rest_framework.routers import DefaultRouter
from projects.views import ProjectViewSet, TaskViewSet, PortfolioViewSet

# Создаем роутер для API
router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'portfolio', PortfolioViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('projects/', views.projects_list, name='projects'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('update-task/<int:task_id>/', views.update_task_status, name='update_task_status'),
    path('kanban/', views.kanban, name='kanban'),  # <-- добавить эту строку

    # API маршруты
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)