"""
URL configuration for HW project.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Импортируем только то, что существует
from task_manager.views import CategoryViewSet

# Создаем router
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Подключаем router для ModelViewSet
    path('api/v1/', include(router.urls)),

    # Остальные маршруты (если нужны)
    # path('', include('task_manager.urls')),
]