# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.core.urlresolvers import reverse, reverse_lazy
from django.forms import PasswordInput
from django.forms.models import modelform_factory, inlineformset_factory
from django.forms import PasswordInput, inlineformset_factory, CheckboxSelectMultiple
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.contrib.auth.models import User
from guardian.decorators import permission_required_or_403
from guardian.mixins import LoginRequiredMixin, PermissionRequiredMixin
from project.models import MiembroEquipo, Proyecto, Flujo, Actividad
from django.template import RequestContext
from project.models import MiembroEquipo, Proyecto
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.views import generic
from project.forms import RolForm, UserEditForm, UserCreateForm, FlujosCreateForm, ActividadFormSet, \
    PlantillaCreateForm, \
    CreateFromPlantillaForm
from guardian.shortcuts import get_perms
from django.forms.extras.widgets import SelectDateWidget
from project.forms import RolForm, UserEditForm, UserCreateForm
from guardian.shortcuts import get_perms, remove_perm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from projectium import settings


class GlobalPermissionRequiredMixin(PermissionRequiredMixin):
    accept_global_perms = True
    return_403 = True
    raise_exception = True


#TODO El GlobalPermissionRequiredMixin necesita que self.object esté definido con la instancia
#TODO sobre la cual comparar el permiso. En nuestro caso por ejemplo AddFlujo necesita saber si
#TODO el permiso create_flujo está asociado a la instancia del Proyecto y no a la de algún flujo
class CreateViewPermissionRequiredMixin(GlobalPermissionRequiredMixin):
    def get_object(self):
        return None


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
    template_name = 'project/user/user_list.html'

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
    template_name = 'project/user/user_detail.html'

    def get_context_data(self, **kwargs):
        """
        Agregar lista de proyectos al contexto

        :param kwargs: diccionario de argumentos claves
        :return: contexto
        """
        context = super(UserDetail, self).get_context_data(**kwargs)
        context['projects'] = self.object.miembroequipo_set.all()
        return context


class AddUser(LoginRequiredMixin, CreateViewPermissionRequiredMixin, generic.CreateView):
    """
    Agregar un Usuario al Sistema
    """
    model = User
    form_class = UserCreateForm
    template_name = 'project/user/user_form.html'
    permission_required = 'auth.add_user'

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


class DeleteUser(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.DeleteView):
    """
    Eliminar un Usuario del Sistema
    """
    model = User
    template_name = 'project/user/user_delete.html'
    context_object_name = 'usuario'
    success_url = reverse_lazy('project:user_list')
    permission_required = 'auth.delete_user'


class UpdateUser(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.UpdateView):
    """
    Actualizar un Usuario del Sistema
    """
    model = User
    template_name = 'project/user/user_form.html'
    permission_required = 'auth.change_user'
    form_class = modelform_factory(User, form=UserEditForm,
                                   fields=['first_name', 'last_name', 'email', 'username', 'password'], )

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

        initial = {'general_perms': perm_list}

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
    template_name = 'project/proyecto/project_list.html'
    show_cancelled = False

    def get_queryset(self):
        """
        Obtener proyectos del Sistema.

        :return: lista de proyectos
        """
        if self.request.user.has_perm('project.list_all_projects'):
            proyectos = Proyecto.objects
            return proyectos.filter(estado='CA') if self.show_cancelled else proyectos.exclude(estado='CA')
        else:
            proyectos = self.request.user.miembroequipo_set
            return [x.proyecto for x in (proyectos.filter(proyecto__estado='CA') if self.show_cancelled
                                         else proyectos.exclude(proyecto__estado='CA'))]


class ProjectDetail(LoginRequiredMixin, DetailView):
    """
    Vista de Detalles de Proyecto
    """
    model = Proyecto
    context_object_name = 'project'
    template_name = 'project/proyecto/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetail, self).get_context_data(**kwargs)
        context['team'] = self.object.miembroequipo_set.all()
        context['flows'] = self.object.flujo_set.all()
        context['sprints'] = self.object.sprint_set.all()
        return context


