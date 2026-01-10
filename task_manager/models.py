from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.utils import timezone


# Менеджер для мягкого удаления
class SoftDeleteManager(models.Manager):
    """Кастомный менеджер для работы с мягким удалением"""

    def get_queryset(self):
        """Возвращает только неудалённые записи"""
        return super().get_queryset().filter(is_deleted=False)

    def with_deleted(self):
        """Все записи включая удалённые"""
        return super().get_queryset()

    def deleted_only(self):
        """Только удалённые записи"""
        return super().get_queryset().filter(is_deleted=True)


# МОДЕЛЬ КАТЕГОРИИ
class Category(models.Model):
    """Категория задач с поддержкой мягкого удаления"""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название категории'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание категории'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    # Поля для мягкого удаления
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Удалена?'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата удаления'
    )

    # Переопределение менеджера
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        """Мягкое удаление категории"""
        self.is_deleted = True
        self.deleted_at = now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self):
        """Полное удаление из БД"""
        super().delete()

    def restore(self):
        """Восстановление категории"""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


# МОДЕЛЬ ЗАДАЧИ
class Task(models.Model):
    """Основная модель задачи"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name='Название задачи'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание задачи'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Приоритет'
    )
    deadline = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Срок выполнения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='Категория'
    )

    # Поля владельца и мягкого удаления
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='task_owner',
        verbose_name='Владелец задачи',
        default=1  # Временное значение, в продакшене убрать default
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Удалена?'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата удаления'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    # Применяем менеджер мягкого удаления
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def delete(self, using=None, keep_parents=False):
        """Мягкое удаление задачи"""
        self.is_deleted = True
        self.deleted_at = now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self):
        """Полное удаление из БД"""
        super().delete()

    def restore(self):
        """Восстановление задачи"""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])

    @property
    def is_overdue(self):
        """Проверка просроченности задачи"""
        if self.deadline:
            return self.deadline < now()
        return False

    def get_subtasks_count(self):
        """Количество подзадач"""
        return self.subtasks.count()

    def get_completed_subtasks_count(self):
        """Количество выполненных подзадач"""
        return self.subtasks.filter(status='done').count()


# МОДЕЛЬ ПОДЗАДАЧИ
class SubTask(models.Model):
    """Подзадача для основной задачи"""
    STATUS_CHOICES = [
        ('not_started', 'Не начата'),
        ('in_progress', 'В процессе'),
        ('done', 'Выполнена'),
        ('blocked', 'Заблокирована'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name='Название подзадачи'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание подзадачи'
    )
    completed = models.BooleanField(
        default=False,
        verbose_name='Выполнено'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        verbose_name='Статус подзадачи'
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='subtasks',
        verbose_name='Основная задача'
    )

    # Поля владельца и мягкого удаления
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subtask_owner',
        verbose_name='Владелец подзадачи',
        default=1  # Временное значение, в продакшене убрать default
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Удалена?'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата удаления'
    )

    deadline = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Срок выполнения подзадачи'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    # Применяем менеджер мягкого удаления
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name = 'Подзадача'
        verbose_name_plural = 'Подзадачи'
        ordering = ['-created_at']

    def __str__(self):
        status_icon = "✓" if self.completed else "✗"
        return f"{self.title} {status_icon} ({self.get_status_display()})"

    def delete(self, using=None, keep_parents=False):
        """Мягкое удаление подзадачи"""
        self.is_deleted = True
        self.deleted_at = now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self):
        """Полное удаление из БД"""
        super().delete()

    def restore(self):
        """Восстановление подзадачи"""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def mark_as_done(self):
        """Отметить подзадачу как выполненную"""
        self.completed = True
        self.status = 'done'
        self.save(update_fields=['completed', 'status'])

    def update_status(self, new_status):
        """Обновить статус подзадачи"""
        if new_status in dict(self.STATUS_CHOICES):
            self.status = new_status
            if new_status == 'done':
                self.completed = True
            self.save(update_fields=['status', 'completed'])

    @property
    def is_overdue(self):
        """Проверка просроченности подзадачи"""
        if self.deadline:
            return self.deadline < now()
        return False