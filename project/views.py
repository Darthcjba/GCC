from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from project.models import MiembroEquipo, Proyecto
from django.views.generic import ListView, DetailView

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