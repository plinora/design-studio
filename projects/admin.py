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
    from .models import Order, Message, Review

    @admin.register(Order)
    class OrderAdmin(admin.ModelAdmin):
        list_display = ['id', 'client', 'designer', 'service', 'status', 'price', 'created_at']
        list_filter = ['status']

    @admin.register(Message)
    class MessageAdmin(admin.ModelAdmin):
        list_display = ['sender', 'receiver', 'text', 'created_at', 'is_read']
        list_filter = ['is_read']

    @admin.register(Review)
    class ReviewAdmin(admin.ModelAdmin):
        list_display = ['client', 'designer', 'rating', 'text', 'created_at']
        list_filter = ['rating']