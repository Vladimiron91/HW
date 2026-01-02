from django.db import models
from django.utils.timezone import now


#ЗАДАНИЕ 2: Менеджер для мягкого удаления
class SoftDeleteManager(models.Manager):
    """
    Менеджер для исключения удалённых записей из стандартных запросов.
    По умолчанию возвращаются только не удалённые объекты.
    """

    def get_queryset(self):
        """
        Переопределяем метод get_queryset(),
        чтобы он по умолчанию выдавал только те записи, которые не "удалены" из базы.
        """
        return super().get_queryset().filter(is_deleted=False)

    def with_deleted(self):
        """Возвращает все объекты, включая удалённые"""
        return super().get_queryset()

    def deleted_only(self):
        """Возвращает только удалённые объекты"""
        return super().get_queryset().filter(is_deleted=True)


#МОДЕЛЬ КАТЕГОРИИ
class Category(models.Model):
    """
    Модель категории с мягким удалением.
    Задание 2: Добавлены поля is_deleted и deleted_at
    """
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

    #ЗАДАНИЕ 2: Поля для мягкого удаления
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Удалена?'
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата удаления'
    )

    #ЗАДАНИЕ 2: Переопределение менеджера
    objects = SoftDeleteManager()  # По умолчанию - только активные категории
    all_objects = models.Manager()  # Полный доступ (включая удалённые)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    #ЗАДАНИЕ 2: Метод мягкого удаления
    def delete(self, using=None, keep_parents=False):
        """
        Переопределяем метод удаления для мягкого удаления.
        Обновляет поля is_deleted=True и deleted_at=текущее время.
        """
        self.is_deleted = True
        self.deleted_at = now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self):
        """Полное удаление из базы данных"""
        super().delete()

    def restore(self):
        """Восстановление удалённой категории"""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])


#МОДЕЛЬ ЗАДАЧИ (для связи с категорией)
class Task(models.Model):
    """
    Модель задачи, связанная с категорией.
    Нужна для подсчёта задач в категории (Задание 1).
    """
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

    # Связь с категорией (для подсчёта задач)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',  # Важно для подсчёта задач!
        verbose_name='Категория'
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
            return self.deadline < now()
        return False


#МОДЕЛЬ ПОДЗАДАЧИ (опционально)
class SubTask(models.Model):
    """
    Модель подзадачи (опционально, если нужно).
    """
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