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

# Новые импорты для задания с владельцами
from .permissions import IsOwnerOrReadOnly, IsTaskOwner, IsSubTaskOwner
from .serializers import (
    TaskSerializer, SubTaskCreateSerializer, SubTaskSerializer,
    CategorySerializer, TaskDetailSerializer, TaskCreateSerializer,
    CategoryCreateSerializer, CategoryCreateUpdateSerializer,
    UserTaskSerializer, UserSubTaskSerializer
)

from django.utils.timezone import now
from django.db.models import Count, Q
from .models import Task, SubTask, Category

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
    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategorySerializer

    # ЗАДАНИЕ 2: Пермишены - только админы могут изменять
    permission_classes = [IsAdminUser]
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateUpdateSerializer
        return CategorySerializer

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
    queryset = Task.objects.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer

    # ЗАДАНИЕ 2: Пермишены - только свои задачи
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]

    # ЗАДАНИЕ 3: Пагинация будет применена автоматически через глобальные настройки
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline', 'category', 'priority']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'title']

    def get_queryset(self):
        """Возвращаем только задачи текущего пользователя"""
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(owner=user, is_deleted=False)
        return Task.objects.none()

    def perform_create(self, serializer):
        """Автоматически назначаем владельца при создании"""
        serializer.save(owner=self.request.user)


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    """
    ЗАДАНИЕ 2 и 1: Пермишены и JWT аутентификация для деталей задачи
    """
    queryset = Task.objects.filter(is_deleted=False)
    serializer_class = TaskSerializer

    # ЗАДАНИЕ 2: Пермишены - только владелец может изменять
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):
        """Выбор сериализатора для детального просмотра"""
        if self.request.method == 'GET':
            return TaskDetailSerializer
        return TaskSerializer

    def get_queryset(self):
        """Только задачи текущего пользователя"""
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(owner=user, is_deleted=False)
        return Task.objects.none()


# ==================== GENERIC VIEWS ДЛЯ ПОДЗАДАЧ ====================

class SubTaskListCreateView(ListCreateAPIView):
    """
    ЗАДАНИЕ 3: Глобальная пагинация (5 подзадач на страницу)
    ЗАДАНИЕ 2 и 1: Пермишены и JWT аутентификация
    """
    queryset = SubTask.objects.filter(is_deleted=False)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubTaskCreateSerializer
        return SubTaskSerializer

    # ЗАДАНИЕ 2: Пермишены - только свои подзадачи
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]

    # ЗАДАНИЕ 3: Пагинация через глобальные настройки
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline', 'task', 'completed']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline']

    def get_queryset(self):
        """Возвращаем только подзадачи текущего пользователя"""
        user = self.request.user
        if user.is_authenticated:
            return SubTask.objects.filter(owner=user, is_deleted=False)
        return SubTask.objects.none()

    def perform_create(self, serializer):
        """Автоматически назначаем владельца при создании"""
        serializer.save(owner=self.request.user)


class SubTaskDetailView(RetrieveUpdateDestroyAPIView):
    """
    ЗАДАНИЕ 2 и 1: Пермишены и JWT аутентификация для подзадач
    """
    queryset = SubTask.objects.filter(is_deleted=False)
    serializer_class = SubTaskSerializer

    # ЗАДАНИЕ 2: Пермишены - только владелец может изменять
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        """Только подзадачи текущего пользователя"""
        user = self.request.user
        if user.is_authenticated:
            return SubTask.objects.filter(owner=user, is_deleted=False)
        return SubTask.objects.none()


