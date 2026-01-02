"""
Дополнительные endpoint для статистики (не требуется в задании).
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from task_manager.models import Category, Task


@api_view(['GET'])
def category_stats(request):
    """
    Статистика по категориям.
    """
    # Активные категории с количеством задач
    categories_stats = Category.objects.annotate(
        task_count=Count('tasks')
    ).values('id', 'name', 'task_count')

    # Удалённые категории
    deleted_count = Category.all_objects.filter(is_deleted=True).count()

    # Всего задач
    total_tasks = Task.objects.count()
    tasks_without_category = Task.objects.filter(category__isnull=True).count()

    return Response({
        'total_categories': Category.objects.count(),
        'deleted_categories': deleted_count,
        'total_tasks': total_tasks,
        'tasks_without_category': tasks_without_category,
        'categories_with_stats': list(categories_stats)
    })