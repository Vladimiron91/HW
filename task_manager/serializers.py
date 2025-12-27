from rest_framework.serializers import ModelSerializer
from task_manager.models import Task

class TaskSerializer(ModelSerializer):
        class Meta:
            model = Task
            fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at']