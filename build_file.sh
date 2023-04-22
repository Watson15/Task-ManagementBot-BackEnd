pip install -r requirements.txt 
cd discordBot 
python manage.py makemigrations 
python manage.py migrate
python manage.py test