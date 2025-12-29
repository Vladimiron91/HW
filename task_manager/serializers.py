from rest_framework import serializers
from django.utils.timezone import now
from task_manager.models import Task, SubTask, Category


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'deadline', 'created_at']


# === ЗАДАНИЕ 1: SubTaskCreateSerializer ===
class SubTaskCreateSerializer(serializers.ModelSerializer):
    """
    Специальный сериализатор для создания подзадач.
    Поле created_at должно быть доступно только для чтения.
    """
    created_at = serializers.DateTimeField(read_only=True)  # Задание 1: read_only поле

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'completed', 'status', 'task', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


# === ЗАДАНИЕ 2: CategoryCreateSerializer ===
class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания категорий с проверкой уникальности.
    Нужно переопределить методы create и update.
    """

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        """
        Проверяем уникальность названия при создании.
        Если категория с таким именем уже есть - возвращаем ошибку.
        """
        name = validated_data.get('name')

        # Проверяем, нет ли уже категории с таким именем
        if Category.objects.filter(name=name).exists():
            raise serializers.ValidationError({
                'name': 'Категория с таким названием уже существует.'
            })

        # Если всё хорошо - создаём категорию
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Проверяем уникальность названия при обновлении.
        Важно: проверяем только если имя изменилось.
        """
        name = validated_data.get('name')

        # Если пытаемся изменить имя
        if name and name != instance.name:
            # Проверяем, нет ли другой категории с таким именем
            if Category.objects.filter(name=name).exists():
                raise serializers.ValidationError({
                    'name': 'Категория с таким названием уже существует.'
                })

        # Обновляем остальные поля
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        return instance


# Базовый сериализатор для подзадач (для задания 3 и новых заданий)
class SubTaskSerializer(serializers.ModelSerializer):
    """
    Простой сериализатор для подзадач.
    Будет использоваться во вложенном виде.
    """
    task_title = serializers.CharField(source='task.title', read_only=True)

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'completed', 'status', 'task', 'task_title', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


# === ЗАДАНИЕ 3: TaskDetailSerializer ===
class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Детальный сериализатор задачи с вложенными подзадачами.
    Показывает все подзадачи, связанные с задачей.
    """
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'deadline', 'created_at', 'updated_at', 'subtasks'
        ]


# === ЗАДАНИЕ 4: TaskCreateSerializer ===
class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания задач с валидацией поля deadline.
    Дата deadline не может быть в прошлом.
    """

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'deadline']

    def validate_deadline(self, value):
        """
        Проверяем, что deadline не в прошлом.
        Если дата в прошлом - возвращаем ошибку валидации.
        """
        if value and value < now():
            raise serializers.ValidationError("Дата дедлайна не может быть в прошлом.")
        return value

    def validate(self, data):
        """
        Дополнительная валидация данных.
        Проверяем корректность статуса и приоритета.
        """
        # Проверяем статус
        if 'status' in data:
            valid_statuses = [choice[0] for choice in Task.STATUS_CHOICES]
            if data['status'] not in valid_statuses:
                raise serializers.ValidationError({
                    'status': f'Недопустимый статус. Допустимые значения: {", ".join(valid_statuses)}'
                })

        # Проверяем приоритет
        if 'priority' in data:
            valid_priorities = [choice[0] for choice in Task.PRIORITY_CHOICES]
            if data['priority'] not in valid_priorities:
                raise serializers.ValidationError({
                    'priority': f'Недопустимый приоритет. Допустимые значения: {", ".join(valid_priorities)}'
                })

        return data


# Сериализатор для категорий (простой, без валидации)
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']