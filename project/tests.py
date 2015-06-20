# -*- coding: utf-8 -*-
import datetime
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import SESSION_KEY
from django.utils import timezone
import reversion
from project.models import Proyecto, Flujo, UserStory, Sprint, Actividad


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
        response = c.post('/users/add/', {'first_name': 'John', 'last_name': 'Doe', 'username':'john', 'email': 'john@doe.com', 'password1': '123', 'password2': '123'}, follow=True)
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
        #ahora ya no deberia estar activo el usuario
        response = c.get('/users/2/')
        self.assertEquals(response.status_code, 200)
        u = User.objects.get(pk=2)
        self.assertIsNotNone(u)
        self.assertFalse(u.is_active)

class ProjectTest(TestCase):

    def setUp(self):
        u = User.objects.create_superuser('temp','temp@email.com', 'temp')
        p = Permission.objects.get(codename='add_proyecto')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='change_proyecto')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='delete_proyecto')
        u.user_permissions.add(p)
        u = User.objects.create_user('fulano','temp@email.com', 'temp')
        pro= Proyecto.objects.create(nombre_corto='Royecto', nombre_largo='Royecto Largo', estado='Inactivo',inicio=timezone.now(),fin=timezone.now(),creacion='2015-03-10 18:00',duracion_sprint='30', descripcion='Prueba numero 800')
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
        response = c.post('projects/add/', {'nombre_corto': 'test', 'nombre_largo': 'test_proyecto',
                                            'descripcion': 'test', 'duracion_sprint': 30, 'inicio': timezone.now(),
                                            'fin': timezone.now()}, follow=True)
        #self.assertRedirects(response, '/projects/{}/'.format(p.id))

    def test_edit_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/projects/1/edit/')
        self.assertEquals(response.status_code, 200)
        #response = c.post('/projects/1/edit/', {'nombre_corto': 'Poyecto', 'nombre_largo': 'Royecto Largo', 'estado': 'Inactivo', 'inicio': timezone.now(), 'fin': timezone.now(), 'creacion': '2015-03-10 18:00', 'duracion_sprint': '30', 'descripcion': 'Prueba numero 800'}, follow=True)
        p = Proyecto.objects.get(pk=1)
        p.nombre_corto = 'Poyecto'
        p.save(update_fields=['nombre_corto'])
        #deberia redirigir
        self.assertEquals(response.status_code, 200)
        self.assertIsNotNone(Proyecto.objects.get(nombre_corto='Poyecto'))

    def test_delete_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get('/projects/1/delete/')
        self.assertEquals(response.status_code, 200)
        response = c.post('/projects/1/delete/', {'Confirmar':True}, follow=True)
        p = Proyecto.objects.get(pk=1)
        p.delete()
        self.assertRedirects(response, '/projects/')
        #ahora ya no deberia existir el registro
        response = c.get('/projects/1/')
        self.assertEquals(response.status_code, 404)

    def test_approve_project(self):
        c = self.client
        login = c.login(username='temp', password='temp')
        self.assertTrue(login)
        #cremaos un proyecto
        response = c.post('projects/add/', {'nombre_corto': 'test', 'nombre_largo': 'test_proyecto',
                                            'descripcion': 'test', 'duracion_sprint': 30, 'inicio': timezone.now(),
                                            'fin': timezone.now()}, follow=True)
        p = Proyecto.objects.first()
        p.estado = 'CO' #lo marcamos como terminado
        p.save()
        #nos dirigimos al formulario de aprobacion del proyecto
        response = c.get(reverse('project:project_aprobar', args=(str(p.id))))
        self.assertEquals(response.status_code, 200)
        #aprobamos el proyecto
        response = c.post(reverse('project:project_aprobar', args=(str(p.id))), data={'aprobar':'aprobar'})
        #deberia redirigir
        self.assertRedirects(response, '/projects/1/')
        #el proyecto deberia estar aprobado
        p = Proyecto.objects.first()
        self.assertEquals(p.estado, 'AP')

    def test_reject_project(self):
        c = self.client
        login = c.login(username='temp', password='temp')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        #creamos un proyecto
        response = c.post('projects/add/', {'nombre_corto': 'test', 'nombre_largo': 'test_proyecto',
                                            'descripcion': 'test', 'duracion_sprint': 30, 'inicio': timezone.now(),
                                            'fin': timezone.now()}, follow=True)
        p = Proyecto.objects.first()
        p.estado = 'CO' #lo marcamos como terminado
        p.save()
        #nos dirigimos al formulario de rechazo del proyecto
        response = c.get(reverse('project:project_aprobar', args=(str(p.id))))
        self.assertEquals(response.status_code, 200)
        #rechazamos el proyecto
        response = c.post(reverse('project:project_aprobar', args=(str(p.id))), data={'recahzar':'rechazar'})
        #deberia redirigir
        self.assertRedirects(response, '/projects/1/')
        #el proyecto deberia estar completado
        p = Proyecto.objects.first()
        self.assertNotEquals(p.estado, 'AP')
        self.assertEquals(p.estado, 'CO')

