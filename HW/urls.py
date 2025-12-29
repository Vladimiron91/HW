"""
URL configuration for HW project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from task_manager import views as task_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # ==================== СУЩЕСТВУЮЩИЕ МАРШРУТЫ ====================
    # API для задач (старые задания)
    path('tasks/create/', task_views.task_create, name='task-create'),
    path('tasks/', task_views.task_list, name='task-list'),
    path('tasks/<int:pk>/', task_views.task_detail, name='task-detail'),
    path('tasks/stats/', task_views.task_stats, name='task-stats'),
    path('tasks/<int:pk>/update/', task_views.task_update, name='task-update'),
    path('tasks/<int:pk>/delete/', task_views.task_delete, name='task-delete'),

    # ==================== ЗАДАНИЯ 1-5 (ПРЕДЫДУЩИЕ) ====================
    # Задание 5: Классы представлений для подзадач
    path('subtasks/', task_views.SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:pk>/', task_views.SubTaskDetailUpdateDeleteView.as_view(), name='subtask-detail-update-delete'),

    # Демонстрационные маршруты для других заданий
    path('categories/', task_views.category_list_create, name='category-list-create'),
    path('tasks/<int:pk>/detail/', task_views.task_detail_with_subtasks, name='task-detail-with-subtasks'),
    path('tasks/create-validated/', task_views.task_create_with_validation, name='task-create-validated'),

    # ==================== НОВЫЕ ЗАДАНИЯ (фильтрация и пагинация) ====================
    # НОВОЕ ЗАДАНИЕ 1: Фильтрация задач по дню недели
    path('tasks-by-weekday/', task_views.TaskByWeekdayView.as_view(), name='tasks-by-weekday'),

    # НОВОЕ ЗАДАНИЕ 2: Пагинация подзадач
    path('subtasks-paginated/', task_views.SubTaskPaginatedView.as_view(), name='subtasks-paginated'),

    # НОВОЕ ЗАДАНИЕ 3: Фильтрация подзадач по названию задачи и статусу
    path('subtasks-filtered/', task_views.SubTaskFilteredView.as_view(), name='subtasks-filtered'),

    # Дополнительный маршрут для обратной совместимости (старый список задач)
    path('tasks-old/', task_views.task_list_old, name='task-list-old'),
]