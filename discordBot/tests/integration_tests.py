from rest_framework.test import APITransactionTestCase, APITestCase
from bot8.models import Task, Users
from rest_framework import status
from datetime import datetime

class IntegrationTest(APITestCase):
    '''Integration tests for backend API'''


    def testPostAndEditDueDate(self):
        '''
        - use post to create a task with a due date
        - use due date endpoint to edit the due date
        '''
        response_create_task = self.client.post("/task", data = {"title": "New Task"})
        self.assertEqual(response_create_task.status_code, status.HTTP_201_CREATED)
        dd_DT = datetime.strptime("2023-10-25 14:30", '%Y-%m-%d %H:%M')
        self.client.post("/due-date/1", data={"due_date":dd_DT}) 
        dd_DT = datetime.strptime("2023-11-26 14:30", '%Y-%m-%d %H:%M')
        self.client.post("/due-date/1", data={"due_date":dd_DT})
        
        response = self.client.get("/due-date/1")
        data= response.data
        print(data)
        self.assertEqual(data,'2023-11-26 14:30')


    def testPostAndEditReminder(self):
        '''
        - use post to create a task with a reminder
        - use reminder endpoint to edit the reminder
        '''
        response_create_task = self.client.post("/task", data = {"title": "New Task", "reminder":"2023-03-25T14:40:00Z"})
        self.assertEqual(response_create_task.status_code, status.HTTP_201_CREATED)
        response_reminder = self.client.put("/reminder/1", data={"reminder":"2023-03-26T14:40:00Z"})
        self.assertEqual(response_reminder.status_code,status.HTTP_200_OK)

        task = Task.objects.all().get(id=1)
        self.assertEqual(str(task.reminder),"2023-03-26 14:40:00+00:00") 

    def testPostAndAddUsers(self):
        '''
        - use post to create a task with
        - use user endpoint to add users
        '''

        self.client.post("/task", data = {"title": "New Task"})
        self.client.put("/assignees/1", data={"assignees":["user#1", "user#3"]})

        response = self.client.get("/task")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertEqual(data[0]['assignees'],["user#1", "user#3"])

    def testPostAndListWithDueDates(self):
        '''
        - use post to create tasks with due dates
        - list the tasks to make sure that they are sorted by due date
        '''
        self.client.post("/task", data={"title":"task 1"})
        self.client.post("/task", data={"title":"task 2"})
        self.client.post("/task", data={"title":"task 3"})
        dd_DT = datetime.strptime("2023-10-26 14:30", '%Y-%m-%d %H:%M')
        self.client.post("/due-date/1", data={"due_date":dd_DT}) 
        dd_DT = datetime.strptime("2023-10-25 15:13", '%Y-%m-%d %H:%M')
        self.client.post("/due-date/2", data={"due_date":dd_DT})
        dd_DT = datetime.strptime("2023-10-25 14:30", '%Y-%m-%d %H:%M')
        self.client.post("/due-date/3", data={"due_date":dd_DT}) 

        response = self.client.get("/task")
        data = response.data

        self.assertEqual(data[0]['title'], "task 3")
        self.assertEqual(data[1]['title'], "task 2")
        self.assertEqual(data[2]['title'], "task 1")


    def testPostAndListWithUsers(self):
        '''
        - use post to create tasks with users
        - list the tasks for a user to make sure only assigned tasks are shown
        '''
        self.client.post("/task", data={"title":"task 1"})
        self.client.post("/task", data={"title":"task 2"})
        self.client.post("/task", data={"title":"task 3"})

        print([task.id for task in Task.objects.all()])

        self.client.put("/assignees/1", data={"assignees":["user#1", "user#3"]})
        self.client.put("/assignees/2", data={"assignees":["user#5", "user#3"]})
        self.client.put("/assignees/3", data={"assignees":["user#1"]})

        response = self.client.get("/task?user=user#1")
        data = response.data

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], "task 1")
        self.assertEqual(data[1]['title'], "task 3")




