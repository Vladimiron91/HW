from django.contrib import admin
from .models import Task, SubTask, Category


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'deadline', 'created_at', 'is_overdue']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'deadline'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description')
        }),
        ('Статус и сроки', {
            'fields': ('status', 'priority', 'deadline')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task', 'completed', 'created_at']
    list_filter = ['completed', 'created_at']
    search_fields = ['title', 'description', 'task__title']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'task')
        }),
        ('Статус выполнения', {
            'fields': ('completed',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    readonly_fields = ['created_at']