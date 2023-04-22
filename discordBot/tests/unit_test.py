from rest_framework.test import APITestCase
from rest_framework import status
from bot8.models import Task, Users
from datetime import datetime

class US1Tests(APITestCase):
    '''Tests for US1 : Task Creation'''

    def setUp(self):
        self.data = {
            "title" : "newTest"
        }
        self.url = "/task"  
    
    def testTaskCreationResponeIn(self):
        '''test for checking if can post a task'''

        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def testTaskCreationActuallyAddedCount(self):
        '''test for checking if after adding a task the task count is 1'''

        self.assertEqual(Task.objects.count(), 0)
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)

    def testTaskCreationTitleThere(self):
        '''test for checking that title of task added is correct'''

        self.assertEqual(Task.objects.count(), 0)
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        get_response = self.client.get(self.url)
        responseOne = get_response.json()[0]
        self.assertEqual(responseOne["title"], self.data["title"])


class US2Tests(APITestCase):
    '''Tests for US2 : Task Assignment'''

    def setUp(self):
        # create a task in database
        # endpoint needs existing task
        Task.objects.create(title = 'newTask')

        self.data = {
            "assignees": ["Amann#4989","Jack#7654"]
        }
        self.url = "/assignees/1"
   
    def testTaskAssignment(self):
        '''
        When a task is created, users should be able to be assigned to it
        by providing a list of users and an id of a task
        '''
        response = self.client.put(path=self.url, data=self.data)

        self.assertEqual(response.status_code,status.HTTP_200_OK)
        tasks = Task.objects.all()
        self.assertEqual(1, len(tasks))
        assignees = tasks[0].assignees.all()
        self.assertEqual(2, len(assignees))
        self.assertEqual(self.data['assignees'][0], assignees[0].username)
        self.assertEqual(self.data['assignees'][1], assignees[1].username)

    def testAssigningDuplicateUser(self):
        '''
        Assigning a user to a task that they are already assigned
        to should return an error status code
        '''
        self.client.put(path=self.url, data=self.data)
        # remove first assignee from data
        self.data['assignees'].pop(0)
        # put request with single duplicate user
        response = self.client.put(path=self.url, data=self.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_message = f'User(s) {self.data["assignees"]} are already assigned to this task'
        self.assertEqual(response.data, expected_message)
    
    def testAddingUserToTaskWithUser(self):
        '''
        Adding a user to a task when the task already has a user assigned
        should not clear the existing user
        '''
        self.client.put(path=self.url, data={"assignees":["User#2345"]})
        self.assertEqual(1, len(Task.objects.get(id=1).assignees.all()))
        self.client.put(path=self.url, data={"assignees":["Another#1115"]})
        self.assertEqual(2, len(Task.objects.get(id=1).assignees.all()))


class US3Tests(APITestCase):
    '''Tests for US3 : Task Management Dashboard'''

    def testNoTasks(self):
        '''Testing to see if can display nothing if there are no tasks'''

        response = self.client.get("/task")
        self.assertEqual(response.data, [])

    
    def testDisplayMultipleTasksOrderByDueDate(self):
        '''Testing to see if can display multiple tasks ordered by due date'''

        Task.objects.create(title="Task 1", due_date="2023-03-23T14:30:00Z")
        Task.objects.create(title="Task 2", due_date="2023-03-25T14:30:00Z")
        Task.objects.create(title="Task 3", due_date="2023-03-25T13:30:00Z")
        Task.objects.create(title="Task 4", due_date="2023-03-25T13:00:00Z")
        Task.objects.create(title="Task 5", due_date="2023-04-21T14:30:00Z")
        Task.objects.create(title="Task 6", due_date="2024-01-21T14:30:00Z")
        Task.objects.create(title="Task 7", due_date="2023-03-25T14:40:00Z")
        
        response = self.client.get("/task")
        data = response.data

        self.assertEqual(data[0]['due_date'], "2023-03-23T14:30:00Z")
        self.assertEqual(data[1]['due_date'], "2023-03-25T13:00:00Z")
        self.assertEqual(data[2]['due_date'], "2023-03-25T13:30:00Z")
        self.assertEqual(data[3]['due_date'], "2023-03-25T14:30:00Z")
        self.assertEqual(data[4]['due_date'], "2023-03-25T14:40:00Z")
        self.assertEqual(data[5]['due_date'], "2023-04-21T14:30:00Z")
        self.assertEqual(data[6]['due_date'], "2024-01-21T14:30:00Z")

    def testDisplayMultipleSomeDueDates(self):
        '''
        Test to see if tasks can be listed when some have due dates set and
        some don't. Tasks with a due date should first be listed and sorted by date
        and then tasks are listed by id
        '''
        Task.objects.create(title="Task 1", due_date="2023-03-23T14:30:00Z")
        Task.objects.create(title="Task 2")
        Task.objects.create(title="Task 3", due_date="2023-03-25T13:30:00Z")
        Task.objects.create(title="Task 4")
        Task.objects.create(title="Task 5", due_date="2023-03-21T14:30:00Z")
        
        response = self.client.get("/task")
        data = response.data

        self.assertEqual(data[0]['title'], "Task 5")
        self.assertEqual(data[1]['title'], "Task 1")
        self.assertEqual(data[2]['title'], "Task 3")
        self.assertEqual(data[3]['title'], "Task 2")
        self.assertEqual(data[4]['title'], "Task 4")
        
    def testListTasksByUser(self):
        '''Testing to see if you can list tasks assigned to a user'''

        discord_name = "user#2345"

        user = Users.objects.create(username=discord_name)
        T1 = Task.objects.create(title="Task 1", due_date="2023-03-18T14:30:00Z")
        T1.assignees.set([user])
        Task.objects.create(title="Task 2", due_date="2023-03-14T14:30:00Z")
        T3 = Task.objects.create(title="Task 3", due_date="2023-03-12T14:30:00Z")
        T3.assignees.set([user])

        response = self.client.get(f'/task?user={user}')
        data = response.data    

        self.assertEqual(data[0]['due_date'], "2023-03-12T14:30:00Z")
        self.assertEqual(data[1]['due_date'], "2023-03-18T14:30:00Z")

        
class US4Tests(APITestCase):
    '''Tests for US4 : Due Date'''

    def setUp(self):
        self.data = {
            "title" : "newTest"
        }
        self.url = "/due-date/1"
        self.dd = '2023-10-25 14:30'
        self.dd_DT = datetime.strptime(self.dd, '%Y-%m-%d %H:%M')
        self.due_dateAndID = {"due_date":self.dd_DT}
        self.new_dd = '2023-11-24 14:30'
        self.new_dd_DT = datetime.strptime(self.new_dd, '%Y-%m-%d %H:%M')
        self.response = self.client.post("/task", data=self.data)

    def testNoDueDate(self):
        '''testing to see if there is no due date when first making a task'''

        get_response = self.client.get(self.url)
        self.assertIsNone(get_response.data)

    def testAddDueDate(self):
        '''testing to see if you can add a due date and it then exists'''

        self.response = self.client.post(self.url, data=self.due_dateAndID)
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.data, self.dd)

    def testChangeDueDate(self):
        '''testing to see if you can change the duedate after it is created'''

        self.response = self.client.post(self.url, data=self.due_dateAndID)
        self.due_dateAndID = {"due_date":self.new_dd_DT}
        self.response = self.client.post(self.url, data=self.due_dateAndID)
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.data, self.new_dd)

        
class US5Tests(APITestCase):
    '''Tests for US5 : Task Deletion'''
    
    def testDeleteExistingTask(self):
        '''Tests to see that task was deleted/does not exist after deletion'''

        # add Task to database, will have id 1
        Task.objects.create(title="New Task")
        self.client.delete("/task/1")
        self.assertEqual(0, len(Task.objects.all()))

    def testDeleteNonExistantTask(self):
        '''Tests that a 404 is returned when trying to delete a task which does not exist'''

        response = self.client.delete("/task/1")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class US6Tests(APITestCase):
    '''Tests for US1 : Task Reminders'''
 
    def testReminderSet(self):
        '''tests to see that an reminder date exists in the task'''

        Task.objects.create(title = 'newTask', due_date="2023-03-25T14:40:00Z")

        response = self.client.put("/reminder/1", data={"reminder":"2023-03-25T14:40:00Z"})
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        task = Task.objects.all().get(id=1)
        self.assertEqual(str(task.reminder),"2023-03-25 14:40:00+00:00")

