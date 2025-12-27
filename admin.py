from django.contrib import admin
from task_manager.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'deadline', 'created_at', 'is_overdue')
    list_filter = ('status', 'created_at', 'deadline')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'status')
        }),
        ('Временные параметры', {
            'fields': ('deadline', 'created_at', 'updated_at')
        }),
    )