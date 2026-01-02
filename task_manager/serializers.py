from rest_framework import serializers
from django.utils.timezone import now
from task_manager.models import Task, SubTask, Category  # Убедитесь, что SubTask импортирована


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at']


# ==================== ЗАДАНИЕ 1: SubTaskCreateSerializer ====================
class SubTaskCreateSerializer(serializers.ModelSerializer):
    """
    Специальный сериализатор для создания подзадач.
    Поле created_at должно быть доступно только для чтения.
    """
    created_at = serializers.DateTimeField(read_only=True)  # Задание 1: read_only поле

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'completed', 'task', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


# ==================== ЗАДАНИЕ 2: CategoryCreateSerializer ====================
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


# Базовый сериализатор для подзадач
class SubTaskSerializer(serializers.ModelSerializer):
    """
    Простой сериализатор для подзадач.
    Будет использоваться во вложенном виде.
    """

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'completed', 'task', 'created_at']
        read_only_fields = ['created_at']


# ==================== ЗАДАНИЕ 3: TaskDetailSerializer ====================
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


# ==================== ЗАДАНИЕ 4: TaskCreateSerializer ====================
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


# ==================== ДЛЯ НОВОГО ЗАДАНИЯ: Сериализаторы для категорий ====================
class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения категорий.
    """

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'is_deleted', 'deleted_at']
        read_only_fields = ['created_at', 'is_deleted', 'deleted_at']


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления категорий.
    """

    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

    def validate_name(self, value):
        """
        Проверяем уникальность имени среди не удалённых категорий.
        """
        # Исключаем текущую категорию при обновлении
        if self.instance:
            if Category.objects.filter(name=value, is_deleted=False).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Категория с таким названием уже существует.")
        else:
            # При создании проверяем среди всех не удалённых
            if Category.objects.filter(name=value, is_deleted=False).exists():
                raise serializers.ValidationError("Категория с таким названием уже существует.")
        return value