# ==================== ДОПОЛНИТЕЛЬНЫЕ VIEWSET ====================

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для задач с JWT аутентификацией и пермишенами
    Включает функционал для работы с владельцами задач
    """
    serializer_class = TaskSerializer

    # ЗАДАНИЕ 2: Пермишены - только владелец может изменять
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]

    # ЗАДАНИЕ 3: Пагинация через глобальные настройки
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'title']

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskSerializer

    def get_queryset(self):
        """Только задачи текущего пользователя"""
        user = self.request.user
        return Task.objects.filter(owner=user, is_deleted=False)

    def perform_create(self, serializer):
        """Автоматически назначаем владельца при создании"""
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Получение всех задач текущего пользователя"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Просроченные задачи пользователя"""
        queryset = self.get_queryset().filter(
            deadline__lt=now(),
            status__in=['pending', 'in_progress']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def subtasks(self, request, pk=None):
        """Подзадачи конкретной задачи"""
        task = self.get_object()
        subtasks = task.subtasks.filter(is_deleted=False)
        serializer = SubTaskSerializer(subtasks, many=True)
        return Response(serializer.data)


class SubTaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для подзадач с JWT аутентификацией и пермишенами
    Включает функционал для работы с владельцами подзадач
    """
    serializer_class = SubTaskSerializer

    # ЗАДАНИЕ 2: Пермишены - только владелец может изменять
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    # ЗАДАНИЕ 1: JWT аутентификация
    authentication_classes = [JWTAuthentication]

    # ЗАДАНИЕ 3: Пагинация через глобальные настройки
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'completed', 'task']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.action == 'create':
            return SubTaskCreateSerializer
        return SubTaskSerializer

    def get_queryset(self):
        """Только подзадачи текущего пользователя"""
        user = self.request.user
        return SubTask.objects.filter(owner=user, is_deleted=False)

    def perform_create(self, serializer):
        """Автоматически назначаем владельца при создании"""
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def my_subtasks(self, request):
        """Получение всех подзадач текущего пользователя"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Просроченные подзадачи пользователя"""
        queryset = self.get_queryset().filter(
            deadline__lt=now(),
            status__in=['not_started', 'in_progress']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_done(self, request, pk=None):
        """Отметить подзадачу как выполненную"""
        subtask = self.get_object()
        subtask.mark_as_done()
        serializer = self.get_serializer(subtask)
        return Response(serializer.data)


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
                ).filter(deadline_weekday=weekday_int, is_deleted=False)
            except ValueError:
                return Response(
                    {"error": "Параметр weekday должен быть числом от 1 до 7"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            tasks = Task.objects.filter(is_deleted=False)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==================== НОВЫЕ VIEW ДЛЯ РАБОТЫ С ВЛАДЕЛЬЦАМИ ====================

class MyTasksView(APIView):
    """API для получения задач текущего пользователя"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        """Получить все задачи текущего пользователя"""
        tasks = Task.objects.filter(owner=request.user, is_deleted=False)
        serializer = UserTaskSerializer(tasks, many=True)
        return Response(serializer.data)


class MySubTasksView(APIView):
    """API для получения подзадач текущего пользователя"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        """Получить все подзадачи текущего пользователя"""
        subtasks = SubTask.objects.filter(owner=request.user, is_deleted=False)
        serializer = UserSubTaskSerializer(subtasks, many=True)
        return Response(serializer.data)


class TaskOwnerStatsView(APIView):
    """Статистика задач для текущего пользователя"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        """Получить статистику по задачам пользователя"""
        user = request.user

        total_tasks = Task.objects.filter(owner=user, is_deleted=False).count()
        by_status = Task.objects.filter(owner=user, is_deleted=False)\
            .values('status').annotate(count=Count('status'))
        overdue_tasks = Task.objects.filter(
            owner=user,
            deadline__lt=now(),
            status__in=['pending', 'in_progress'],
            is_deleted=False
        ).count()

        total_subtasks = SubTask.objects.filter(owner=user, is_deleted=False).count()
        completed_subtasks = SubTask.objects.filter(
            owner=user,
            completed=True,
            is_deleted=False
        ).count()

        data = {
            "user": user.username,
            "total_tasks": total_tasks,
            "tasks_by_status": list(by_status),
            "overdue_tasks": overdue_tasks,
            "total_subtasks": total_subtasks,
            "completed_subtasks": completed_subtasks
        }
        return Response(data)


# ==================== APIView ДЛЯ СОЗДАНИЯ ЗАДАЧ И ПОДЗАДАЧ ====================

class TaskCreateAPIView(APIView):
    """Создание задачи с автоматическим назначением владельца"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        """Создать новую задачу"""
        serializer = TaskCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubTaskCreateAPIView(APIView):
    """Создание подзадачи с автоматическим назначением владельца"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        """Создать новую подзадачу"""
        serializer = SubTaskCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)