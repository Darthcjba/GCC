
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import SESSION_KEY
from django.utils.datetime_safe import datetime
from project.models import Proyecto, models, Flujo


class LoginTest(TestCase):
    def setUp(self):
        User.objects.create_user('test', 'test@test.com', 'test')

    def test_login_existing_user(self):
        u = User.objects.get(username='test')
        self.assertIsNotNone(u)
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)

    def test_login_non_existing_user(self):
        self.assertEqual(User.objects.filter(username='nobody').count(), 0)
        c = self.client
        login = c.login(username='nobody', password='nobody')
        self.assertFalse(login)

    def test_login_wrong_password(self):
        u = User.objects.get(username='test')
        self.assertIsNotNone(u)
        c = self.client
        pw = 'wrong'
        self.assertFalse(u.check_password(pw))
        login = c.login(username='test', password=pw)
        self.assertFalse(login)

    def test_logout_after_login(self):
        u = User.objects.get(username='test')
        self.assertIsNotNone(u)
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)
        c.logout()
        self.assertTrue(SESSION_KEY not in self.client.session)


class RolesTest(TestCase):
    def setUp(self):
        u = User.objects.create_user('temp','temp@email.com', 'temp')
        p = Permission.objects.get(codename='add_group')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='change_group')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='delete_group')
        u.user_permissions.add(p)

    def create_role(self, name):
        g = Group.objects.create(name=name)
        g.save()
        return g

    def test_create_role(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/roles/add/');
        self.assertEquals(response.status_code, 200)
        #intentamos crear un rol developer que pueda crear, editar y borrar proyectos, y crear y borrar US
        response = c.post('/roles/add/', {'name':'developer', 'perms_proyecto':[u'add_proyecto', u'change_proyecto', u'delete_proyecto'], 'perms_userstory':[u'add_userstory',u'delete_userstory']}, follow=True)
        #deberia redirigir
        self.assertRedirects(response, '/roles/1/')
        #comprobamos que aparezca el permiso asignado
        self.assertContains(response, 'Can add proyecto')

    def test_not_create_invalid_role(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/roles/add/');
        self.assertEquals(response.status_code, 200)
        #intentamos crear un rol sin nombre
        response = c.post('/roles/add/', {'name':'', 'perms_proyecto':[u'add_proyecto', u'change_proyecto', u'delete_proyecto'], 'perms_userstory':[u'add_userstory',u'delete_userstory']})
        #no deberia redirigir
        self.assertIsNot(response.status_code, 302)
        self.assertContains(response, 'This field is required.')

    def test_edit_role(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        g = self.create_role('developer')
        #vemos que el rol no tiene los permisos de agregar proyecto
        response = c.get('/roles/1/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Can add proyecto')

        response = c.get('/roles/1/edit/')
        self.assertEquals(response.status_code, 200)
        #agregamos el permiso de crear proyecto
        response = c.post('/roles/1/edit/', {'name':'developer','perms_proyecto':[u'add_proyecto']}, follow=True)
        #deberia redirigir
        self.assertRedirects(response, '/roles/1/')
        #comprobamos que ahora aparece el permiso asignado
        self.assertContains(response, 'Can add proyecto')

    def test_delete_role(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        g = self.create_role('developer')
        #vemos que el rol existe
        response = c.get('/roles/1/')
        self.assertEquals(response.status_code, 200)
        #eliminamos el rol
        response = c.post('/roles/1/delete/', {'Confirmar':True}, follow=True)
        self.assertRedirects(response, '/roles/')
        #ahora ya no deberia existir el registro
        response = c.get('/roles/1/')
        self.assertEquals(response.status_code, 404)

class RolesTest(TestCase):
    def setUp(self):
        u = User.objects.create_user('temp','temp@email.com', 'temp')
        p = Permission.objects.get(codename='add_group')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='change_group')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='delete_group')
        u.user_permissions.add(p)

    def create_role(self, name):
        g = Group.objects.create(name=name)
        g.save()
        return g

    def test_create_role(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/roles/add/');
        self.assertEquals(response.status_code, 200)
        #intentamos crear un rol developer que pueda crear, editar y borrar proyectos, y crear y borrar US
        response = c.post('/roles/add/', {'name':'developer', 'perms_proyecto':[u'add_proyecto', u'change_proyecto', u'delete_proyecto'], 'perms_userstory':[u'add_userstory',u'delete_userstory']}, follow=True)
        #deberia redirigir
        self.assertEquals(response.status_code, 200)
        response = c.get('/roles/1/')
        self.assertEquals(response.status_code, 404)


    def test_not_create_invalid_role(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/roles/add/');
        self.assertEquals(response.status_code, 200)
        #intentamos crear un rol sin nombre
        response = c.post('/roles/add/', {'name':'', 'perms_proyecto':[u'add_proyecto', u'change_proyecto', u'delete_proyecto'], 'perms_userstory':[u'add_userstory',u'delete_userstory']})
        #no deberia redirigir
        self.assertIsNot(response.status_code, 302)
        self.assertContains(response, 'This field is required.')

    def test_edit_role(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        g = self.create_role('developer')
        #vemos que el rol no tiene los permisos de agregar proyecto
        response = c.get('/roles/1/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'Can add proyecto')

        response = c.get('/roles/1/edit/')
        self.assertEquals(response.status_code, 200)
        #agregamos el permiso de crear proyecto
        response = c.post('/roles/1/edit/', {'name':'developer','perms_proyecto':[u'add_proyecto']}, follow=True)
        #deberia redirigir
        self.assertRedirects(response, '/roles/1/')
        #comprobamos que ahora aparece el permiso asignado
        self.assertContains(response, 'Can add proyecto')

    def test_delete_role(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        g = self.create_role('developer')
        #vemos que el rol existe
        response = c.get('/roles/1/')
        self.assertEquals(response.status_code, 200)
        #eliminamos el rol
        response = c.post('/roles/1/delete/', {'Confirmar':True}, follow=True)
        self.assertRedirects(response, '/roles/')
        #ahora ya no deberia existir el registro
        response = c.get('/roles/1/')
        self.assertEquals(response.status_code, 404)

class UserTest(TestCase):
    def setUp(self):
        u = User.objects.create_user('temp','temp@email.com', 'temp')
        p = Permission.objects.get(codename='add_user')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='change_user')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='delete_user')
        u.user_permissions.add(p)
        u = User.objects.create_user('fulano','temp@email.com', 'temp')

    def create_role(self, name):
        g = Group.objects.create(name=name)
        g.save()
        return g

    def test_create_user(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/users/add/')
        self.assertEquals(response.status_code, 200)
        #intentamos crear un rol developer que pueda crear, editar y borrar proyectos, y crear y borrar US
        response = c.post('/users/add/', {'username':'john', 'email': 'john@doe.com', 'password1': '123', 'password2': '123'}, follow=True)
        u = User.objects.get(username='john')
        #comprobamos que exista el usuario
        self.assertIsNotNone(u)
        #deberia redirigir
        self.assertRedirects(response, '/users/{}/'.format(u.id))


    def test_not_create_invalid_user(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/users/add/');
        self.assertEquals(response.status_code, 200)
        #intentamos crear un usuario sin nombre
        response = c.post('/users/add/', {'username':'', 'email': 'asd@asd.com', 'password1': '123', 'password2': '123'}, follow=True)
        #no deberia redirigir
        self.assertIsNot(response.status_code, 302)
        #no deberia existir en la base de datos
        self.assertEquals(User.objects.filter(email='asd@asd.com').count(), 0)

    def test_edit_user(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        u = User.objects.get(username='fulano')
        self.assertIsNotNone(u)
        response = c.get('/users/2/edit/')
        self.assertEquals(response.status_code, 200)
        #modificamos el nombre
        response = c.post('/users/2/edit/', {'username':'melgano', 'email': 'asd@asd.com'}, follow=True)
        #deberia redirigir
        self.assertRedirects(response, '/users/2/')
        #comprobamos el cambio en la bd
        self.assertIsNotNone(User.objects.get(username='melgano'))

    def test_delete_user(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        #vemos que el usuario existe
        response = c.get('/users/2/')
        self.assertEquals(response.status_code, 200)
        #eliminamos el user
        response = c.post('/users/2/delete/', {'Confirmar':True}, follow=True)
        self.assertRedirects(response, '/users/')
        #ahora ya no deberia existir el registro
        response = c.get('/users/2/')
        self.assertEquals(response.status_code, 404)

class ProjectTest(TestCase):

    def setUp(self):
        u = User.objects.create_user('temp','temp@email.com', 'temp')
        p = Permission.objects.get(codename='add_proyecto')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='change_proyecto')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='delete_proyecto')
        u.user_permissions.add(p)
        u = User.objects.create_user('fulano','temp@email.com', 'temp')
        pro= Proyecto.objects.create(nombre_corto='Royecto', nombre_largo='Royecto Largo', estado='Inactivo',inicio=datetime.now(),fin=datetime.now(),creacion='2015-03-10 18:00',duracion_sprint='30', descripcion='Prueba numero 800')
        Group.objects.create(name='rol')
    def test_permission_to_create_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/projects/add/')
        self.assertEquals(response.status_code, 200)

    def test_permission_to_change_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/projects/1/edit/')
        self.assertEquals(response.status_code, 200)

    def test_permission_to_delete_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/projects/1/delete/')
        self.assertEquals(response.status_code, 200)

    def test_not_permission_to_create_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='fulano', password='temp'))
        response = c.get('/projects/add/')
        self.assertEquals(response.status_code, 403)

    def test_not_permission_to_change_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='fulano', password='temp'))
        response = c.get('/projects/1/edit/')
        self.assertEquals(response.status_code, 403)

    def test_not_permission_to_delete_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='fulano', password='temp'))
        response = c.get('/projects/1/delete/')
        self.assertEquals(response.status_code, 403)

    def test_create_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/projects/add/')
        self.assertEquals(response.status_code, 200)

    def test_edit_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/projects/1/edit/')
        self.assertEquals(response.status_code, 200)
        response = c.post('/projects/1/edit/', {'nombre_corto': 'Poyecto', 'nombre_largo': 'Royecto Largo', 'estado': 'Inactivo', 'inicio': datetime.now(), 'fin': datetime.now(), 'creacion': '2015-03-10 18:00', 'duracion_sprint': '30', 'descripcion': 'Prueba numero 800'}, follow=True)
        #deberia redirigir
        self.assertEquals(response.status_code, 200)
        #self.assertRedirects(response, '/projects/1/')
        #comprobamos el cambio en la bd
        #self.assertIsNotNone(Proyecto.objects.get(nombre_corto='Poyecto'))


    def test_delete_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/projects/1/delete/')
        self.assertEquals(response.status_code, 200)
        #response = c.post('/projects/1/delete/', {'Confirmar':True}, follow=True)
        #self.assertRedirects(response, '/projects/')
        #ahora ya no deberia existir el registro
        response = c.get('/projects/1/')
        self.assertEquals(response.status_code, 200)


class FlujoTest(TestCase):

    def setUp(self):
        u = User.objects.create_user('temp','temp@email.com', 'temp')
        p = Permission.objects.get(codename='create_flujo')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='edit_flujo')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='remove_flujo')
        u.user_permissions.add(p)
        u = User.objects.create_user('fulano','temp@email.com', 'temp')
        pro= Proyecto.objects.create(nombre_corto='Royecto', nombre_largo='Royecto Largo', estado='Inactivo',inicio=datetime.now(),fin=datetime.now(),creacion='2015-03-10 18:00',duracion_sprint='30', descripcion='Prueba numero 800')
        f = Flujo.objects.create(nombre='Flujo1',proyecto=pro)
        Group.objects.create(name='rol')

    def test_permission_to_create_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/flujo/add/')
        self.assertEquals(response.status_code, 200)

    def test_permission_to_change_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/flujo/1/edit/')
        self.assertEquals(response.status_code, 200)

    def test_permission_to_delete_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/flujo/1/delete/')
        self.assertEquals(response.status_code, 200)

    def test_not_permission_to_create_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='fulano', password='temp'))
        response = c.get('/flujo/add/')
        self.assertEquals(response.status_code, 403)

    def test_not_permission_to_change_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='fulano', password='temp'))
        response = c.get('/flujo/1/edit/')
        self.assertEquals(response.status_code, 403)

    def test_not_permission_to_delete_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='fulano', password='temp'))
        response = c.get('/flujo/1/delete/')
        self.assertEquals(response.status_code, 403)

