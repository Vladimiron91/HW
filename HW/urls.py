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
from django.urls import path
from task_manager.views import (
    TaskListCreateView,
    TaskDetailView,
    SubTaskListCreateView,
    SubTaskDetailView,
    task_stats,
)

app_name = "task_manager_generic"

urlpatterns = [
    # ==================== ЗАДАНИЕ 1: Generic Views для задач ====================
    # ListCreateAPIView для создания и получения списка задач
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),

    # RetrieveUpdateDestroyAPIView для получения, обновления и удаления задач
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

    # ==================== ЗАДАНИЕ 2: Generic Views для подзадач ====================
    # ListCreateAPIView для создания и получения списка подзадач
    path('subtasks/', SubTaskListCreateView.as_view(), name='subtask-list-create'),

    # RetrieveUpdateDestroyAPIView для получения, обновления и удаления подзадач
    path('subtasks/<int:pk>/', SubTaskDetailView.as_view(), name='subtask-detail'),

    # ==================== СТАТИСТИКА (оставляем как есть) ====================
    path('stats/', task_stats, name='task-stats'),
]