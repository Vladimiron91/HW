from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает изменение и удаление только владельцу объекта.
    Остальным — только чтение.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) всем аутентифицированным пользователям
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешаем изменение и удаление только владельцу
        return obj.owner == request.user


class IsTaskOwner(permissions.BasePermission):
    """
    Разрешает доступ только владельцу задачи.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsSubTaskOwner(permissions.BasePermission):
    """
    Разрешает доступ только владельцу подзадачи.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user