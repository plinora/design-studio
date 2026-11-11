from django.db import models
from django.conf import settings


class Project(models.Model):
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
    project_type = models.CharField(max_length=20, choices=ProjectType.choices, default=ProjectType.OTHER, verbose_name='Тип проекта')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name='Статус')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_projects', limit_choices_to={'role': 'client'}, verbose_name='Клиент')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='managed_projects', limit_choices_to={'role': 'manager'}, verbose_name='Менеджер')
    designers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='designer_projects', limit_choices_to={'role': 'designer'}, blank=True, verbose_name='Дизайнеры')
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
    class Status(models.TextChoices):
        TODO = 'todo', 'К выполнению'
        IN_PROGRESS = 'in_progress', 'В работе'
        REVIEW = 'review', 'На проверке'
        DONE = 'done', 'Выполнено'

    title = models.CharField(max_length=200, verbose_name='Название задачи')
    description = models.TextField(verbose_name='Описание')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', verbose_name='Проект')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks', limit_choices_to={'role': 'designer'}, verbose_name='Исполнитель')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO, verbose_name='Статус')
    deadline = models.DateField(verbose_name='Срок выполнения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return self.title


class Portfolio(models.Model):
    class Category(models.TextChoices):
        BRANDING = 'branding', 'Брендинг'
        WEB = 'web', 'Веб-дизайн'
        PRINT = 'print', 'Полиграфия'
        INTERIOR = 'interior', 'Интерьеры'

    title = models.CharField(max_length=200, verbose_name='Название работы')
    description = models.TextField(verbose_name='Описание')
    category = models.CharField(max_length=20, choices=Category.choices, verbose_name='Категория')
    image = models.ImageField(upload_to='portfolio/', verbose_name='Изображение')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='portfolio_items', verbose_name='Проект')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Работа в портфолио'
        verbose_name_plural = 'Портфолио'

    def __str__(self):
        return self.title


class Service(models.Model):
    SPHERE_CHOICES = [
        ('branding', 'Брендинг'),
        ('web', 'Веб-дизайн'),
        ('graphic', 'Графический дизайн'),
        ('interior', 'Интерьеры'),
        ('other', 'Другое'),
    ]

    designer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='services', limit_choices_to={'role': 'designer'}, verbose_name='Дизайнер')
    title = models.CharField(max_length=200, verbose_name='Название услуги')
    description = models.TextField(verbose_name='Описание')
    sphere = models.CharField(max_length=20, choices=SPHERE_CHOICES, verbose_name='Сфера')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Цена (₽)')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ServiceImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images', verbose_name='Услуга')
    image = models.ImageField(upload_to='services/', verbose_name='Изображение')

    class Meta:
        verbose_name = 'Фото услуги'
        verbose_name_plural = 'Фото услуг'


class Favorite(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites', limit_choices_to={'role': 'client'}, verbose_name='Клиент')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='favorited_by', verbose_name='Услуга')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        unique_together = ['client', 'service']

    def __str__(self):
        return f"{self.client.username} → {self.service.title}"


class Complaint(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='complaints', verbose_name='Услуга')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints', verbose_name='Пользователь (кто пожаловался)')
    reason = models.TextField(verbose_name='Причина жалобы')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата жалобы')
    is_reviewed = models.BooleanField(default=False, verbose_name='Рассмотрено')

    class Meta:
        verbose_name = 'Жалоба'
        verbose_name_plural = 'Жалобы'

    def __str__(self):
        return f"Жалоба на {self.service.title} от {self.user.username}"


class Order(models.Model):
    class Status(models.TextChoices):
        THINKING = 'thinking', 'Думаете над проектом'
        PAID = 'paid', 'Оплачен'
        IN_PROGRESS = 'in_progress', 'В разработке'
        READY = 'ready', 'Готово'
        COMPLETED = 'completed', 'Завершён'
        CANCELLED = 'cancelled', 'Отменён'

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders_client', limit_choices_to={'role': 'client'}, verbose_name='Клиент')
    designer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders_designer', limit_choices_to={'role': 'designer'}, verbose_name='Дизайнер')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name='Услуга')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.THINKING, verbose_name='Статус')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Сумма')
    result = models.TextField(blank=True, verbose_name='Результат работы')
    client_confirmed = models.BooleanField(default=False, verbose_name='Клиент подтвердил')
    designer_confirmed = models.BooleanField(default=False, verbose_name='Дизайнер подтвердил')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Последнее обновление')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} — {self.service.title if self.service else 'Без услуги'}"


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='Отправитель')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages', verbose_name='Получатель')
    text = models.TextField(verbose_name='Текст сообщения')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages', verbose_name='Заказ')
    file = models.FileField(upload_to='chat_files/', blank=True, null=True, verbose_name='Вложение')
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True, verbose_name='Изображение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}: {self.text[:30]}"


class Review(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given', limit_choices_to={'role': 'client'}, verbose_name='Клиент')
    designer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_received', limit_choices_to={'role': 'designer'}, verbose_name='Дизайнер')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='reviews', verbose_name='Заказ')
    rating = models.PositiveSmallIntegerField(verbose_name='Оценка (1–5)')
    text = models.TextField(verbose_name='Текст отзыва')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f"{self.client.username} → {self.designer.username}: {self.rating}★"
class Meta:
    verbose_name = 'Услуга'
    verbose_name_plural = 'Услуги'
    ordering = ['-created_at']

@property
def average_rating(self):
    from django.db.models import Avg
    avg = Review.objects.filter(designer=self.designer).aggregate(Avg('rating'))['rating__avg']
    return round(avg, 1) if avg else 0

def __str__(self):
    return self.title