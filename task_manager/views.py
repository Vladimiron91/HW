"""
ЗАДАНИЕ 1: Настройка JWT аутентификации
ЗАДАНИЕ 2: Реализация пермишенов для API
ЗАДАНИЕ 3: Настройка глобальной пагинации
"""

from django.db.models.functions import ExtractWeekDay
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import filters, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# ==================== ЗАДАНИЕ 1 и 2: JWT АУТЕНТИФИКАЦИЯ И ПЕРМИШЕНЫ ====================
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.utils.timezone import now
from django.db.models import Count
from .models import Task, SubTask, Category
from .serializers import TaskSerializer, SubTaskCreateSerializer, SubTaskSerializer, CategorySerializer, \
    TaskDetailSerializer, TaskCreateSerializer

# ==================== СУЩЕСТВУЮЩИЕ ФУНКЦИОНАЛЬНЫЕ VIEW ====================

@api_view(['POST'])
def task_create(request):
    """Создание задачи"""
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def task_list(request):
    """Список всех задач"""
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def task_detail(request, pk):
    """Детали задачи по ID"""
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = TaskSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def task_stats(request):
    """Статистика задач"""
    total = Task.objects.count()
    by_status = Task.objects.values('status').annotate(count=Count('status'))
    overdue = Task.objects.filter(deadline__lt=now()).count()

    data = {
        "total_tasks": total,
        "tasks_by_status": list(by_status),
        "overdue_tasks": overdue
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['PUT'])
def task_update(request, pk):
    """Обновление задачи"""
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = TaskSerializer(task, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def task_delete(request, pk):
    """Удаление задачи"""
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    task.delete()
    return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# ==================== VIEWSET ДЛЯ КАТЕГОРИЙ ====================

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ЗАДАНИЕ 1 и 2: JWT аутентификация и пермишены для категорий
    - Только админы могут создавать/изменять/удалять категории
    - Все могут просматривать категории
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    # ЗАДАНИЕ 2: Пермишены - только админы могут изменять
    permission_classes = [IsAdminUser]  # Изменение только для админов
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]

    @action(detail=True, methods=['get'])
    def count_tasks(self, request, pk=None):
        """Подсчёт задач в категории"""
        category = self.get_object()
        count = category.tasks.count()
        return Response({'category': category.name, 'tasks_count': count})


# ==================== GENERIC VIEWS ДЛЯ ЗАДАЧ ====================

class TaskListCreateView(ListCreateAPIView):
    """
    ЗАДАНИЕ 3: Глобальная пагинация (5 элементов на страницу)
    ЗАДАНИЕ 2: IsAuthenticatedOrReadOnly - чтение для всех, запись только авторизованным
    ЗАДАНИЕ 1: JWT аутентификация
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    # ЗАДАНИЕ 2: Пермишены
    permission_classes = [IsAuthenticatedOrReadOnly]
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]

    # ЗАДАНИЕ 3: Пагинация будет применена автоматически через глобальные настройки
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    """
    ЗАДАНИЕ 2 и 1: Пермишены и JWT аутентификация для деталей задачи
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    # ЗАДАНИЕ 2: Пермишены
    permission_classes = [IsAuthenticatedOrReadOnly]
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]


# ==================== GENERIC VIEWS ДЛЯ ПОДЗАДАЧ ====================

class SubTaskListCreateView(ListCreateAPIView):
    """
    ЗАДАНИЕ 3: Глобальная пагинация (5 подзадач на страницу)
    ЗАДАНИЕ 2 и 1: Пермишены и JWT аутентификация
    """
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer

    # ЗАДАНИЕ 2: Пермишены
    permission_classes = [IsAuthenticatedOrReadOnly]
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]

    # ЗАДАНИЕ 3: Пагинация через глобальные настройки
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']


class SubTaskDetailView(RetrieveUpdateDestroyAPIView):
    """
    ЗАДАНИЕ 2 и 1: Пермишены и JWT аутентификация для подзадач
    """
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer

    # ЗАДАНИЕ 2: Пермишены
    permission_classes = [IsAuthenticatedOrReadOnly]
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]


# ==================== ДОПОЛНИТЕЛЬНЫЕ VIEWSET ====================

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для задач с JWT аутентификацией и пермишенами
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    # ЗАДАНИЕ 2: Пермишены
    permission_classes = [IsAuthenticatedOrReadOnly]
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]

    # ЗАДАНИЕ 3: Пагинация через глобальные настройки
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'title']


class SubTaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для подзадач с JWT аутентификацией и пермишенами
    """
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer

    # ЗАДАНИЕ 2: Пермишены
    permission_classes = [IsAuthenticatedOrReadOnly]
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]

    # ЗАДАНИЕ 3: Пагинация через глобальные настройки
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'completed', 'task']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']


# ==================== VIEW ДЛЯ ФИЛЬТРАЦИИ ПО ДНЮ НЕДЕЛИ ====================

class TaskByWeekdayView(APIView):
    """
    View для фильтрации задач по дню недели
    """
    # ЗАДАНИЕ 2: Разрешить всем читать
    permission_classes = [AllowAny]

    def get(self, request):
        weekday = request.query_params.get('weekday', None)

        if weekday is not None:
            try:
                weekday_int = int(weekday)
                tasks = Task.objects.annotate(
                    deadline_weekday=ExtractWeekDay('deadline')
                ).filter(deadline_weekday=weekday_int)
            except ValueError:
                return Response(
                    {"error": "Параметр weekday должен быть числом от 1 до 7"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            tasks = Task.objects.all()

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)