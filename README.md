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

## Demo
Puede entrar a la demo siguiendo el link: [http://projectium.herokuapp.com/](http://projectium.herokuapp.com/)

- Username: **demo**
- Password: **demo**

## Equipo

[![Jordan Ayala](https://avatars2.githubusercontent.com/u/6710350?v=3&s=144)](https://github.com/jmayalag) | [![Santiago Ortiz](https://avatars0.githubusercontent.com/u/11400041?v=3&s=144)](https://github.com/santiortizpy) | [![Guillermo Peralta](https://avatars1.githubusercontent.com/u/10501948?v=3&s=144)](https://github.com/voluntadpear)
---|---|---
[Jordan Ayala](https://github.com/jmayalag) | [Santiago Ortiz](https://github.com/santiortizpy) | [Guillermo Peralta](https://github.com/voluntadpear)
[jmayala@protonmail.com](mailto://jmayala@protonmail.com) | [santiortizpy@gmail.com](mailto://santiortizpy@gmail.com) | [gperaltascura@gmail.com](mailto://gperaltascura@gmail.com)

## Dependencias
- Python 2.7.x
- Django 1.7.x
- [Psycopg 2](http://initd.org/psycopg/docs/install.html "Psycopg Installation")
- [PostgreSQL 9.4.x](http://www.postgresql.org "PostgreSQL")
- [PhantomJS](http://phantomjs.org) - _Requirement to Export Reports as PDF_

# Quickstart

## Instalacion

```sh
$ git clone https://github.com/BreakingBugs/Projectium.git
$ cd Projectium
$ pip install -r requirements.txt
$ ./poblar_bd.sh
$ python manage runserver
```


## Configuracion
Cambiar de acuerdo a la configuracion de tu base de datos

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
