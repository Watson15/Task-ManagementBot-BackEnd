from django.db import models

class Users(models.Model):
    '''
    A model to represent a user of the bot.
    Username is used as primary key since discord
    usernames are unique
    '''
    username = models.CharField(primary_key=True, max_length=60)
    servername = models.CharField(null=True, max_length=100)

    def __str__(self):
        return self.username
    
class Task(models.Model):
    '''
    Model to represent a single task.
    Tasks can hold users who are assigned
    to the task
    '''
    title = models.CharField(max_length=60)
    due_date = models.DateTimeField(null=True)
    assignees = models.ManyToManyField(Users, blank=True, related_name='task')
    reminder = models.DateTimeField(null=True)
    guild = models.IntegerField(null=True)

    def __str__(self):
        return self.title