class FlujoTest(TestCase):

    def setUp(self):
        u = User.objects.create_superuser('temp','temp@email.com', 'temp')
        p = Permission.objects.get(codename='create_flujo')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='edit_flujo')
        u.user_permissions.add(p)
        p = Permission.objects.get(codename='remove_flujo')
        u.user_permissions.add(p)
        u = User.objects.create_user('fulano','temp@email.com', 'temp')
        pro= Proyecto.objects.create(nombre_corto='Royecto', nombre_largo='Royecto Largo', estado='Inactivo',inicio=timezone.now(),fin=timezone.now(),creacion='2015-03-10 18:00',duracion_sprint='30', descripcion='Prueba numero 800')
        f = Flujo.objects.create(nombre='Flujo1', proyecto=pro)
        Group.objects.create(name='rol')

    def test_permission_to_create_proyecto(self):
        c = self.client
        self.assertTrue(c.login(username='temp', password='temp'))
        response = c.get(reverse('project:flujo_add', args=('1')))
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
        response = c.get(reverse('project:flujo_add', args=('1')))
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
        pro= Proyecto.objects.create(nombre_corto='Royecto', nombre_largo='Royecto Largo', estado='Inactivo',inicio=timezone.now(),fin=timezone.now(),creacion='2015-03-10 18:00',duracion_sprint='30', descripcion='Prueba numero 800')
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

