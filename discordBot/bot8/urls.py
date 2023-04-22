from django.urls import path
from .views import TaskList, DueDate, assignUsersToTask, reminder, TaskDetail

urlpatterns = [
    path('task', TaskList.as_view()),
    path('task/<int:pk>', TaskDetail.as_view()),
    path('due-date/<int:pk>', DueDate.as_view()),
    path('assignees/<int:pk>', assignUsersToTask.as_view()),
    path('reminder/<int:pk>',reminder.as_view()),
]