class ProjectCreate(LoginRequiredMixin, CreateViewPermissionRequiredMixin, generic.CreateView):
    """
    Permite la creacion de Proyectos
    """
    model = Proyecto
    permission_required = 'project.add_proyecto'
    form_class = modelform_factory(Proyecto,
                                   widgets={'inicio': SelectDateWidget, 'fin': SelectDateWidget},
                                   fields=('nombre_corto', 'nombre_largo', 'estado', 'inicio', 'fin', 'duracion_sprint',
                                           'descripcion'))
    template_name = 'project/proyecto/project_form.html'
    TeamMemberInlineFormSet = inlineformset_factory(Proyecto, MiembroEquipo, can_delete=True,
                                                    fields=['usuario', 'roles'],
                                                    extra=1,
                                                    widgets={'roles': CheckboxSelectMultiple})

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

        return render(self.request, self.get_template_names(), {'form': form, 'formset': formset},
                      context_instance=RequestContext(self.request))


class ProjectUpdate(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.UpdateView):
    """
    Permite la Edicion de Proyectos
    """
    model = Proyecto
    permission_required = 'project.change_proyecto'
    template_name = 'project/proyecto/project_form.html'
    TeamMemberInlineFormSet = inlineformset_factory(Proyecto, MiembroEquipo, can_delete=True,
                                                    fields=['usuario', 'roles'],
                                                    extra=1,
                                                    widgets={'roles': CheckboxSelectMultiple})
    form_class = modelform_factory(Proyecto,
                                   widgets={'inicio': SelectDateWidget, 'fin': SelectDateWidget},
                                   fields=('nombre_corto', 'nombre_largo', 'estado', 'inicio', 'fin', 'duracion_sprint',
                                           'descripcion'))


    def form_valid(self, form):
        '''
        actualiza los miembros del equipo del proyecto que se hayan especifico

        :param form: formulario de edición del proyecto
        '''
        self.object = form.save()
        formset = self.TeamMemberInlineFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            # borramos todos los permisos asociados al usuario en el proyecto antes de volver a asignar los nuevos
            project = self.object
            for form in formset:
                if form.has_changed():  #solo los formularios con cambios efectuados
                    user = form.cleaned_data['usuario']
                    for perm in get_perms(user, project):
                        remove_perm(perm, user, project)

            formset.save()
            return HttpResponseRedirect(self.get_success_url())

        return render(self.request, self.get_template_names(), {'form': form, 'formset': formset},
                      context_instance=RequestContext(self.request))

    def get_context_data(self, **kwargs):
        '''
        Especifica los datos de contexto a pasar al template
        :param kwargs: Diccionario con parametros con nombres clave
        '''
        context = super(ProjectUpdate, self).get_context_data(**kwargs)
        if (self.request.method == 'GET'):
            context['formset'] = self.TeamMemberInlineFormSet(instance=self.object)
        return context


class ProjectDelete(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.DeleteView):
    """
    Vista para la cancelacion de proyectos
    """
    model = Proyecto
    template_name = 'project/proyecto/proyect_delete.html'
    success_url = reverse_lazy('project:project_list')
    permission_required = 'project.delete_proyecto'

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


class AddRolView(LoginRequiredMixin, CreateViewPermissionRequiredMixin, generic.CreateView):
    '''
    View que agrega un rol al sistema
    '''

    model = Group
    template_name = 'project/rol/rol_form.html'
    form_class = RolForm
    permission_required = 'auth.add_group'

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


class UpdateRolView(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.UpdateView):
    """
    Vista de Actualizacion de Roles
    """
    model = Group
    template_name = 'project/rol/rol_form.html'
    form_class = RolForm
    permission_required = 'auth.change_group'

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
            # borramos todos los permisos que tiene asociado el usuario en el proyecto
            for perm in get_perms(user, project):
                remove_perm(perm, user, project)
            all_roles = team_member.roles.all()
            for role in all_roles:
                team_member.roles.remove(
                    role)  #desacociamos al usuario de los demas roles con los que contaba (para que se eliminen los permisos anteriores)
                team_member.roles.add(role)  #volvemos a agregar para que se copien los permisos actualizados
        return HttpResponseRedirect(self.get_success_url())


