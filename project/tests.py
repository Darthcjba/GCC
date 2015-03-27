from django.test import TestCase

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