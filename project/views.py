from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required, permission_required
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
from project.forms import RolForm, UserForm, UserCreateForm
from guardian.shortcuts import get_perms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


# Home simple para probar bootstrap
@login_required()
def home(request):
    context = {}
    context['users'] = User.objects.all()
    context['proyects'] = Proyecto.objects.all()
    context['team_members'] = MiembroEquipo.objects.all()

    return render(request, 'project/home.html', context)


class UserList(LoginRequiredMixin, ListView):
    model = User
    context_object_name = 'users'
    template_name = 'project/user_list.html'

    def get_queryset(self):
        return User.objects.exclude(id=-1)


class UserDetail(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'usuario'
    template_name = 'project/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super(UserDetail, self).get_context_data(**kwargs)
        context['projects'] = [x.proyecto for x in self.object.miembroequipo_set.all()]
        return context


class AddUser(LoginRequiredMixin, generic.CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'project/user_form.html'

    @method_decorator(permission_required('auth.add_group', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(AddUser, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('project:user_detail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        super(AddUser, self).form_valid(form)
        escogidas = self.request.POST.getlist('general_perms')
        for permname in escogidas:
            perm = Permission.objects.get(codename=permname)
            self.object.user_permissions.add(perm)

        return HttpResponseRedirect(self.get_success_url())


class DeleteUser(LoginRequiredMixin, generic.DeleteView):
    model = User
    template_name = 'project/user_delete.html'
    context_object_name = 'usuario'
    success_url = reverse_lazy('project:user_list')


class UpdateUser(LoginRequiredMixin, generic.UpdateView):
    model = User
    template_name = 'project/user_form.html'
    form_class = modelform_factory(User, form=UserForm,
                                   fields=['first_name', 'last_name', 'email', 'username', 'password'], )

    @method_decorator(permission_required('auth.change_group', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateUser, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('project:user_detail', kwargs={'pk': self.object.id})

    def get_initial(self):
        modelo = self.get_object()

        perm_list = [perm.codename for perm in list(modelo.user_permissions.all())]

        initial = {'general_perms':perm_list}

        return initial

    def form_valid(self, form):
        super(UpdateUser, self).form_valid(form)
        # eliminamos permisos anteriores
        self.object.user_permissions.clear()
        escogidas = self.request.POST.getlist('general_perms')
        for permname in escogidas:
            perm = Permission.objects.get(codename=permname)
            self.object.user_permissions.add(perm)

        return HttpResponseRedirect(self.get_success_url())


class ProjectList(LoginRequiredMixin, ListView):
    model = Proyecto
    context_object_name = 'projects'
    template_name = 'project/project_list.html'

    def get_queryset(self):
        if self.request.user.has_perm('project.list_all_projects'):
            return Proyecto.objects.all()
        else:
            return [x.proyecto for x in self.request.user.miembroequipo_set.all()]


class ProjectDetail(LoginRequiredMixin, DetailView):
    model = Proyecto
    context_object_name = 'project'
    template_name = 'project/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetail, self).get_context_data(**kwargs)
        #team = self.object.miembroequipo_set
        #context['product_owner'] = team.filter(rol='Product Owner')
        #context['scrum_master'] = team.filter(rol='Scrum Master')
        return context


class AddRolView(LoginRequiredMixin, generic.CreateView):
    model = Group
    template_name = 'project/rol_form.html'
    form_class = RolForm

    def get_context_data(self, **kwargs):
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
        super(AddRolView, self).form_valid(form)
        escogidas = get_selected_perms(self.request.POST)
        for permname in escogidas:
            perm = Permission.objects.get(codename=permname)
            self.object.permissions.add(perm)
        return HttpResponseRedirect(self.get_success_url())


class UpdateRolView(LoginRequiredMixin, generic.UpdateView):
    model = Group
    template_name = 'project/rol_form.html'
    form_class = RolForm

    def get_context_data(self, **kwargs):
        context = super(UpdateRolView, self).get_context_data(**kwargs)
        context['current_action'] = "Update"
        return context

    def get_success_url(self):
        return reverse('project:rol_detail', kwargs={'pk': self.object.id})

    @method_decorator(permission_required('auth.change_group', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateRolView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        modelo = self.get_object()

        perm_list = [perm.codename for perm in list(modelo.permissions.all())]

        initial = {'perms_proyecto': perm_list, 'perms_sprint': perm_list, 'perms_userstory': perm_list,
                   'perms_flujo': perm_list, 'perms_actividad': perm_list}
        return initial


    def form_valid(self, form):
        super(UpdateRolView, self).form_valid(form)
        # eliminamos permisos anteriores
        self.object.permissions.clear()
        escogidas = get_selected_perms(self.request.POST)
        for permname in escogidas:
            perm = Permission.objects.get(codename=permname)
            self.object.permissions.add(perm)

        return HttpResponseRedirect(self.get_success_url())


class DeleteRolView(generic.DeleteView):
    model = Group
    template_name = 'project/rol_delete.html'
    success_url = reverse_lazy('project:rol_list')

    @method_decorator(permission_required('auth.delete_group', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteRolView, self).dispatch(request, *args, **kwargs)


def get_selected_perms(POST):
    current_list = POST.getlist('perms_proyecto')
    current_list.extend(POST.getlist('perms_teammembers'))
    current_list.extend(POST.getlist('perms_userstory'))
    current_list.extend(POST.getlist('perms_flujo'))
    current_list.extend(POST.getlist('perms_sprint'))
    current_list.extend(POST.getlist('perms_actividad'))
    return current_list


class RolList(generic.ListView):
    model = Group
    template_name = 'project/rol_list.html'
    context_object_name = 'roles'


class RolDetail(generic.DetailView):
    model = Group
    template_name = 'project/rol_detail.html'
    context_object_name = 'rol'

