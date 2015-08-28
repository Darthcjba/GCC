Projectium
==========
---

## Django Project Manager
Projectium uses state-of-the-art technology to make sure your Project is done right.

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
___
#### Credits
- Jordan Ayala
- Santiago Ortiz
- Guillermo Peralta
