# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission, Group
from django.core.urlresolvers import reverse, reverse_lazy
from django.forms import PasswordInput
from django.forms.models import modelform_factory, inlineformset_factory
from django.forms import PasswordInput, inlineformset_factory, CheckboxSelectMultiple
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.contrib.auth.models import User
from project.models import MiembroEquipo, Proyecto,Flujo, Actividad
from django.template import RequestContext
from project.models import MiembroEquipo, Proyecto
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.views import generic
from project.forms import RolForm, UserEditForm, UserCreateForm, FlujosCreateForm, ActividadFormSet, PlantillaCreateForm
from guardian.shortcuts import get_perms
from django.forms.extras.widgets import SelectDateWidget
from project.forms import RolForm, UserEditForm, UserCreateForm
from guardian.shortcuts import get_perms, remove_perm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class LoginRequiredMixin(object):
    """
        Mixin que exige que el usuario este logueado.
    """
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


@login_required()
def home(request):
    """
    Vista para la pantalla principal.
    """
    context = {}
    context['users'] = User.objects.all()
    context['proyects'] = Proyecto.objects.all()
    context['team_members'] = MiembroEquipo.objects.all()

    return render(request, 'project/home.html', context)


class UserList(LoginRequiredMixin, ListView):
    """
    Lista de usuarios.
    """
    model = User
    context_object_name = 'users'
    template_name = 'project/user_list.html'

    def get_queryset(self):
        """
        Retorna una los usuarios excluyendo el AnonymousUser

        :return: lista de usuarios
        """
        return User.objects.exclude(id=-1)


class UserDetail(LoginRequiredMixin, DetailView):
    """
    Ver detalles de Usuario
    """
    model = User
    context_object_name = 'usuario'
    template_name = 'project/user_detail.html'

    def get_context_data(self, **kwargs):
        """
        Agregar lista de proyectos al contexto

        :param kwargs: diccionario de argumentos claves
        :return: contexto
        """
        context = super(UserDetail, self).get_context_data(**kwargs)
        context['projects'] = self.object.miembroequipo_set.all()
        return context


