from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Permission, Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import generic
from project.forms import RolForm


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class AddRolView(LoginRequiredMixin, generic.CreateView):
    model = Group
    ##TODO definir template
    form_class = RolForm
    success_url = '/'

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
    ##TODO definir template
    form_class = RolForm
    success_url = '/'

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
    success_url = '/'
    ##TODO definir template

    @method_decorator(permission_required('auth.delete_group', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteRolView, self).dispatch(request, *args, **kwargs)

def get_selected_perms(POST):
    escogidas = POST.getlist('perms_proyecto')
    escogidas.extend(POST.getlist('perms_userstory'))
    escogidas.extend(POST.getlist('perms_flujo'))
    escogidas.extend(POST.getlist('perms_sprint'))
    escogidas.extend(POST.getlist('perms_actividad'))
    return escogidas

class RolList(generic.ListView):
    model = Group
