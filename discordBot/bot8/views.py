from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import F
from .serializers import TaskSerializer
from .models import Task, Users
import datetime
import pytz

class TaskList(generics.ListCreateAPIView):
    '''
    View to create and view tasks
    
    - GET "/task"
        list all tasks sorted by due date (no due dates last)
        
    - POST "/task"
        create a task (users can't be added through this endpoint)
        ex data = {"title" : "new task}
        
    - GET "/task?user=<username>
        list all tasks assigned to <username> sorted by due date
    '''
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.query_params.get('user')
        guild = self.request.query_params.get('guild')
        
        # order tasks by due date with null due dates listed last
        queryset = Task.objects.all().order_by(F('due_date').asc(nulls_last=True))
        
        # if the user parameter has been provided, only show
        # tasks assigned to the user
        if user is not None:
            queryset = queryset.filter(assignees=user)
        if guild is not None:
            queryset = queryset.filter(guild=guild)
        return queryset
    

class TaskDetail(generics.RetrieveDestroyAPIView):
    '''
    A view to delete a specific task
    
    - DELETE "/task/<id>
        deletes the task with id <id>
    '''
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

class DueDate(APIView):
    '''
    View for adding and getting due dates for a task
    
    - POST "/due-date/<id>"
        add a due date to the task with id <id>
        due date provided as "Y,M,D,H,M"
        ex data = {"due_date" : "2022,03,16,2,32"}
    - GET "/due-date/<id>"
        get the due date from the task with id <id>
        returned in format "Y-M-D H:M"
    '''
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def post(self, request, pk):
        # format due date  
        dueDate = request.data["due_date"]
        #Year, Month, Day, Hour, Minute = [int(el) for el in dueDate.split(",")]
        #d = datetime.datetime(Year, Month, Day, Hour, Minute, tzinfo = pytz.UTC)
        
        try:
            # find task at id
            task = Task.objects.filter(id=pk)[0]
        except:
            # task at id not found
            return Response(data = "A problem occured when trying to add a due date", status =status.HTTP_400_BAD_REQUEST)
        
        task.due_date=dueDate
        task.save()
        return Response (data="A Due Date has been assigned to the task!", status = status.HTTP_200_OK)
        
    
    def get(self, request, pk):
        try:
            # find task and return due date
            task = Task.objects.filter(id=pk)[0]
            DD = task.due_date
            ND = DD.strftime('%Y-%m-%d %H:%M')
            return Response (data = ND, status = status.HTTP_200_OK)
        except:
            # task at id not found
            return Response(data=None, status = status.HTTP_400_BAD_REQUEST)
        

class assignUsersToTask (APIView):
    '''
    View to add users to a task

    - PUT "assignees/<id>"
        assign users to task with id <id>
        ex data = {"assignees" : ["user1#1234", "user4#2312"]}
    '''
   
    def put(self, request, pk):
        try:
            # get the list of assignees from the data
            assignees = request.data.getlist('assignees') # not request.data['assignees']
            task = Task.objects.all().get(id=pk)
            
            # get a list of duplicate users who are already assigned to the task
            duplicate_users = task.assignees.filter(pk__in=assignees)

            # if there are duplicate users return an error
            if len(duplicate_users):
                # get list of usernames of duplicate users
                usernames = [user.username for user in duplicate_users]
                return Response(
                    data = f'User(s) {usernames} are already assigned to this task', 
                    status=status.HTTP_400_BAD_REQUEST)
            
            for assignee in assignees:
                # try to find the user with the username
                user = Users.objects.filter(username=assignee)
                
                # if the use exists then add them to the task
                if len(user):
                    task.assignees.add(user[0])
                # if the user doesn't exist then create them and add to task
                else:
                    user = Users.objects.create(username=assignee)
                    task.assignees.add(user)

            return Response(data="Added User(s)", status=status.HTTP_200_OK)
        
        except:  
            return Response(data='Failed to add user(s)', status=status.HTTP_400_BAD_REQUEST)

class reminder (APIView):
    '''
    View for adding a reminder to a task
    
    - PUT "reminder/<id>
        add a reminder to the task with id <id>
        reminder provided with standard datetime timezone format
        ex data = {"reminder" : "2023-03-26T14:40:00Z"}
    '''
    def put(self, request, pk):
        try:
            # add the reminder to the task
            reminder_date = request.data['reminder']
            task = Task.objects.all().get(id = pk)
            task.reminder = reminder_date
            task.save()

            return Response(data="Reminder has been set", status=status.HTTP_200_OK)
        
        except:
            # could not find task at id
            return Response( data= "Reminder was not set or Invalid format", status= status.HTTP_400_BAD_REQUEST)