class UserStoryTest(TestCase):
    def setUp(self):
        u = User.objects.create_superuser('test', 'test@test.com', 'test') #Superusuario con todos los permisos
        u2 = User.objects.create_user('none', 'none@none.com', 'none') #Usuario sin permisos
        p = Proyecto.objects.create(nombre_corto='Test Project', nombre_largo='Test Project name', estado='Inactivo',
                                    inicio=timezone.now(), fin=timezone.now(), creacion='2015-03-10 18:00',
                                    duracion_sprint='30', descripcion='Test')

    def test_add_userstory_with_permission(self):
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        #deberia existir
        self.assertIsNotNone(p)
        response = c.get(reverse('project:userstory_add', args=(str(p.id))))
        self.assertEquals(response.status_code, 200)
        response = c.post(reverse('project:userstory_add', args=(str(p.id))),
            {'nombre':'Test User story', 'descripcion':'This is a User Story for testing purposes.', 'prioridad': 1,
             'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        #deberia redirigir
        self.assertRedirects(response, '/userstory/1/')
        us = UserStory.objects.get(pk=1)
        self.assertIsNotNone(us)
        response = c.get(reverse('project:userstory_detail', args=(str(us.id))))
        self.assertEquals(response.status_code, 200)

    def test_add_userstory_no_permission(self):
        c = self.client
        login = c.login(username='none', password='none')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        #deberia existir
        self.assertIsNotNone(p)
        response = c.get(reverse('project:userstory_add', args=(str(p.id))))
        #debería rechazar (403 - Permiso denegado)
        self.assertEquals(response.status_code, 403)
        response = c.post(reverse('project:userstory_add', args=(str(p.id))),
            {'nombre':'Test User story', 'descripcion':'This is a User Story for testing purposes.', 'prioridad': 1,
             'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        #no debería haber creado user story
        response = c.get(reverse('project:userstory_detail', args=(str(1))))
        self.assertEquals(response.status_code, 404)

    def test_update_userstory_with_permission(self):
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        #creamos un user story
        response = c.post(reverse('project:userstory_add', args=(str(p.id))),
            {'nombre':'First Value US', 'descripcion':'This is a User Story for testing purposes.', 'prioridad': 1,
             'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        us = UserStory.objects.first()
        self.assertIsNotNone(us)
        self.assertEquals(us.nombre, 'First Value US')
        response = c.get(reverse('project:userstory_detail', args=(str(us.id))))
        self.assertEquals(response.status_code, 200)
        #nos vamos a la página de edición de user story
        response = c.get(reverse('project:userstory_update', args=(str(us.id))))
        #debería retornar 200
        self.assertEquals(response.status_code, 200)
        response = c.post(reverse('project:userstory_update', args=(str(p.id))),
            {'nombre':'Second Value US', 'descripcion':'This is a User Story for testing purposes.', 'prioridad': 1,
             'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        self.assertRedirects(response, '/userstory/1/')
        us = UserStory.objects.first()
        self.assertIsNotNone(us)
        #vemos que el nombre ya no es el anterior
        self.assertNotEquals(us.nombre, 'First Value US')
        self.assertEquals(us.nombre, 'Second Value US')

    def test_update_userstory_no_permission(self):
        c = self.client
        login = c.login(username='none', password='none')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        #creamos un user story
        response = c.post(reverse('project:userstory_add', args=(str(p.id))),
            {'nombre':'First Value US', 'descripcion':'This is a User Story for testing purposes.', 'prioridad': 1,
             'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        us = UserStory.objects.first()
        #No debío haber creado el userstory
        self.assertEquals(response.status_code, 403)
        self.assertIsNone(us)

    def test_registraractividad_userstory_with_permission(self):
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        #creamos un user story
        response = c.post(reverse('project:userstory_add', args=(str(p.id))),
            {'nombre':'First Value US', 'descripcion':'This is a User Story for testing purposes.', 'prioridad': 1,
             'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        us = UserStory.objects.first()
        self.assertIsNotNone(us)
        self.assertEquals(us.nombre, 'First Value US')
        s = Sprint.objects.create(nombre="Sprint 1", inicio=timezone.now(), fin=timezone.now() + datetime.timedelta(days=30), proyecto=p)
        f = Flujo.objects.create(nombre="Implementación", proyecto=p)
        a1 = Actividad.objects.create(name="Analisis", flujo=f)
        a2 = Actividad.objects.create(name="Desarrollo", flujo=f)
        us.actividad = a2
        us.estado = 1 #Estado en curso
        us.sprint = s
        us.desarrollador = p.equipo.first()
        us.save()
        response = c.get(reverse('project:userstory_detail', args=(str(us.id))))
        self.assertEquals(response.status_code, 200)
        #nos vamos a la página de registrar actividad de user story
        response = c.get(reverse('project:userstory_registraractividad', args=(str(us.id))))
        #debería retornar 200
        self.assertEquals(response.status_code, 200)

        post_data = {
            'actividad': 1,
            'horas_a_registrar': 4,
            'estado_actividad': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-MIN_NUM_FORMS': 0,
            'form-TOTAL_FORMS': 1,
            'form-0-mensaje': 'Mensaje',
            'form-0-fecha': '2015-05-29 17:56:16',
        }
        response = c.post(reverse('project:userstory_registraractividad', args=(str(us.id))),post_data, follow=True)
        self.assertRedirects(response, '/userstory/1/')
        us = UserStory.objects.first()
        self.assertIsNotNone(us)
        nota = us.nota_set.last()
        #se creo una nota
        self.assertIsNotNone(nota)
        self.assertEquals(nota.mensaje, 'Mensaje')

    def test_registraractividad_userstory_no_permission(self):
        c = self.client
        login = c.login(username='none', password='none')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        #creamos un user story
        us = UserStory()
        us.nombre = 'First Value US'
        us.descripcion = "This is a User Story for test purposes."
        us.prioridad = 1
        us.valor_tecnico = 10
        us.valor_negocio = 10
        us.tiempo_estimado = 10
        us.proyecto = p
        s = Sprint.objects.create(nombre="Sprint 1", inicio=timezone.now(), fin=timezone.now() + datetime.timedelta(days=30), proyecto=p)
        f = Flujo.objects.create(nombre="Implementación", proyecto=p)
        a1 = Actividad.objects.create(name="Analisis", flujo=f)
        a2 = Actividad.objects.create(name="Desarrollo", flujo=f)
        us.actividad = a2
        us.sprint = s
        us.desarrollador = p.equipo.first()
        us.save()
        response = c.get(reverse('project:userstory_detail', args=(str(us.id))))
        #no deberia poder ver User Story recien creado
        self.assertEquals(response.status_code, 403)
        #nos vamos a la página de registrar actividad de user story
        response = c.get(reverse('project:userstory_registraractividad', args=(str(us.id))))
        #debería retornar 403
        self.assertEquals(response.status_code, 403)


    def test_delete_userstory_with_permission(self):
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        #creamos un user story
        response = c.post(reverse('project:userstory_add', args=(str(p.id))),
            {'nombre':'First Value US', 'descripcion':'This is a User Story for testing purposes.', 'prioridad': 1,
             'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        us = UserStory.objects.first()
        self.assertIsNotNone(us)
        #nos vamos a la página de borrado de user story
        response = c.get(reverse('project:userstory_delete', args=(str(us.id))))
        #debería retornar 200
        self.assertEquals(response.status_code, 200)
        response = c.post(reverse('project:userstory_delete', args=(str(p.id))),
            {'Confirmar':True}, follow=True)
        us = UserStory.objects.first()
        #No debería existir
        self.assertIsNone(us)

    def test_list_userstories_with_permission(self):
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        #listamos user stories del proyecto
        response = c.get(reverse('project:product_backlog', args=(str(p.id))))
        self.assertEquals(response.status_code, 200)

    def test_list_userstories_no_permission(self):
        c = self.client
        login = c.login(username='none', password='none')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        #listamos user stories del proyecto
        response = c.get(reverse('project:product_backlog', args=(str(p.id))))
        self.assertEquals(response.status_code, 403)

    def test_approve_userstory(self):
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        #creamos un user story
        response = c.post(reverse('project:userstory_add', args=(str(p.id))),
            {'nombre':'First Value US', 'descripcion':'This is a User Story for testing purposes.', 'prioridad': 1,
             'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        us = UserStory.objects.first()
        self.assertIsNotNone(us)
        self.assertEquals(us.nombre, 'First Value US')
        s = Sprint.objects.create(nombre="Sprint 1", inicio=timezone.now(), fin=timezone.now() + datetime.timedelta(days=30), proyecto=p)
        f = Flujo.objects.create(nombre="Implementación", proyecto=p)
        a1 = Actividad.objects.create(name="Analisis", flujo=f)
        a2 = Actividad.objects.create(name="Desarrollo", flujo=f)
        us.actividad = a2
        us.estado = 2 #Estado Pendiente de aprobacion
        us.estado_actividad = 2
        us.sprint = s
        us.desarrollador = p.equipo.first()
        us.save()
        #nos dirigimos al formulario de aprobacion del userstory
        response = c.get(reverse('project:userstory_aprobar', args=(str(us.id))))
        self.assertEquals(response.status_code, 200)
        #aprobamos el userstory
        response = c.post(reverse('project:userstory_aprobar', args=(str(us.id))))
        #deberia redirigir
        self.assertRedirects(response, '/projects/1/userstories/')
        #el userstory deberia estar aprobado
        us = UserStory.objects.first()
        self.assertEquals(us.estado, 3)

    def test_reject_userstory(self):
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        #creamos un user story
        response = c.post(reverse('project:userstory_add', args=(str(p.id))),
            {'nombre':'First Value US', 'descripcion':'This is a User Story for testing purposes.', 'prioridad': 1,
             'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        us = UserStory.objects.first()
        self.assertIsNotNone(us)
        self.assertEquals(us.nombre, 'First Value US')
        s = Sprint.objects.create(nombre="Sprint 1", inicio=timezone.now(), fin=timezone.now() + datetime.timedelta(days=30), proyecto=p)
        f = Flujo.objects.create(nombre="Implementación", proyecto=p)
        a1 = Actividad.objects.create(name="Analisis", flujo=f)
        a2 = Actividad.objects.create(name="Desarrollo", flujo=f)
        us.actividad = a2
        us.estado = 2 #Estado Pendiente de aprobacion
        us.estado_actividad = 2
        us.sprint = s
        us.desarrollador = p.equipo.first()
        us.save()
        #nos dirigimos al formulario de rechazo del userstory
        response = c.get(reverse('project:userstory_rechazar', args=(str(us.id))))
        self.assertEquals(response.status_code, 200)
        #rechazamos el userstory
        response = c.post(reverse('project:userstory_rechazar', args=(str(us.id))), {'actividad':a2.id, 'estado_actividad':0})
        #deberia redirigir
        self.assertRedirects(response, '/userstory/1/')
        #el userstory deberia estar en curso de vuelta
        us = UserStory.objects.first()
        self.assertEquals(us.estado, 1)

    def test_pending_userstory(self):
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        #creamos un user story
        response = c.post(reverse('project:userstory_add', args=(str(p.id))),
            {'nombre':'First Value US', 'descripcion':'This is a User Story for testing purposes.', 'prioridad': 1,
             'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        us = UserStory.objects.first()
        self.assertIsNotNone(us)
        self.assertEquals(us.nombre, 'First Value US')
        s = Sprint.objects.create(nombre="Sprint 1", inicio=timezone.now(), fin=timezone.now() + datetime.timedelta(days=30), proyecto=p)
        f = Flujo.objects.create(nombre="Implementación", proyecto=p)
        a1 = Actividad.objects.create(name="Analisis", flujo=f)
        a2 = Actividad.objects.create(name="Desarrollo", flujo=f)
        us.actividad = a2
        us.estado = 1 #Estado En Curso
        us.estado_actividad = 2
        us.sprint = s
        us.desarrollador = p.equipo.first()
        us.save()
        response = c.get(reverse('project:pending_userstories', args=(str(p.id))))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "No hay User Stories pendientes de aprobación.")
        us.estado = 2 #Estado Pendiente de Aprobacion
        us.save()
        response = c.get(reverse('project:pending_userstories', args=(str(p.id))))
        self.assertNotContains(response, "No hay User Stories pendientes de aprobación.")

class VersionTest(TestCase):
    def setUp(self):
        u = User.objects.create_superuser('test', 'test@test.com', 'test')
        u2 = User.objects.create_user('none', 'none@none.com', 'none')
        p = Proyecto.objects.create(nombre_corto='Project', nombre_largo='Project name', estado='Inactivo',
                                    inicio=timezone.now(), fin=timezone.now(), creacion='2015-03-10 18:00',
                                    duracion_sprint='30', descripcion='Test')
        us = UserStory.objects.create(nombre='User Story', descripcion='Test Description', prioridad=1,
                                      valor_negocio=10, valor_tecnico=10, tiempo_estimado=10, proyecto_id=1)
        # g = Group.objects.create()

    def test_version_no_permission(self):
        c = self.client
        login = c.login(username='none', password='none')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        self.assertIsNotNone(p)
        us = UserStory.objects.get(pk=1)
        self.assertIsNotNone(us)
        response = c.get(reverse('project:version_list', args=(str(us.id))))
        self.assertEquals(response.status_code, 403)

    def test_version_with_permission(self):
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        self.assertIsNotNone(p)
        us = UserStory.objects.get(pk=1)
        self.assertIsNotNone(us)
        response = c.get(reverse('project:version_list', args=(str(us.id))))
        self.assertEquals(response.status_code, 200)

    def test_initial_version(self):
        u = User.objects.get(username='test')
        self.assertIsNotNone(u)
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        self.assertIsNotNone(p)
        response = c.get(reverse('project:userstory_add', args=(str(p.id))))
        self.assertEquals(response.status_code, 200)
        response = c.post(reverse('project:userstory_add', args=(str(p.id))),
                          {'nombre': 'Test_Version', 'descripcion': 'Test Description', 'prioridad': 1,
                           'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        # deberia redirigir
        self.assertRedirects(response, '/userstory/2/')
        us = UserStory.objects.get(pk=2)
        self.assertIsNotNone(us)
        # se debe crear una version inicial
        v = reversion.get_for_object(us)[0]
        self.assertIsNotNone(v)


    def test_update_version(self):
        u = User.objects.get(username='test')
        self.assertIsNotNone(u)
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)
        us = UserStory.objects.first()
        self.assertIsNotNone(us)
        response = c.get(reverse('project:userstory_update', args=(str(us.id))))
        self.assertEquals(response.status_code, 200)
        response = c.post(reverse('project:userstory_update', args=(str(us.id))),
                           {'nombre': 'User Story Mod', 'descripcion': 'Test Description', 'prioridad': 1,
                           'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        self.assertRedirects(response, reverse('project:userstory_detail', args=(str(us.id))))
        # se debe crear una version de actualizacion
        v = reversion.get_for_object(us)[0]
        self.assertIsNotNone(v)
        # comprobamos que sea la version correcta
        self.assertEquals(str(v), 'User Story Mod')

    def test_revert_version(self):
        c = self.client
        login = c.login(username='test', password='test')
        self.assertTrue(login)
        p = Proyecto.objects.first()
        self.assertIsNotNone(p)
        response = c.get(reverse('project:userstory_add', args=(str(p.id))))
        self.assertEquals(response.status_code, 200)
        response = c.post(reverse('project:userstory_add', args=(str(p.id))),
                          {'nombre': 'Test_Version_Initial', 'descripcion': 'Test Description', 'prioridad': 1,
                           'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        # deberia redirigir
        self.assertRedirects(response, '/userstory/2/')
        us = UserStory.objects.get(pk=2)
        self.assertIsNotNone(us)
        response = c.get(reverse('project:userstory_update', args=(str(us.id))))
        self.assertEquals(response.status_code, 200)
        response = c.post(reverse('project:userstory_update', args=(str(us.id))),
                           {'nombre': 'Test_Version_Mod', 'descripcion': 'Test Description', 'prioridad': 1,
                           'valor_negocio': 10, 'valor_tecnico': 10, 'tiempo_estimado': 10}, follow=True)
        self.assertRedirects(response, reverse('project:userstory_detail', args=(str(us.id))))
        # comprobamos que se modifico
        us = UserStory.objects.get(nombre='Test_Version_Mod')
        self.assertIsNotNone(us)
        # revertimos a la version inicial
        v = reversion.get_for_object(us)[1]
        self.assertIsNotNone(v)
        response = c.get(reverse('project:version_revert', args=(str(us.id), str(v.id))))
        self.assertEquals(response.status_code, 200)
        initial = response.context['form'].initial
        response = c.post(reverse('project:version_revert', args=(str(us.id), str(v.id))), initial, follow=True)
        self.assertRedirects(response, reverse('project:userstory_detail', args=(str(us.id))))
        # comprobamos que se volvio a la version inicial
        us = UserStory.objects.get(pk=2)
        self.assertEquals(us.nombre, 'Test_Version_Initial')

class SprintTest(TestCase):

        def setUp(self):
            u = User.objects.create_superuser('temp','temp@email.com', 'temp')
            pro= Proyecto.objects.create(nombre_corto='Royecto', nombre_largo='Royecto Largo', estado='IN',inicio=timezone.now(),fin=timezone.now(),creacion=timezone.now(), duracion_sprint='30', descripcion='Prueba numero 800')
            User.objects.create_user('tempdos', 'tempdos@email.com', 'tempdos')
            UserStory.objects.create(nombre= 'Test_Version', descripcion= 'Test Description', prioridad= 1,
                           valor_negocio= 10, valor_tecnico= 10, tiempo_estimado =10, proyecto = pro)
            f=Flujo.objects.create(nombre ='flujo_test', proyecto= pro)
            Actividad.objects.create(name='actividad_test', flujo=f)
            Sprint.objects.create(nombre='sprint_test',inicio=timezone.now(),fin=timezone.now(), proyecto=pro)

        def test_to_create_sprint(self):
            c = self.client
            self.assertTrue(c.login(username='temp', password='temp'))
            p= Proyecto.objects.first()
            self.assertIsNotNone(p)
            us=UserStory.objects.first()
            self.assertIsNotNone(us)
            u=User.objects.first()
            self.assertIsNotNone(u)
            f=User.objects.first()
            self.assertIsNotNone(f)
            response = c.get(reverse('project:sprint_add', args=(str(p.id))))
            self.assertEquals(response.status_code, 200)
            post_data = {
            'nombre': 'Sprint_test',
            'inicio': timezone.now(),
            'proyecto':p,
            'fin':timezone.now(),
            'actividad': 1,
            'tiempo_registrado': 4,
            'estado_actividad': 1,
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': 1000,
            'form-MIN_NUM_FORMS': 0,
            'form-TOTAL_FORMS': 1,
            'form-0-userStory': us.id,
            'form-0-desarrollador':u.id,
            'form-0-flujo':f.id,
        }
            response = c.post(reverse('project:sprint_add', args=(str(p.id))), post_data, follow=True)
            self.assertEquals(response.status_code,200)
            s=Sprint.objects.get(pk=1)
            self.assertIsNotNone(s)
            #self.assertRedirects(response, '/sprint/1/')

        def test_to_edit_sprint(self):
            c = self.client
            self.assertTrue(c.login(username='temp', password='temp'))
            p= Proyecto.objects.first()
            self.assertIsNotNone(p)
            us=UserStory.objects.first()
            self.assertIsNotNone(us)
            u=User.objects.first()
            self.assertIsNotNone(u)
            f=Flujo.objects.create(nombre ='flujo_test2', proyecto= p)
            Actividad.objects.create(name='actividad_test2', flujo=f)
            self.assertIsNotNone(f)
            s=Sprint.objects.get(pk=1)
            response = c.get(reverse('project:sprint_add', args=(str(s.id))))
            self.assertEquals(response.status_code, 200)
            post_data = {
                'nombre': 'Sprint_test',
                'inicio': timezone.now(),
                'fin':timezone.now(),
                'proyecto':p,
                'form-INITIAL_FORMS': 0,
                'form-MAX_NUM_FORMS': 1000,
                'form-MIN_NUM_FORMS': 0,
                'form-TOTAL_FORMS': 1,
                'form-0-userStory': us.id,
                'form-0-desarrollador':u.id,
                'form-0-flujo':f.id,
            }
            response = c.post(reverse('project:sprint_update',args=(str(s.id))),
                          post_data, follow=True)
            self.assertEquals(response.status_code,200)


        def test_permission_to_create_sprint(self):
            c = self.client
            self.assertTrue(c.login(username='temp', password='temp'))
            p= Proyecto.objects.first()
            self.assertIsNotNone(p)
            response = c.get(reverse('project:sprint_add', args=(str(p.id))))
            self.assertEquals(response.status_code, 200)

        def test_permission_to_no_create_sprint(self):
            c = self.client
            self.assertTrue(c.login(username='tempdos', password='tempdos'))
            p= Proyecto.objects.first()
            self.assertIsNotNone(p)
            response = c.get(reverse('project:sprint_add', args=(str(p.id))))
            self.assertEquals(response.status_code, 403)

        def test_permission_to_edit_sprint(self):
            c = self.client
            self.assertTrue(c.login(username='temp', password='temp'))
            p= Proyecto.objects.first()
            self.assertIsNotNone(p)
            s=Sprint.objects.first()
            response = c.get(reverse('project:sprint_update', args=(str(s.id))))
            self.assertEquals(response.status_code, 200)

        def test_permission_to_no_edit_sprint(self):
            c = self.client
            self.assertTrue(c.login(username='tempdos', password='tempdos'))
            p= Proyecto.objects.first()
            self.assertIsNotNone(p)
            s=Sprint.objects.first()
            response = c.get(reverse('project:sprint_update', args=(str(s.id))))
            self.assertEquals(response.status_code, 403)
