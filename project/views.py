from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission, Group
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from project.models import MiembroEquipo, Proyecto
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.views import generic
from project.forms import RolForm

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


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


class ProjectList(LoginRequiredMixin, ListView):
    model = Proyecto
    context_object_name = 'projects'
    template_name = 'project/project_list.html'


class ProjectDetail(LoginRequiredMixin, DetailView):
    model = Proyecto
    context_object_name = 'project'
    template_name = 'project/project_detail.html'


class AddRolView(LoginRequiredMixin, generic.CreateView):
    model = Group
    template_name = 'project/rol_form.html'
    form_class = RolForm

    def get_success_url(self):
        return reverse('project:rol_detail', kwargs={'pk': self.object.id })

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

    def get_success_url(self):
        return reverse('project:rol_detail', kwargs={'pk': self.object.id })

    @method_decorator(permission_required('auth.change_group', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateRolView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        modelo = self.get_object()

        perm_list = [perm.codename for perm in list(modelo.permissions.all())]

        initial = {'perms_proyecto':perm_list, 'perms_sprint':perm_list, 'perms_userstory':perm_list,
                   'perms_flujo':perm_list, 'perms_actividad':perm_list}
        return initial


    def form_valid(self, form):
        super(UpdateRolView, self).form_valid(form)
        #eliminamos permisos anteriores
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
    list = POST.getlist('perms_proyecto')
    list.extend(POST.getlist('perms_userstory'))
    list.extend(POST.getlist('perms_flujo'))
    list.extend(POST.getlist('perms_sprint'))
    list.extend(POST.getlist('perms_actividad'))
    return list

class RolList(generic.ListView):
    model = Group
    template_name = 'project/rol_list.html'
    context_object_name = 'roles'

class RolDetail(generic.DetailView):
    model = Group
    template_name = 'project/rol_detail.html'
    context_object_name = 'rol'
