from django.db import models
from django.utils import timezone


class Task(models.Model):
    # Статусы задач
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]

    # Приоритеты задач (добавляем для задания)
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

    # Добавляем поле приоритета
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

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_overdue(self):
        """Проверка, просрочена ли задача"""
        if self.deadline:
            return self.deadline < timezone.now()
        return False

    def save(self, *args, **kwargs):
        """Переопределение метода save для дополнительной логики"""
        if self.status == 'completed' and not self.deadline:
            # Если задача завершена без срока, устанавливаем deadline на текущее время
            self.deadline = timezone.now()
        super().save(*args, **kwargs)


# === Модель категории ===
class Category(models.Model):
    """
    Модель для категорий задач.
    Нужна для задания 2 (проверка уникальности названия).
    """
    name = models.CharField(
        max_length=100,
        unique=True,  # Важно для проверки уникальности
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

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


# === Модель подзадачи ===
class SubTask(models.Model):
    """
    Модель для подзадач.
    """
    # Статусы подзадач (для задания 3 - фильтрация по статусу)
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

    # Добавляем поле статуса для задания 3
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        verbose_name='Статус подзадачи'
    )

    # Связь с основной задачей
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='subtasks',
        verbose_name='Основная задача'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Подзадача'
        verbose_name_plural = 'Подзадачи'
        ordering = ['-created_at']

    def __str__(self):
        status = "✓" if self.completed else "✗"
        return f"{self.title} {status} ({self.get_status_display()})"