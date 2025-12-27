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

    # === Существующие маршруты (ваш код) ===
    # api for task
    # Задание 1
    path('tasks/create/', task_views.task_create, name='task-create'),

    # Задание 2
    path('tasks/', task_views.task_list, name='task-list'),
    path('tasks/<int:pk>/', task_views.task_detail, name='task-detail'),

    # Задание 3
    path('tasks/stats/', task_views.task_stats, name='task-stats'),

    # просто дополнительно сделал
    path('tasks/<int:pk>/update/', task_views.task_update, name='task-update'),
    path('tasks/<int:pk>/delete/', task_views.task_delete, name='task-delete'),

    # === НОВЫЕ МАРШРУТЫ ДЛЯ ДОМАШНЕГО ЗАДАНИЯ ===

    # ЗАДАНИЕ 5: Маршруты для подзадач (классы представлений)
    path('subtasks/', task_views.SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:pk>/', task_views.SubTaskDetailUpdateDeleteView.as_view(), name='subtask-detail-update-delete'),

    # Демонстрационные маршруты для других заданий
    # Задание 2: Категории с проверкой уникальности
    path('categories/', task_views.category_list_create, name='category-list-create'),

    # Задание 3: Задачи с вложенными подзадачами
    path('tasks/<int:pk>/detail/', task_views.task_detail_with_subtasks, name='task-detail-with-subtasks'),

    # Задание 4: Создание задач с валидацией deadline
    path('tasks/create-validated/', task_views.task_create_with_validation, name='task-create-validated'),
]
