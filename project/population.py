import os


def populate():
    po = add_rol('Product Owner')
    dev = add_rol('Developer')
    sm = add_rol('Scrum Master')

    u = add_user('Guille')
    c = add_user('lg_ceo')
    s = add_user('Google')
    p = add_project('Shamu', 'Nexus 6')
    add_team_member(u, p, dev)
    add_team_member(c, p, po)
    add_team_member(s, p, sm)

    print "Population finished"


# TODO anhadir permisos
def add_rol(nombre, permisos=None):
    try:
        r = Group.objects.get(name=nombre)
    except Group.DoesNotExist:
        r = Group.objects.create(name=nombre)
        r.permissions.add(1)
    return r


def add_user(user, password='123'):
    try:
        u = User.objects.get(username=user)
    except User.DoesNotExist:
        u = User.objects.create_user(user, "{}@gmail.com".format(user.lower()), password)
    return u


def add_project(short, longn, sprint=30):
    try:
        p = Proyecto.objects.get(nombre_corto=short)
    except Proyecto.DoesNotExist:
        p = Proyecto.objects.get_or_create(nombre_corto=short, nombre_largo=longn, duracion_sprint=sprint,
                                           inicio=timezone.now(), fin=timezone.now())
    return p


def add_team_member(user, project, role):
    try:
        t = MiembroEquipo.objects.get(usuario=user.id, proyecto=project.id, rol=role.id)
    except MiembroEquipo.DoesNotExist:
        t = MiembroEquipo.objects.create(usuario=user, proyecto=project, rol=role)
    return t

# Start execution here!
if __name__ == '__main__':
    print "Starting Projectium population script..."
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectium.settings')
    import django

    django.setup()
    from project.models import Proyecto, MiembroEquipo
    from django.contrib.auth.models import User, Group
    from django.utils import timezone

    populate()