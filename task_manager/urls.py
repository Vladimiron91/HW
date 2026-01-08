from django.urls import path, include
from rest_framework.routers import DefaultRouter
from task_manager.views import (
    CategoryViewSet,
    TaskViewSet,
    SubTaskViewSet,
    TaskListCreateView,
    TaskDetailView,
    SubTaskListCreateView,
    SubTaskDetailView,
    task_stats,
    task_list,
    task_detail,
    task_create,
    task_update,
    task_delete,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'subtasks', SubTaskViewSet, basename='subtask')

app_name = "task_manager"

urlpatterns = [
    # Маршруты через router (для ViewSet)
    path('', include(router.urls)),

    # Функциональные view (для обратной совместимости)
    path('tasks/create/', task_create, name='task-create'),
    path('tasks/', task_list, name='task-list'),
    path('tasks/<int:pk>/', task_detail, name='task-detail'),
    path('tasks/stats/', task_stats, name='task-stats'),
    path('tasks/<int:pk>/update/', task_update, name='task-update'),
    path('tasks/<int:pk>/delete/', task_delete, name='task-delete'),

    # Generic Views (для отдельных задач и подзадач)
    path('generic/tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('generic/tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('generic/subtasks/', SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('generic/subtasks/<int:pk>/', SubTaskDetailView.as_view(), name='subtask-detail'),
]