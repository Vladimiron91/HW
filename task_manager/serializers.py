from rest_framework import serializers
from django.utils.timezone import now
from task_manager.models import Task, SubTask, Category


# СУЩЕСТВУЮЩИЕ СЕРИАЛИЗАТОРЫ

class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'deadline', 'created_at', 'updated_at', 'is_overdue'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_overdue']


class SubTaskSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = SubTask
        fields = [
            'id', 'title', 'description', 'completed', 'status',
            'task', 'task_title', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


#ЗАДАНИЯ: СЕРИАЛИЗАТОРЫ ДЛЯ СОЗДАНИЯ

class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания задач с валидацией
    """

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'deadline']

    def validate_deadline(self, value):
        """
        Проверяем, что deadline не в прошлом
        """
        if value and value < now():
            raise serializers.ValidationError("Дата дедлайна не может быть в прошлом.")
        return value


class SubTaskCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания подзадач с read_only полем created_at
    """
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'completed', 'status', 'task', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


#ДЛЯ ФИЛЬТРАЦИИ

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']