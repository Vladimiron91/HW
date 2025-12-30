"""
Домашнее задание: Замена функций представлений на Generic Views для задач и подзадач
Используя Generic Views, замените существующие классы представлений для задач (Tasks) и подзадач (SubTasks)
на соответствующие классы для полного CRUD (Create, Read, Update, Delete) функционала.
"""

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from task_manager.models import Task, SubTask
from .serializers import TaskSerializer, TaskCreateSerializer, SubTaskSerializer, SubTaskCreateSerializer


#ЗАДАНИЕ 1: ЗАМЕНА ПРЕДСТАВЛЕНИЙ ДЛЯ ЗАДАЧ

class TaskPagination(PageNumberPagination):
    """
    Пагинация для задач
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class TaskListCreateView(ListCreateAPIView):
    """
    ЗАДАНИЕ 1:
    Замена представлений для задач (Tasks) на Generic Views

    Используйте ListCreateAPIView для создания и получения списка задач.
    Реализуйте фильтрацию, поиск и сортировку:
    - Фильтрация по полям status и deadline
    - Поиск по полям title и description
    - Сортировка по полю created_at

    Использование:
    GET /api/v1/tasks/ - список задач
    POST /api/v1/tasks/ - создать задачу
    GET /api/v1/tasks/?status=completed - фильтр по статусу
    GET /api/v1/tasks/?search=важная - поиск по названию и описанию
    GET /api/v1/tasks/?ordering=created_at - сортировка по дате создания
    GET /api/v1/tasks/?ordering=-created_at - сортировка по убыванию даты
    GET /api/v1/tasks/?deadline__gte=2024-01-01 - фильтр по дате дедлайна
    """

    # Для GET запросов используем TaskSerializer (со всеми полями)
    # Для POST запросов используем TaskCreateSerializer (с валидацией)
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer

    queryset = Task.objects.all()
    pagination_class = TaskPagination

    # Настройка фильтрации, поиска и сортировки
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Фильтрация по конкретным полям
    filterset_fields = {
        'status': ['exact'],
        'deadline': ['exact', 'gte', 'lte', 'gt', 'lt'],  # gte = >=, lte = <=, gt = >, lt = <
    }

    # Поиск по нескольким полям
    search_fields = ['title', 'description']

    # Сортировка по полям
    ordering_fields = ['created_at', 'deadline', 'title']
    ordering = ['-created_at']  # Сортировка по умолчанию


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    """
    ЗАДАНИЕ 1 (продолжение):
    Замена представлений для задач на Generic Views

    Используйте RetrieveUpdateDestroyAPIView для получения, обновления и удаления задач.

    Использование:
    GET /api/v1/tasks/1/ - получить задачу
    PUT /api/v1/tasks/1/ - полностью обновить задачу
    PATCH /api/v1/tasks/1/ - частично обновить задачу
    DELETE /api/v1/tasks/1/ - удалить задачу
    """

    # Для GET запросов используем TaskSerializer
    # Для PUT/PATCH используем TaskCreateSerializer с валидацией
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TaskCreateSerializer
        return TaskSerializer

    queryset = Task.objects.all()
    lookup_field = 'pk'


#ЗАДАНИЕ 2: ЗАМЕНА ПРЕДСТАВЛЕНИЙ ДЛЯ ПОДЗАДАЧ

class SubTaskPagination(PageNumberPagination):
    """
    Пагинация для подзадач
    """
    page_size = 5  # По умолчанию 5 на страницу (как в предыдущем задании)
    page_size_query_param = 'page_size'
    max_page_size = 100


class SubTaskListCreateView(ListCreateAPIView):
    """
    НОВОЕ ЗАДАНИЕ 2:
    Замена представлений для подзадач (SubTasks) на Generic Views

    Используйте ListCreateAPIView для создания и получения списка подзадач.
    Реализуйте фильтрацию, поиск и сортировку:
    - Фильтрация по полям status и task (через task__status и task__deadline)
    - Поиск по полям title и description
    - Сортировка по полю created_at

    Использование:
    GET /api/v1/subtasks/ - список подзадач
    POST /api/v1/subtasks/ - создать подзадачу
    GET /api/v1/subtasks/?status=done - фильтр по статусу подзадачи
    GET /api/v1/subtasks/?task__status=completed - фильтр по статусу родительской задачи
    GET /api/v1/subtasks/?search=важная - поиск по названию и описанию
    GET /api/v1/subtasks/?ordering=-created_at - сортировка по убыванию даты
    """

    # Для GET запросов используем SubTaskSerializer
    # Для POST запросов используем SubTaskCreateSerializer
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubTaskCreateSerializer
        return SubTaskSerializer

    queryset = SubTask.objects.all()
    pagination_class = SubTaskPagination

    # Настройка фильтрации, поиска и сортировки
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Фильтрация по конкретным полям
    filterset_fields = {
        'status': ['exact'],
        'completed': ['exact'],
        'task': ['exact'],  # Фильтр по ID задачи
        'task__status': ['exact'],  # Фильтр по статусу родительской задачи
        'task__deadline': ['exact', 'gte', 'lte'],  # Фильтр по дедлайну родительской задачи
    }

    # Поиск по нескольким полям
    search_fields = ['title', 'description', 'task__title']

    # Сортировка по полям
    ordering_fields = ['created_at', 'updated_at', 'title', 'task__title']
    ordering = ['-created_at']  # Сортировка по умолчанию


class SubTaskDetailView(RetrieveUpdateDestroyAPIView):
    """
    НОВОЕ ЗАДАНИЕ 2 (продолжение):
    Замена представлений для подзадач на Generic Views

    Используйте RetrieveUpdateDestroyAPIView для получения, обновления и удаления подзадач.

    Использование:
    GET /api/v1/subtasks/1/ - получить подзадачу
    PUT /api/v1/subtasks/1/ - полностью обновить подзадачу
    PATCH /api/v1/subtasks/1/ - частично обновить подзадачу
    DELETE /api/v1/subtasks/1/ - удалить подзадачу
    """

    # Для GET запросов используем SubTaskSerializer
    # Для PUT/PATCH используем SubTaskCreateSerializer
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SubTaskCreateSerializer
        return SubTaskSerializer

    queryset = SubTask.objects.all()
    lookup_field = 'pk'


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count

@api_view(['GET'])
def task_stats(request):
    """
    Агрегирующий эндпоинт для статистики задач оставляем как есть.
    """
    total = Task.objects.count()
    completed = Task.objects.filter(status='completed').count()
    in_progress = Task.objects.filter(status='in_progress').count()
    overdue = Task.objects.filter(deadline__lt=now()).exclude(status='completed').count()

    # Статистика по статусам
    status_stats = Task.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    # Статистика по приоритетам
    priority_stats = Task.objects.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')

    return Response({
        'total_tasks': total,
        'completed_tasks': completed,
        'in_progress_tasks': in_progress,
        'overdue_tasks': overdue,
        'completion_rate': round((completed / total * 100), 1) if total > 0 else 0,
        'status_distribution': list(status_stats),
        'priority_distribution': list(priority_stats),
    }, status=status.HTTP_200_OK)


# ФИЛЬТРЫ

import django_filters


class TaskFilter(django_filters.FilterSet):
    """
    Кастомный фильтр для задач
    """
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    deadline_gte = django_filters.DateTimeFilter(field_name='deadline', lookup_expr='gte')
    deadline_lte = django_filters.DateTimeFilter(field_name='deadline', lookup_expr='lte')

    class Meta:
        model = Task
        fields = ['status', 'priority']


class SubTaskFilter(django_filters.FilterSet):
    """
    Кастомный фильтр для подзадач
    """
    title = django_filters.CharFilter(lookup_expr='icontains')
    task_title = django_filters.CharFilter(field_name='task__title', lookup_expr='icontains')

    class Meta:
        model = SubTask
        fields = ['status', 'completed', 'task']