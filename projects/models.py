from django.db import models
from django.conf import settings


class Project(models.Model):
    """Модель проекта"""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        IN_PROGRESS = 'in_progress', 'В работе'
        REVIEW = 'review', 'На согласовании'
        COMPLETED = 'completed', 'Завершен'
        CANCELLED = 'cancelled', 'Отменен'

    class ProjectType(models.TextChoices):
        BRANDING = 'branding', 'Брендинг'
        WEB_DESIGN = 'web_design', 'Веб-дизайн'
        PRINT = 'print', 'Полиграфия'
        INTERIOR = 'interior', 'Интерьеры'
        UI_UX = 'ui_ux', 'UI/UX дизайн'
        OTHER = 'other', 'Другое'

    title = models.CharField(max_length=200, verbose_name='Название проекта')
    description = models.TextField(verbose_name='Описание')
    project_type = models.CharField(
        max_length=20,
        choices=ProjectType.choices,
        default=ProjectType.OTHER,
        verbose_name='Тип проекта'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='Статус'
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_projects',
        limit_choices_to={'role': 'client'},
        verbose_name='Клиент'
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_projects',
        limit_choices_to={'role': 'manager'},
        verbose_name='Менеджер'
    )
    designers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='designer_projects',
        limit_choices_to={'role': 'designer'},
        blank=True,
        verbose_name='Дизайнеры'
    )

    start_date = models.DateField(verbose_name='Дата начала')
    deadline = models.DateField(verbose_name='Дедлайн')
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Бюджет')
    references = models.TextField(blank=True, verbose_name='Референсы')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.title


class Task(models.Model):
    """Модель задачи"""

    class Status(models.TextChoices):
        TODO = 'todo', 'К выполнению'
        IN_PROGRESS = 'in_progress', 'В работе'
        REVIEW = 'review', 'На проверке'
        DONE = 'done', 'Выполнено'

    title = models.CharField(max_length=200, verbose_name='Название задачи')
    description = models.TextField(verbose_name='Описание')

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Проект'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_tasks',
        limit_choices_to={'role': 'designer'},
        verbose_name='Исполнитель'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        verbose_name='Статус'
    )

    deadline = models.DateField(verbose_name='Срок выполнения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return self.title


class Portfolio(models.Model):
    """Модель портфолио"""

    class Category(models.TextChoices):
        BRANDING = 'branding', 'Брендинг'
        WEB = 'web', 'Веб-дизайн'
        PRINT = 'print', 'Полиграфия'
        INTERIOR = 'interior', 'Интерьеры'

    title = models.CharField(max_length=200, verbose_name='Название работы')
    description = models.TextField(verbose_name='Описание')
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        verbose_name='Категория'
    )
    image = models.ImageField(upload_to='portfolio/', verbose_name='Изображение')
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='portfolio_items',
        verbose_name='Проект'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Работа в портфолио'
        verbose_name_plural = 'Портфолио'

    def __str__(self):
        return self.title
