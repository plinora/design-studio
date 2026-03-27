from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import User as CustomUser
from projects.models import Project, Task


def home(request):

    return render(request, 'home.html')


def register(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        company = request.POST.get('company', '')

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'register.html')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return render(request, 'register.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return render(request, 'register.html')

        # Создаем пользователя с ролью "клиент"
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role='client',  # всегда клиент
            company=company
        )

        login(request, user)
        messages.success(request, f'Добро пожаловать, {username}! Вы зарегистрированы как клиент.')
        return redirect('home')

    return render(request, 'register.html')


@login_required
def projects_list(request):
    """Список проектов"""
    if request.user.is_client:
        projects = Project.objects.filter(client=request.user)
    elif request.user.is_manager:
        projects = Project.objects.filter(manager=request.user)
    elif request.user.is_designer:
        projects = request.user.designer_projects.all()
    else:
        projects = Project.objects.all()

    return render(request, 'projects.html', {'projects': projects})


@login_required
def project_detail(request, project_id):
    """Детали проекта"""
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all()
    return render(request, 'project_detail.html', {'project': project, 'tasks': tasks})


@login_required
def my_tasks(request):
    """Мои задачи (для дизайнера)"""
    if request.user.is_designer:
        tasks = Task.objects.filter(assignee=request.user)
    else:
        tasks = []
    return render(request, 'my_tasks.html', {'tasks': tasks})


@login_required
def update_task_status(request, task_id):
    """Обновление статуса задачи"""
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, assignee=request.user)
        new_status = request.POST.get('status')
        if new_status in ['todo', 'in_progress', 'review']:
            task.status = new_status
            task.save()
            messages.success(request, f'Статус задачи "{task.title}" обновлен')
    return redirect('my_tasks')
@login_required
def kanban(request):
    """Канбан-доска для задач"""
    return render(request, 'kanban.html')
