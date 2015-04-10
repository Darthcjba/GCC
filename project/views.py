# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission, Group
from django.core.urlresolvers import reverse, reverse_lazy
from django.forms import PasswordInput
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from project.models import MiembroEquipo, Proyecto
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.views import generic
from django.forms.extras.widgets import SelectDateWidget
from project.forms import RolForm, UserEditForm, UserCreateForm
from guardian.shortcuts import get_perms
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

    @method_decorator(permission_required('auth.add_proyecto', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectCreate, self).dispatch(request, *args, **kwargs)

class ProjectUpdate(LoginRequiredMixin, generic.UpdateView):
    """
    Permite la Edicion de Proyectos
    """
    model = Proyecto
    template_name = 'project/project_form.html'
    form_class =  modelform_factory(Proyecto,
        widgets={'inicio': SelectDateWidget, 'fin': SelectDateWidget},
        fields = ('nombre_corto', 'nombre_largo', 'estado', 'inicio', 'fin', 'duracion_sprint', 'descripcion'))

    @method_decorator(permission_required('auth.change_proyecto', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectUpdate, self).dispatch(request, *args, **kwargs)

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

    @method_decorator(permission_required('auth.delete_proyecto', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
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


def get_selected_perms(POST):
    """
    Obtener los permisos marcados en el formulario
    :param POST: diccionario con los datos del formulario
    :return: lista de permisos
    """
    current_list = POST.getlist('perms_proyecto')
    current_list.extend(POST.getlist('perms_teammembers'))
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