class DeleteRolView(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.DeleteView):
    """
    Vista de Eliminacion de Roles
    """
    model = Group
    template_name = 'project/rol/rol_delete.html'
    success_url = reverse_lazy('project:rol_list')
    permission_required = 'auth.delete_group'

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
        # print('team_members_set antes de borrar: ' + ' '.join([member.usuario.username for member in team_members_set]))
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
                team_member.roles.remove(
                    role)  #desacociamos al usuario de los demas roles con los que contaba (para que se eliminen los permisos anteriores)
                team_member.roles.add(role)  #volvemos a agregar para que se copien los permisos actualizados

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


class RolList(LoginRequiredMixin, generic.ListView):
    """
    Vista de Listado de Roles
    """
    model = Group
    template_name = 'project/rol/rol_list.html'
    context_object_name = 'roles'


class RolDetail(LoginRequiredMixin, generic.DetailView):
    """
    Vista de Detalles de Rol
    """
    model = Group
    template_name = 'project/rol/rol_detail.html'
    context_object_name = 'rol'


class FlujoList(LoginRequiredMixin, generic.ListView):
    """
    Vista de Listado de Flujos en el sistema
    """
    model = Flujo
    template_name = 'project/flujo/flujo_list.html'
    context_object_name = 'flujos'

    def get_queryset(self):
        project_pk = self.kwargs['project_pk']
        project = get_object_or_404(Proyecto, pk=project_pk)
        return Flujo.objects.filter(proyecto=project)


class FlujoDetail(LoginRequiredMixin, generic.DetailView):
    """
    Vista de Detalles de un flujo
    """
    model = Flujo
    template_name = 'project/flujo/flujo_detail.html'
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


class AddFlujo(LoginRequiredMixin, CreateViewPermissionRequiredMixin, generic.CreateView):
    """
    View que agrega un flujo al sistema
    """
    model = Flujo
    template_name = 'project/flujo/flujo_form.html'
    form_class = FlujosCreateForm
    permission_required = 'project.create_flujo'

    def get_context_data(self, **kwargs):
        """
        Agregar datos al contexto
        :param kwargs: argumentos clave
        :return: contexto
        """
        context = super(AddFlujo, self).get_context_data(**kwargs)
        context['current_action'] = "Agregar"
        if (self.request.method == 'GET'):
            context['actividad_form'] = ActividadFormSet()
        return context

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
        self.object = form.save(commit=False)
        self.object.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['project_pk'])
        self.object.save()
        actividad_form = ActividadFormSet(self.request.POST, instance=self.object)
        if actividad_form.is_valid():
            actividad_form.save()
            order = [form.instance.id for form in actividad_form.ordered_forms]
            self.object.set_actividad_order(order)

            return HttpResponseRedirect(self.get_success_url())

        return self.render(self.request, self.get_template_names(), {'form': form,
                                                                     'actividad_form': actividad_form},
                           context_instance=RequestContext(self.request))


