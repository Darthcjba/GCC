
python CrearBasedeDatos.py
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata fixtures/initial_data.json
python manage.py test