class AddUser(LoginRequiredMixin, generic.CreateView):
    """
    Agregar un Usuario al Sistema
    """
    model = User
    form_class = UserCreateForm
    template_name = 'project/user_form.html'

    @method_decorator(permission_required('auth.add_user', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        """
        Requiere el permiso 'add_user'

        :param request: Request del cliente
        :param args: Lista de argumentos
        :param kwargs: Argumentos Clave
        :return: dispatch de CreateView
        """
        return super(AddUser, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        Retorna una los usuarios excluyendo el AnonymousUser

        :return: url del UserDetail
        """
        return reverse('project:user_detail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        """
        Verificar validez del formulario

        :param form: formulario completado
        :return: Url de Evento Correcto
        """
        super(AddUser, self).form_valid(form)

        escogidas = self.request.POST.getlist('general_perms')
        for permname in escogidas:
            perm = Permission.objects.get(codename=permname)
            self.object.user_permissions.add(perm)

        return HttpResponseRedirect(self.get_success_url())


class DeleteUser(LoginRequiredMixin, generic.DeleteView):
    """
    Eliminar un Usuario del Sistema
    """
    model = User
    template_name = 'project/user_delete.html'
    context_object_name = 'usuario'
    success_url = reverse_lazy('project:user_list')

    @method_decorator(permission_required('auth.delete_user', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteUser, self).dispatch(request, *args, **kwargs)

class UpdateUser(LoginRequiredMixin, generic.UpdateView):
    """
    Actualizar un Usuario del Sistema
    """
    model = User
    template_name = 'project/user_form.html'
    form_class = modelform_factory(User, form=UserEditForm,
                                   fields=['first_name', 'last_name', 'email', 'username', 'password'], )

    @method_decorator(permission_required('auth.change_user', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        """
        Requerir permiso 'change_user'

        :param request: Requeust del cliente
        :param args: Lista de Argumentos
        :param kwargs: Argumentos Clave
        :return: Dispatch de UpdateView
        """
        return super(UpdateUser, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        Obtener url de evento correcto

        :return: url de UserDetail
        """
        return reverse('project:user_detail', kwargs={'pk': self.object.id})

    def get_initial(self):
        """
        Obtener datos iniciales para el formulario

        :return: diccionario con los datos iniciales
        """
        modelo = self.get_object()

        perm_list = [perm.codename for perm in list(modelo.user_permissions.all())]

        initial = {'general_perms':perm_list}

        return initial

    def form_valid(self, form):
        """
        Comprobar validez del formulario recibido

        :param form: Formulario recibido
        :return: URL de evento correcto
        """
        super(UpdateUser, self).form_valid(form)
        # eliminamos permisos anteriores
        self.object.user_permissions.clear()
        escogidas = self.request.POST.getlist('general_perms')
        for permname in escogidas:
            perm = Permission.objects.get(codename=permname)
            self.object.user_permissions.add(perm)

        return HttpResponseRedirect(self.get_success_url())


class ProjectList(LoginRequiredMixin, ListView):
    """
    Listado de Proyectos
    """
    model = Proyecto
    context_object_name = 'projects'
    template_name = 'project/project_list.html'

    def get_queryset(self):
        """
        Obtener proyectos del Sistema.

        :return: lista de proyectos
        """
        if self.request.user.has_perm('project.list_all_projects'):
            return Proyecto.objects.exclude(estado='CA')
        else:
            return [x.proyecto for x in self.request.user.miembroequipo_set.all()]


class ProjectDetail(LoginRequiredMixin, DetailView):
    """
    Vista de Detalles de Proyecto
    """
    model = Proyecto
    context_object_name = 'project'
    template_name = 'project/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetail, self).get_context_data(**kwargs)
        context['team'] = self.object.miembroequipo_set.all()
        context['flows'] = self.object.flujo_set.all()
        context['sprints'] = self.object.sprint_set.all()
        #context['product_owner'] = team.filter(rol='Product Owner')
        #context['scrum_master'] = team.filter(rol='Scrum Master')
        return context

class ProjectCreate(LoginRequiredMixin, generic.CreateView):
    """
    Permite la creacion de Proyectos
    """
    model = Proyecto
    form_class =  modelform_factory(Proyecto,
        widgets={'inicio': SelectDateWidget, 'fin': SelectDateWidget},
        fields = ('nombre_corto', 'nombre_largo', 'estado', 'inicio', 'fin', 'duracion_sprint', 'descripcion'))
    template_name = 'project/project_form.html'
    TeamMemberInlineFormSet = inlineformset_factory(Proyecto, MiembroEquipo, can_delete=True,
                                        fields=['usuario', 'roles'],
                                        extra=1,
                                        widgets={'roles' : CheckboxSelectMultiple})

    @method_decorator(permission_required('project.add_proyecto', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        """
        Comprueba que esté el permiso de agregar proyecto
        """
        return super(ProjectCreate, self).dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super(ProjectCreate, self).get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['formset'] = self.TeamMemberInlineFormSet()
        return context

    def form_valid(self, form):
        """
        Guarda los miembros de equipo especificados asociados al proyecto.

        :param form: formulario del proyecto
        """

        self.object = form.save()
        formset = self.TeamMemberInlineFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(self.get_success_url())

        return render(self.request, self.get_template_names(), {'form' : form, 'formset' : formset},
                      context_instance=RequestContext(self.request))


class ProjectUpdate(LoginRequiredMixin, generic.UpdateView):
    """
    Permite la Edicion de Proyectos
    """
    model = Proyecto
    template_name = 'project/project_form.html'
    TeamMemberInlineFormSet = inlineformset_factory(Proyecto, MiembroEquipo, can_delete=True,
        fields=['usuario', 'roles'],
        extra=1,
        widgets={'roles' : CheckboxSelectMultiple})
    form_class =  modelform_factory(Proyecto,
        widgets={'inicio': SelectDateWidget, 'fin': SelectDateWidget},
        fields = ('nombre_corto', 'nombre_largo', 'estado', 'inicio', 'fin', 'duracion_sprint', 'descripcion'))

    @method_decorator(permission_required('project.change_proyecto', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        '''
        verifica que se cuenten con los permisos de edición de proyecto
        '''
        return super(ProjectUpdate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        '''
        actualiza los miembros del equipo del proyecto que se hayan especifico

        :param form: formulario de edición del proyecto
        '''
        self.object = form.save()
        formset = self.TeamMemberInlineFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            #borramos todos los permisos asociados al usuario en el proyecto antes de volver a asignar los nuevos
            project = self.object
            for form in formset:
                if form.has_changed(): #solo los formularios con cambios efectuados
                    user = form.cleaned_data['usuario']
                    for perm in get_perms(user, project):
                        remove_perm(perm, user, project)

            formset.save()
            return HttpResponseRedirect(self.get_success_url())

        return render(self.request, self.get_template_names(), {'form' : form, 'formset' : formset},
                      context_instance=RequestContext(self.request))

    def get_context_data(self, **kwargs):
        '''
        Especifica los datos de contexto a pasar al template
        :param kwargs: Diccionario con parametros con nombres clave
        '''
        context = super(ProjectUpdate, self).get_context_data(**kwargs)
        if(self.request.method == 'GET'):
            context['formset'] = self.TeamMemberInlineFormSet(instance=self.object)
        return context

class ProjectDelete(LoginRequiredMixin, generic.DeleteView):
    """
    Vista para la cancelacion de proyectos
    """
    model = Proyecto
    template_name = 'project/proyect_delete.html'
    success_url = reverse_lazy('project:project_list')

    def delete(self, request, *args, **kwargs):
        """
        Llama al metodo delete() del objeto
        y luego redirige a la url exitosa.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        if False:
            self.object.delete()
        else:
            self.object.estado = 'CA'
            self.object.save(update_fields=['estado'])
        return HttpResponseRedirect(success_url)

    @method_decorator(permission_required('project.delete_proyecto', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        '''
        verifica que se cuente con el permiso de eliminar proyecto
        '''
        return super(ProjectDelete, self).dispatch(request, *args, **kwargs)


class AddRolView(LoginRequiredMixin, generic.CreateView):
    '''
    View que agrega un rol al sistema
    '''

    model = Group
    template_name = 'project/rol_form.html'
    form_class = RolForm

    def get_context_data(self, **kwargs):
        """
        Agregar datos al contexto

        :param kwargs: argumentos clave
        :return: contexto
        """
        context = super(AddRolView, self).get_context_data(**kwargs)
        context['current_action'] = "Add"
        return context

    def get_success_url(self):
        """

        :return:la url de redireccion a la vista de los detalles del rol editado.
        """
        return reverse('project:rol_detail', kwargs={'pk': self.object.id})

    @method_decorator(permission_required('auth.add_group', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(AddRolView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Comprobar validez del formulario

        :param form: formulario recibido
        :return: URL de redireccion
        """
        super(AddRolView, self).form_valid(form)
        escogidas = get_selected_perms(self.request.POST)
        for permname in escogidas:
            perm = Permission.objects.get(codename=permname)
            self.object.permissions.add(perm)
        return HttpResponseRedirect(self.get_success_url())


class UpdateRolView(LoginRequiredMixin, generic.UpdateView):
    """
    Vista de Actualizacion de Roles
    """
    model = Group
    template_name = 'project/rol_form.html'
    form_class = RolForm

    def get_context_data(self, **kwargs):
        """
        Agregar datos adicionales al contexto

        :param kwargs: argumentos clave
        :return: contexto
        """
        context = super(UpdateRolView, self).get_context_data(**kwargs)
        context['current_action'] = "Update"
        return context

    def get_success_url(self):
        """
        :return: URL de redireccion correcta a UserDetail
        """
        return reverse('project:rol_detail', kwargs={'pk': self.object.id})

    @method_decorator(permission_required('auth.change_group', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        """
        Solicitar el permiso 'change_group'

        :param request: request del cliente
        :param args: lista de argumentos
        :param kwargs: argumentos clave
        :return: dispatch de UpdateView
        """
        return super(UpdateRolView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        """
        Obtener datos iniciales para el formulario

        :return: diccionario de datos iniciales
        """
        modelo = self.get_object()

        perm_list = [perm.codename for perm in list(modelo.permissions.all())]

        initial = {'perms_proyecto': perm_list, 'perms_sprint': perm_list, 'perms_userstory': perm_list,
                   'perms_flujo': perm_list, 'perms_actividad': perm_list}
        return initial


    def form_valid(self, form):
        """
        Comprobar validez del formulario

        :param form: formulario recibido
        :return: URL de redireccion correcta
        """
        super(UpdateRolView, self).form_valid(form)
        # eliminamos permisos anteriores
        self.object.permissions.clear()
        escogidas = get_selected_perms(self.request.POST)
        for permname in escogidas:
            perm = Permission.objects.get(codename=permname)
            self.object.permissions.add(perm)
        # actualizamos los permisos de los miembros de equipos que tienen este rol
        team_members_set = self.object.miembroequipo_set.all()
        for team_member in team_members_set:
            user = team_member.usuario
            project = team_member.proyecto
            #borramos todos los permisos que tiene asociado el usuario en el proyecto
            for perm in get_perms(user, project):
                remove_perm(perm, user, project)
            all_roles = team_member.roles.all()
            for role in all_roles:
                team_member.roles.remove(role) #desacociamos al usuario de los demas roles con los que contaba (para que se eliminen los permisos anteriores)
                team_member.roles.add(role) #volvemos a agregar para que se copien los permisos actualizados
        return HttpResponseRedirect(self.get_success_url())


class DeleteRolView(generic.DeleteView):
    """
    Vista de Eliminacion de Roles
    """
    model = Group
    template_name = 'project/rol_delete.html'
    success_url = reverse_lazy('project:rol_list')

    @method_decorator(permission_required('auth.delete_group', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        """
        Requerir permisos 'delete_group'

        :param request: request del cliente
        :param args: lista de argumentos
        :param kwargs: argumentos clave
        :return: dispatch de DeleteView
        """
        return super(DeleteRolView, self).dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        '''
        Borrar permisos en miembros que hayan tenido este rol asignado luego de eliminar el rol

        :param request: request del cliente
        :param args: lista de argumentos
        :param kwargs: lista de argumentos con palabras claves
        :return: HttpResponseRedirect a la nueva URL
        '''
        self.object = self.get_object()
        success_url = self.get_success_url()
        miembroequipo_set = self.object.miembroequipo_set

        # actualizamos los permisos de los miembros de equipos que tienen este rol
        team_members_set = miembroequipo_set.all()
        #print('team_members_set antes de borrar: ' + ' '.join([member.usuario.username for member in team_members_set]))
        self.object.delete()
        #print('team_members_set despues de borrar: ' + ' '.join([member.usuario.username for member in team_members_set]))
        for team_member in team_members_set:
            print('team_member')
            user = team_member.usuario
            project = team_member.proyecto
            #borramos todos los permisos que tiene asociado el usuario en el proyecto
            for perm in get_perms(user, project):
                remove_perm(perm, user, project)
            other_roles = team_member.roles.all()
            #print("other_roles= " + ' '.join([rol.name for rol in other_roles]))
            for role in other_roles:
                team_member.roles.remove(role) #desacociamos al usuario de los demas roles con los que contaba (para que se eliminen los permisos anteriores)
                team_member.roles.add(role) #volvemos a agregar para que se copien los permisos actualizados


        return HttpResponseRedirect(success_url)

def get_selected_perms(POST):
    """
    Obtener los permisos marcados en el formulario

    :param POST: diccionario con los datos del formulario
    :return: lista de permisos
    """
    current_list = POST.getlist('perms_proyecto')
    current_list.extend(POST.getlist('perms_userstory'))
    current_list.extend(POST.getlist('perms_flujo'))
    current_list.extend(POST.getlist('perms_sprint'))
    current_list.extend(POST.getlist('perms_actividad'))
    return current_list


class RolList(generic.ListView):
    """
    Vista de Listado de Roles
    """
    model = Group
    template_name = 'project/rol_list.html'
    context_object_name = 'roles'


class RolDetail(generic.DetailView):
    """
    Vista de Detalles de Rol
    """
    model = Group
    template_name = 'project/rol_detail.html'
    context_object_name = 'rol'

class FlujoList(generic.ListView):
    """
    Vista de Listado de Flujos en el sistema
    """
    model= Flujo
    template_name = 'project/flujo_list.html'
    context_object_name='flujos'

    def get_queryset(self):
        return Flujo.objects.exclude(proyecto=None)

class FlujoDetail(generic.DetailView):
    """
    Vista de Detalles de un flujo
    """
    model= Flujo
    template_name = 'project/flujo_detail.html'
    context_object_name = 'flujo'
    def get_context_data(self, **kwargs):
        """
        Agregar lista de actividades al contexto
        :param kwargs: diccionario de argumentos claves
        :return: contexto
        """
        context = super(FlujoDetail, self).get_context_data(**kwargs)
        context['actividad'] = self.object.actividad_set.all()
        return context

class AddFlujo(LoginRequiredMixin, generic.CreateView):
    """
    View que agrega un flujo al sistema
    """
    model = Flujo
    template_name = 'project/flujo_form.html'
    form_class = FlujosCreateForm
    def get_context_data(self, **kwargs):
        """
        Agregar datos al contexto
        :param kwargs: argumentos clave
        :return: contexto
        """
        context = super(AddFlujo, self).get_context_data(**kwargs)
        context['current_action'] = "Agregar"
        if(self.request.method == 'GET'):
            context['actividad_form'] = ActividadFormSet()
        return context

    @method_decorator(permission_required('add_flow_template', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        """
        Requiere el permiso 'add_flow_template'
        :param request: Request del cliente
        :param args: Lista de argumentos
        :param kwargs: Argumentos Clave
        :return: dispatch de CreateView
        """
        return super(AddFlujo, self).dispatch(request, *args, **kwargs)
    def get_success_url(self):
        """
        :return:la url de redireccion a la vista de los detalles del flujo agregado.
        """
        return reverse('project:flujo_detail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        """
        Comprobar validez del formulario. Crea una instancia de flujo para asociar con la actividad
        :param form: formulario recibido
        :param actividad_form: formulario recibido de actividad
        :return: URL de redireccion
        """
        self.object = form.save()
        actividad_form = ActividadFormSet(self.request.POST, instance=self.object)
        if actividad_form.is_valid():
            actividad_form.save()
            order = [form.instance.id for form in actividad_form.ordered_forms]
            self.object.set_actividad_order(order)

            return HttpResponseRedirect(self.get_success_url())

        return self.render(self.request, self.get_template_names(), {'form' : form,
                                                                     'actividad_form' : actividad_form},
                           context_instance=RequestContext(self.request))

class UpdateFlujo(LoginRequiredMixin, generic.UpdateView):
    """
    View que agrega un flujo al sistema
    """
    model = Flujo
    template_name = 'project/flujo_form.html'
    form_class = FlujosCreateForm
    def get_context_data(self, **kwargs):
        """
        Agregar datos al contexto
        :param kwargs: argumentos clave
        :return: contexto
        """
        context = super(UpdateFlujo, self).get_context_data(**kwargs)
        context['current_action'] = "Agregar"
        if(self.request.method == 'GET'):
            context['actividad_form'] = ActividadFormSet(instance=self.object)

        return context

    @method_decorator(permission_required('change_flow', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        """
        Requiere el permiso 'add_flow_template'
        :param request: Request del cliente
        :param args: Lista de argumentos
        :param kwargs: Argumentos Clave
        :return: dispatch de CreateView
        """
        return super(UpdateFlujo, self).dispatch(request, *args, **kwargs)
    def get_success_url(self):
        """
        :return:la url de redireccion a la vista de los detalles del flujo agregado.
        """
        return reverse('project:flujo_detail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        """
        Comprobar validez del formulario. Crea una instancia de flujo para asociar con la actividad
        :param form: formulario recibido
        :param actividad_form: formulario recibido de actividad
        :return: URL de redireccion
        """
        self.object = form.save()
        actividad_form = ActividadFormSet(self.request.POST, instance=self.object)
        if actividad_form.is_valid():
            actividad_form.save()
            order = [form.instance.id for form in actividad_form.ordered_forms]
            self.object.set_actividad_order(order)

            return HttpResponseRedirect(self.get_success_url())

        return self.render(self.request, self.get_template_names(), {'form' : form,
                                                                     'actividad_form' : actividad_form},
                           context_instance=RequestContext(self.request))

class DeleteFlujo(generic.DeleteView):
    """
    Vista de Eliminacion de Flujos
    """
    model = Flujo
    template_name = 'project/flujo_delete.html'
    context_object_name = 'flujo'
    success_url = reverse_lazy('project:flujo_list')

    @method_decorator(permission_required('delete_flow_template', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteFlujo, self).dispatch(request, *args, **kwargs)

class PlantillaList(generic.ListView):
    """
    Vista de Listado de Plantillas en el sistema
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_list.html'
    context_object_name = 'plantillas'

    def get_queryset(self):
        return Flujo.objects.filter(proyecto_id=None)

class PlantillaDetail(generic.DetailView):
    """
    Vista de Detalles de una Plantilla
    """
    model= Flujo
    template_name = 'project/plantilla/plantilla_detail.html_detail.html'
    context_object_name = 'plantilla'

class AddPlantilla(LoginRequiredMixin, generic.CreateView):
    """
    View que agrega un flujo al sistema
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_form.html'
    form_class = FlujosCreateForm

    def get_context_data(self, **kwargs):
        """
        Agregar datos al contexto
        :param kwargs: argumentos clave
        :return: contexto
        """
        context = super(AddPlantilla, self).get_context_data(**kwargs)
        context['current_action'] = "Agregar"
        if(self.request.method == 'GET'):
            context['actividad_form'] = ActividadFormSet()
        return context

    @method_decorator(permission_required('add_flow_template', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        """
        Requiere el permiso 'add_flow_template'
        :param request: Request del cliente
        :param args: Lista de argumentos
        :param kwargs: Argumentos Clave
        :return: dispatch de CreateView
        """
        return super(AddPlantilla, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        :return:la url de redireccion a la vista de los detalles del flujo agregado.
        """
        return reverse('project:plantilla_detail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        """
        Comprobar validez del formulario. Crea una instancia de flujo para asociar con la actividad
        :param form: formulario recibido
        :param actividad_form: formulario recibido de actividad
        :return: URL de redireccion
        """
        self.object = form.save()
        actividad_form = ActividadFormSet(self.request.POST, instance=self.object)
        if actividad_form.is_valid():
            actividad_form.save()
            order = [form.instance.id for form in actividad_form.ordered_forms]
            self.object.set_actividad_order(order)

            return HttpResponseRedirect(self.get_success_url())

        return self.render(self.request, self.get_template_names(), {'form' : form,
                                                                     'actividad_form' : actividad_form},
                           context_instance=RequestContext(self.request))

class UpdatePlantilla(LoginRequiredMixin, generic.UpdateView):
    """
    View que agrega un flujo al sistema
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_form.html'
    form_class = PlantillaCreateForm
    def get_context_data(self, **kwargs):
        """
        Agregar datos al contexto
        :param kwargs: argumentos clave
        :return: contexto
        """
        context = super(UpdateFlujo, self).get_context_data(**kwargs)
        context['current_action'] = "Agregar"
        if(self.request.method == 'GET'):
            context['actividad_form'] = ActividadFormSet(instance=self.object)

        return context

    @method_decorator(permission_required('change_flow', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        """
        Requiere el permiso 'add_flow_template'
        :param request: Request del cliente
        :param args: Lista de argumentos
        :param kwargs: Argumentos Clave
        :return: dispatch de CreateView
        """
        return super(UpdatePlantilla, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """
        :return:la url de redireccion a la vista de los detalles del flujo agregado.
        """
        return reverse('project:plantilla_detail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        """
        Comprobar validez del formulario. Crea una instancia de flujo para asociar con la actividad
        :param form: formulario recibido
        :param actividad_form: formulario recibido de actividad
        :return: URL de redireccion
        """
        self.object = form.save()
        actividad_form = ActividadFormSet(self.request.POST, instance=self.object)
        if actividad_form.is_valid():
            actividad_form.save()
            order = [form.instance.id for form in actividad_form.ordered_forms]
            self.object.set_actividad_order(order)

            return HttpResponseRedirect(self.get_success_url())

        return self.render(self.request, self.get_template_names(), {'form' : form,
                                                                     'actividad_form' : actividad_form},
                           context_instance=RequestContext(self.request))

class DeletePlantilla(generic.DeleteView):
    """
    Vista de Eliminacion de Plantillas
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_delete.html'
    context_object_name = 'flujo'
    success_url = reverse_lazy('project:plantilla_list')

    @method_decorator(permission_required('delete_flow_template', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DeletePlantilla, self).dispatch(request, *args, **kwargs)
