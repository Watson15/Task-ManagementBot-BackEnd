# serializer takes model and translates an object into a json response
from rest_framework import serializers
from .models import Task, Users

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('__all__')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('__all__')