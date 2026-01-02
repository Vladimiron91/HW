from rest_framework.decorators import api_view, action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.timezone import now
from django.db.models import Count
from django.db.models.functions import ExtractWeekDay
from .models import Task, SubTask, Category
from .serializers import (
    TaskSerializer, SubTaskSerializer, SubTaskCreateSerializer, 
    CategorySerializer, CategoryCreateUpdateSerializer,  # Используем универсальный сериализатор
    TaskDetailSerializer, TaskCreateSerializer
)


# ==================== СУЩЕСТВУЮЩИЕ VIEW ====================

@api_view(['POST'])
def task_create(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def task_list(request):
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# ... остальные существующие view ...


# ==================== НОВОЕ ЗАДАНИЕ: CategoryViewSet ====================

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet для CRUD операций с категориями.
    Реализует мягкое удаление и кастомные методы.
    """
    # Используем кастомный менеджер для исключения удалённых записей
    queryset = Category.objects.all()
    
    def get_serializer_class(self):
        """Выбираем сериализатор в зависимости от действия"""
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryCreateUpdateSerializer
        return CategorySerializer
    
    # Фильтрация, поиск и сортировка
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    # ==================== ЗАДАНИЕ 1: Кастомный метод count_tasks ====================
    @action(detail=True, methods=['get'])
    def count_tasks(self, request, pk=None):
        """
        Подсчёт количества задач в категории.
        URL: GET /api/v1/categories/{id}/count_tasks/
        """
        category = self.get_object()
        tasks_count = category.tasks.count()
        
        return Response({
            'category_id': category.id,
            'category_name': category.name,
            'tasks_count': tasks_count,
            'message': f'В категории "{category.name}" {tasks_count} задач(а)'
        })
    
    # ==================== ЗАДАНИЕ 2: Методы для мягкого удаления ====================
    
    @action(detail=False, methods=['get'])
    def deleted(self, request):
        """
        Список удалённых категорий.
        URL: GET /api/v1/categories/deleted/
        """
        deleted_categories = Category.all_objects.filter(is_deleted=True)
        serializer = self.get_serializer(deleted_categories, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """
        Восстановление удалённой категории.
        URL: POST /api/v1/categories/{id}/restore/
        """
        # Получаем категорию из всех записей (включая удалённые)
        try:
            category = Category.all_objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response(
                {'error': 'Категория не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not category.is_deleted:
            return Response(
                {'error': 'Категория не была удалена'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Восстанавливаем
        category.is_deleted = False
        category.deleted_at = None
        category.save()
        
        return Response({
            'message': f'Категория "{category.name}" успешно восстановлена',
            'category_id': category.id
        })
    
    def destroy(self, request, *args, **kwargs):
        """
        Мягкое удаление категории (переопределяем стандартный метод).
        """
        category = self.get_object()
        
        # Мягкое удаление
        category.is_deleted = True
        category.deleted_at = now()
        category.save()
        
        return Response({
            'message': f'Категория "{category.name}" помечена как удалённая',
            'category_id': category.id,
            'deleted_at': category.deleted_at,
            'note': 'Используйте endpoint /restore/ для восстановления'
        }, status=status.HTTP_204_NO_CONTENT)