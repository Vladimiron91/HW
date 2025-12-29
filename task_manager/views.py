from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.utils.timezone import now
from django.db.models import Count
from django.db.models.functions import ExtractWeekDay
from task_manager.models import Task, SubTask, Category
from .serializers import TaskSerializer, SubTaskSerializer, SubTaskCreateSerializer, CategorySerializer, \
    CategoryCreateSerializer, TaskDetailSerializer, TaskCreateSerializer


# ==================== СУЩЕСТВУЮЩИЕ VIEW ====================

@api_view(['POST'])
def task_create(request):
    """
    Создание задачи
    """
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def task_list(request):
    """
    Получить список всех задач
    """
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def task_detail(request, pk):
    """
    Получить задачу по ID
    """
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = TaskSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def task_stats(request):
    """
    Статистика задач
    - общее количество
    - количество по каждому статусу
    - количество просроченных задач
    """
    total = Task.objects.count()
    by_status = Task.objects.values('status').annotate(count=Count('status'))
    overdue = Task.objects.filter(deadline__lt=now()).count()

    data = {
        "total_tasks": total,
        "tasks_by_status": list(by_status),
        "overdue_tasks": overdue
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['PUT'])
def task_update(request, pk):
    """
    Обновить задачу по ID
    """
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = TaskSerializer(task, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def task_delete(request, pk):
    """
    Удалить задачу по ID
    """
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    task.delete()
    return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# ==================== ЗАДАНИЯ 1-5 (ПРЕДЫДУЩИЕ) ====================

class SubTaskListCreateView(APIView):
    """
    Класс для работы с подзадачами:
    - GET: получить список всех подзадач
    - POST: создать новую подзадачу
    """

    def get(self, request):
        """
        Получить все подзадачи
        """
        subtasks = SubTask.objects.all()
        serializer = SubTaskSerializer(subtasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Создать новую подзадачу
        Используем SubTaskCreateSerializer (задание 1)
        """
        serializer = SubTaskCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubTaskDetailUpdateDeleteView(APIView):
    """
    Класс для работы с конкретной подзадачей:
    - GET: получить подзадачу по ID
    - PUT: обновить подзадачу
    - DELETE: удалить подзадачу
    """

    def get_object(self, pk):
        """
        Вспомогательный метод для получения подзадачи по ID
        """
        try:
            return SubTask.objects.get(pk=pk)
        except SubTask.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Получить информацию о подзадаче
        """
        subtask = self.get_object(pk)

        if not subtask:
            return Response(
                {"error": "Подзадача не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SubTaskSerializer(subtask)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Обновить подзадачу
        Используем SubTaskCreateSerializer (задание 1)
        """
        subtask = self.get_object(pk)

        if not subtask:
            return Response(
                {"error": "Подзадача не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SubTaskCreateSerializer(subtask, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Удалить подзадачу
        """
        subtask = self.get_object(pk)

        if not subtask:
            return Response(
                {"error": "Подзадача не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )

        subtask.delete()
        return Response(
            {"message": "Подзадача успешно удалена"},
            status=status.HTTP_204_NO_CONTENT
        )


# Дополнительные view для демонстрации работы сериализаторов

@api_view(['GET', 'POST'])
def category_list_create(request):
    """
    Демонстрация работы CategoryCreateSerializer (задание 2)
    """
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # Используем CategoryCreateSerializer с проверкой уникальности
        serializer = CategoryCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def task_detail_with_subtasks(request, pk):
    """
    Демонстрация работы TaskDetailSerializer (задание 3)
    """
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(
            {"error": "Задача не найдена"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Используем TaskDetailSerializer с вложенными подзадачами
    serializer = TaskDetailSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def task_create_with_validation(request):
    """
    Демонстрация работы TaskCreateSerializer (задание 4)
    """
    serializer = TaskCreateSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== НОВЫЕ ЗАДАНИЯ (фильтрация и пагинация) ====================

class TaskByWeekdayView(APIView):
    """
    НОВОЕ ЗАДАНИЕ 1:
    Эндпоинт на получение списка всех задач по дню недели.
    Если никакой параметр запроса не передавался - по умолчанию выводить все записи.
    Если был передан день недели (например вторник) - выводить список задач только на этот день недели.

    Дни недели: 1=Воскресенье, 2=Понедельник, 3=Вторник, 4=Среда, 5=Четверг, 6=Пятница, 7=Суббота
    Использование: GET /api/v1/tasks-by-weekday/?weekday=2 (задачи на понедельник)
    """

    def get(self, request):
        weekday = request.query_params.get('weekday', None)

        if weekday is not None:
            try:
                weekday_int = int(weekday)
                if weekday_int < 1 or weekday_int > 7:
                    return Response(
                        {"error": "День недели должен быть от 1 (Воскресенье) до 7 (Суббота)"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Фильтруем задачи по дню недели дедлайна
                tasks = Task.objects.annotate(
                    deadline_weekday=ExtractWeekDay('deadline')
                ).filter(deadline_weekday=weekday_int)

            except ValueError:
                return Response(
                    {"error": "Параметр weekday должен быть числом от 1 до 7"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Если параметр не передан - все задачи
            tasks = Task.objects.all()

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubTaskPaginatedView(APIView, PageNumberPagination):
    """
    НОВОЕ ЗАДАНИЕ 2:
    Добавить пагинацию в отображение списка подзадач.
    На одну страницу должно отображаться не более 5 объектов.
    Отображение объектов должно идти в порядке убывания даты
    (от самого последнего добавленного объекта к самому первому)

    Использование:
    GET /api/v1/subtasks-paginated/ - первые 5 подзадач
    GET /api/v1/subtasks-paginated/?page=2 - следующие 5 подзадач
    GET /api/v1/subtasks-paginated/?page_size=10 - 10 подзадач на страницу
    """

    page_size = 5  # По умолчанию 5 подзадач на страницу
    page_size_query_param = 'page_size'  # Параметр для изменения размера страницы
    max_page_size = 100  # Максимальный размер страницы

    def get(self, request):
        # Получаем все подзадачи, отсортированные по убыванию даты создания
        subtasks = SubTask.objects.all().order_by('-created_at')

        # Применяем пагинацию
        paginated_subtasks = self.paginate_queryset(subtasks, request)

        # Сериализуем данные
        serializer = SubTaskSerializer(paginated_subtasks, many=True)

        # Возвращаем пагинированный ответ
        return self.get_paginated_response(serializer.data)


class SubTaskFilteredView(APIView, PageNumberPagination):
    """
    НОВОЕ ЗАДАНИЕ 3:
    Эндпоинт на получение списка всех подзадач по названию главной задачи и статусу подзадач.

    Если фильтр параметры в запросе не передавались - выводить данные по умолчанию, с учётом пагинации.
    Если был передан фильтр параметр названия главной задачи - выводить данные по этой главной задаче.
    Если был передан фильтр параметр конкретного статуса подзадачи - выводить данные по этому статусу.
    Если были переданы оба фильтра - выводить данные в соответствии с этими фильтрами.

    Использование:
    GET /api/v1/subtasks-filtered/ - все подзадачи с пагинацией
    GET /api/v1/subtasks-filtered/?task_title=Проект - подзадачи задачи "Проект"
    GET /api/v1/subtasks-filtered/?status=done - подзадачи со статусом "done"
    GET /api/v1/subtasks-filtered/?task_title=Проект&status=in_progress - подзадачи задачи "Проект" со статусом "in_progress"
    """

    page_size = 5  # По умолчанию 5 подзадач на страницу
    page_size_query_param = 'page_size'  # Параметр для изменения размера страницы
    max_page_size = 100

    def get(self, request):
        # Начинаем со всех подзадач, отсортированных по убыванию даты
        subtasks = SubTask.objects.all().order_by('-created_at')

        # Получаем параметры фильтрации из запроса
        task_title = request.query_params.get('task_title', None)
        status_filter = request.query_params.get('status', None)

        # Применяем фильтры, если они переданы
        if task_title:
            # Фильтруем по названию задачи (регистронезависимый поиск)
            subtasks = subtasks.filter(task__title__icontains=task_title)

        if status_filter:
            # Фильтруем по статусу подзадачи
            subtasks = subtasks.filter(status=status_filter)

        # Применяем пагинацию
        paginated_subtasks = self.paginate_queryset(subtasks, request)

        # Сериализуем данные
        serializer = SubTaskSerializer(paginated_subtasks, many=True)

        # Возвращаем пагинированный ответ
        return self.get_paginated_response(serializer.data)


# ==================== ДОПОЛНИТЕЛЬНЫЙ VIEW ДЛЯ ПРОШЛЫХ ЗАДАНИЙ ====================

@api_view(['GET'])
def task_list_old(request):
    """
    Старый эндпоинт для обратной совместимости
    Можно использовать или удалить, если не нужен
    """
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)