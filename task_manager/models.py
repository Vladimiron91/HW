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