from django.shortcuts import render
from django.contrib.auth.models import User
from project.models import MiembroEquipo, Proyecto
from django.views.generic import ListView, DetailView

#Home simple para probar bootstrap
def home(request):
    context = {}
    context['users'] = User.objects.all()
    context['proyects'] = Proyecto.objects.all()
    context['team_members'] = MiembroEquipo.objects.all()

    return render(request, 'project/home.html', context)

class UserList(ListView):
    model = User
    context_object_name = 'users'
    template_name = 'project/user_list.html'

class UserDetail(DetailView):
    model = User
    context_object_name = 'usuario'
    template_name = 'project/user_detail.html'


class ProjectList(ListView):
    model = Proyecto
    context_object_name = 'projects'
    template_name = 'project/project_list.html'

class ProjectDetail(DetailView):
    model = Proyecto
    context_object_name = 'project'
    template_name = 'project/project_detail.html'