class UpdateFlujo(LoginRequiredMixin, generic.UpdateView):
    """
    View que agrega un flujo al sistema
    """
    model = Flujo
    template_name = 'project/flujo/flujo_form.html'
    form_class = FlujosCreateForm
    permission_required = 'project.edit_flujo'

    def get_context_data(self, **kwargs):
        """
        Agregar datos al contexto
        :param kwargs: argumentos clave
        :return: contexto
        """
        context = super(UpdateFlujo, self).get_context_data(**kwargs)
        context['current_action'] = "Agregar"
        if (self.request.method == 'GET'):
            context['actividad_form'] = ActividadFormSet(instance=self.object)

        return context

    #Posiblemente la única forma de comprobar correctamente el permiso para nuestro caso
    #ya que usando el mixin o el decorator, se requieren condiciones que no se cumplen
    def dispatch(self, request, *args, **kwargs):
        proyecto = self.get_object().proyecto
        if 'edit_flujo' in get_perms(self.request.user, proyecto):
            return super(UpdateFlujo, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied()

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

        return self.render(self.request, self.get_template_names(), {'form': form,
                                                                     'actividad_form': actividad_form},
                           context_instance=RequestContext(self.request))


class DeleteFlujo(LoginRequiredMixin, generic.DeleteView):
    """
    Vista de Eliminacion de Flujos
    """
    model = Flujo
    template_name = 'project/flujo/flujo_delete.html'
    context_object_name = 'flujo'

    def dispatch(self, request, *args, **kwargs):
        proyecto = self.get_object().proyecto
        if 'remove_flujo' in get_perms(self.request.user, proyecto):
            return super(DeleteFlujo, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def get_success_url(self):
        return reverse_lazy('project:flujo_list', kwargs={'project_pk': self.get_object().proyecto.id})


class PlantillaList(LoginRequiredMixin, generic.ListView):
    """
    Vista de Listado de Plantillas en el sistema
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_list.html'
    context_object_name = 'plantillas'
    queryset = Flujo.objects.filter(proyecto_id=None)


class PlantillaDetail(LoginRequiredMixin, generic.DetailView):
    """
    Vista de Detalles de una Plantilla
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_detail.html'
    context_object_name = 'plantilla'


class AddPlantilla(LoginRequiredMixin, CreateViewPermissionRequiredMixin, generic.CreateView):
    """
    View que agrega un flujo al sistema
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_form.html'
    form_class = PlantillaCreateForm
    permission_required = 'project.add_flow_template'

    def get_context_data(self, **kwargs):
        """
        Agregar datos al contexto
        :param kwargs: argumentos clave
        :return: contexto
        """
        context = super(AddPlantilla, self).get_context_data(**kwargs)
        context['current_action'] = "Agregar"
        if (self.request.method == 'GET'):
            context['actividad_form'] = ActividadFormSet()
        return context

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

        return self.render(self.request, self.get_template_names(), {'form': form,
                                                                     'actividad_form': actividad_form},
                           context_instance=RequestContext(self.request))


class UpdatePlantilla(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.UpdateView):
    """
    View que agrega un flujo al sistema
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_form.html'
    form_class = PlantillaCreateForm
    permission_required = 'project.change_flow_template'

    def get_context_data(self, **kwargs):
        """
        Agregar datos al contexto
        :param kwargs: argumentos clave
        :return: contexto
        """
        context = super(UpdatePlantilla, self).get_context_data(**kwargs)
        context['current_action'] = "Actualizar"
        if (self.request.method == 'GET'):
            context['actividad_form'] = ActividadFormSet(instance=self.object)

        return context

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

        return self.render(self.request, self.get_template_names(), {'form': form,
                                                                     'actividad_form': actividad_form},
                           context_instance=RequestContext(self.request))


class DeletePlantilla(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.DeleteView):
    """
    Vista de Eliminacion de Plantillas
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_delete.html'
    context_object_name = 'plantilla'
    success_url = reverse_lazy('project:plantilla_list')
    permission_required = 'project.delete_flow_template'


class CreateFromPlantilla(LoginRequiredMixin, PermissionRequiredMixin, generic.FormView):
    '''
    Vista de creación a partir de plantillas
    '''
    template_name = 'project/flujo/flujo_createcopy.html'
    form_class = CreateFromPlantillaForm
    permission_required = 'project.create_flujo'

    def get_success_url(self):
        """
        :return:la url de redireccion a la vista de los detalles del flujo agregado.
        """
        return reverse('project:flujo_detail', kwargs={'pk': self.flujo.id})

    def form_valid(self, form):
        new_flujo = form.cleaned_data['plantilla']
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['project_pk'])
        acti_set = new_flujo.actividad_set.all()
        new_flujo.pk = None
        new_flujo.proyecto = proyecto
        new_flujo.save()
        self.flujo = new_flujo
        for actividad in acti_set:
            actividad.pk = None
            actividad.flujo = new_flujo
            actividad.save()

        return HttpResponseRedirect(self.get_success_url())



