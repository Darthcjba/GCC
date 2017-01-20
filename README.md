# Projectium
Projectium te permite gestionar tus proyectos usando metodologias agiles de desarrollo.

## Features
- Uso de Metodologia Scrum (Sprints y User Stories)
- Gestion de Proyectos
- Gestion de Usuarios, Roles y Permisos
- Gestion de User Stories
    - Versiones
    - Adjuntos
    - Responsables
    - Tiempos
- Control de Progreso mediante Burndown Chart
- Tablero de Progreso (Flujos Kanban)
- Interfaz de Aministracion

![Screenshot](http://i.imgur.com/snbIflS.png)

### Dependencies
- Python 2.7.x
- Django 1.7.x
- [Psycopg 2](http://initd.org/psycopg/docs/install.html "Psycopg Installation")
- [PostgreSQL 9.4.x](http://www.postgresql.org "PostgreSQL")
- [PhantomJS](http://phantomjs.org) - _Requirement to Export Reports as PDF_

### Instalation
```sh
$ git clone https://github.com/UnPolloInc/Projectium.git
$ cd Projectium
$ pip install -r requirements.txt
$ ./poblar_bd.sh
$ python manage runserver
```

### Configuration
Change according to your own database settings
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'projectium',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'ip_address',
        'PORT': 'port',
    }
}
```
# Desarrolladores
- Jordan Ayala
- Santiago Ortiz
- Guillermo Peralta