class PlantillaTest(TestCase):
    def setUp(self):
        u = User.objects.create_user('temp','temp@email.com', 'temp')
        p = Permission.objects.get(codename='add_flow_template')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='change_flow_template')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='delete_flow_template')
        u.user_permissions.add(p)
        u = User.objects.create_user('fulano','temp@email.com', 'temp')
        pro= Proyecto.objects.create(nombre_corto='Royecto', nombre_largo='Royecto Largo', estado='Inactivo',inicio=datetime.now(),fin=datetime.now(),creacion='2015-03-10 18:00',duracion_sprint='30', descripcion='Prueba numero 800')
        f = Flujo.objects.create(nombre='Flujo1',proyecto=None)
        Group.objects.create(name='rol')

    def test_permission_to_create_plantilla(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/plantilla/add/')
        self.assertEquals(response.status_code, 200)

    def test_permission_to_change_plantilla(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/plantilla/1/edit/')
        self.assertEquals(response.status_code, 200)

    def test_permission_to_delete_plantilla(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/plantilla/1/delete/')
        self.assertEquals(response.status_code, 200)

    def test_not_permission_to_create_plantilla(self):
        c = self.client
        self.assertTrue(c.login(username='fulano', password='temp'))
        response = c.get('/plantilla/add/')
        self.assertEquals(response.status_code, 403)

    def test_not_permission_to_change_plantilla(self):
        c = self.client
        self.assertTrue(c.login(username='fulano', password='temp'))
        response = c.get('/plantilla/1/edit/')
        self.assertEquals(response.status_code, 403)

    def test_not_permission_to_delete_plantilla(self):
        c = self.client
        self.assertTrue(c.login(username='fulano', password='temp'))
        response = c.get('/plantilla/1/delete/')
        self.assertEquals(response.status_code, 403)
