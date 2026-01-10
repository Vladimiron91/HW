from rest_framework import serializers
from django.utils.timezone import now
from task_manager.models import Task, SubTask, Category


class TaskSerializer(serializers.ModelSerializer):
    # Поле для отображения имени владельца (только чтение)
    owner_username = serializers.ReadOnlyField(source='owner.username')
    # Поле для отображения названия категории
    category_name = serializers.ReadOnlyField(source='category.name')
    # Количество подзадач
    subtasks_count = serializers.SerializerMethodField()
    # Количество завершённых подзадач
    completed_subtasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'deadline', 'created_at', 'updated_at', 'category',
            'category_name', 'owner', 'owner_username', 'subtasks_count',
            'completed_subtasks_count', 'is_deleted', 'deleted_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_deleted', 'deleted_at']

    def get_subtasks_count(self, obj):
        """Получаем количество подзадач для задачи"""
        return obj.subtasks.count()

    def get_completed_subtasks_count(self, obj):
        """Получаем количество выполненных подзадач"""
        return obj.subtasks.filter(status='done').count()


class SubTaskCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания подзадач.
    Поля created_at и owner доступны только для чтения.
    """
    created_at = serializers.DateTimeField(read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    owner_id = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = SubTask
        fields = [
            'id', 'title', 'description', 'completed', 'task',
            'status', 'deadline', 'created_at', 'owner', 'owner_id'
        ]
        read_only_fields = ['created_at', 'owner', 'owner_id']


class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания категорий с проверкой уникальности.
    """

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        """
        Проверяем уникальность названия при создании.
        """
        name = validated_data.get('name')

        # Проверяем среди всех категорий (включая удалённые)
        if Category.objects.filter(name=name).exists():
            # Проверяем, не удалена ли такая категория
            existing = Category.objects.get(name=name)
            if existing.is_deleted:
                # Восстанавливаем удалённую категорию
                existing.is_deleted = False
                existing.deleted_at = None
                existing.description = validated_data.get('description', existing.description)
                existing.save()
                return existing
            else:
                raise serializers.ValidationError({
                    'name': 'Категория с таким названием уже существует.'
                })

        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Проверяем уникальность названия при обновлении.
        """
        name = validated_data.get('name')

        if name and name != instance.name:
            if Category.objects.filter(name=name).exists():
                existing = Category.objects.get(name=name)
                if existing.is_deleted:
                    raise serializers.ValidationError({
                        'name': 'Невозможно изменить имя: категория с таким названием уже существует (удалена).'
                    })
                else:
                    raise serializers.ValidationError({
                        'name': 'Категория с таким названием уже существует.'
                    })

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


class SubTaskSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор для подзадач.
    """
    task_title = serializers.ReadOnlyField(source='task.title')
    owner_username = serializers.ReadOnlyField(source='owner.username')
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = SubTask
        fields = [
            'id', 'title', 'description', 'completed', 'task', 'task_title',
            'status', 'deadline', 'created_at', 'updated_at', 'owner',
            'owner_username', 'is_deleted', 'deleted_at', 'is_overdue'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'owner', 'owner_username',
            'is_deleted', 'deleted_at', 'is_overdue'
        ]


class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Детальный сериализатор задачи с вложенными подзадачами.
    """
    subtasks = SubTaskSerializer(many=True, read_only=True)
    owner_username = serializers.ReadOnlyField(source='owner.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'deadline', 'created_at', 'updated_at', 'subtasks',
            'category', 'category_name', 'owner', 'owner_username',
            'is_deleted', 'deleted_at', 'is_overdue'
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания задач с валидацией поля deadline.
    Поле owner автоматически заполняется из запроса.
    """
    owner = serializers.ReadOnlyField(source='owner.username')
    owner_id = serializers.ReadOnlyField(source='owner.id')

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'deadline', 'category', 'owner', 'owner_id'
        ]
        read_only_fields = ['owner', 'owner_id']

    def validate_deadline(self, value):
        """
        Проверяем, что deadline не в прошлом.
        """
        if value and value < now():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом.")
        return value


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения категорий.
    Включает информацию о количестве задач.
    """
    tasks_count = serializers.SerializerMethodField()
    active_tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'created_at',
            'is_deleted', 'deleted_at', 'tasks_count', 'active_tasks_count'
        ]
        read_only_fields = [
            'created_at', 'is_deleted', 'deleted_at',
            'tasks_count', 'active_tasks_count'
        ]

    def get_tasks_count(self, obj):
        """Общее количество задач в категории"""
        return obj.tasks.count()

    def get_active_tasks_count(self, obj):
        """Количество активных (не удалённых) задач"""
        return obj.tasks.filter(is_deleted=False).count()


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления категорий.
    """

    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

    def validate_name(self, value):
        """
        Проверяем уникальность имени среди активных категорий.
        """
        # При создании
        if not self.instance:
            # Проверяем среди не удалённых категорий
            if Category.objects.filter(name=value, is_deleted=False).exists():
                raise serializers.ValidationError("Категория с таким названием уже существует.")
        # При обновлении
        else:
            # Если имя изменилось, проверяем уникальность
            if value != self.instance.name:
                if Category.objects.filter(name=value, is_deleted=False).exists():
                    raise serializers.ValidationError("Категория с таким названием уже существует.")
        return value


class UserTaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения задач текущего пользователя.
    Используется в специальных эндпоинтах.
    """
    category_name = serializers.ReadOnlyField(source='category.name')
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'deadline', 'category', 'category_name', 'created_at',
            'is_overdue', 'subtasks_count'
        ]

    def get_subtasks_count(self, obj):
        """Количество подзадач"""
        return obj.subtasks.count()


class UserSubTaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения подзадач текущего пользователя.
    """
    task_title = serializers.ReadOnlyField(source='task.title')
    is_overdue = serializers.ReadOnlyField()

    class Meta:
        model = SubTask
        fields = [
            'id', 'title', 'description', 'completed', 'status',
            'deadline', 'task', 'task_title', 'created_at', 'is_overdue'
        ]