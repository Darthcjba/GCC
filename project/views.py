from django.shortcuts import render
from django.contrib.auth.models import User
from project.models import MiembroEquipo, Proyecto

#Home simple para probar bootstrap
def home(request):
    context = {}
    context['users'] = User.objects.all()
    context['proyects'] = Proyecto.objects.all()
    context['team_members'] = MiembroEquipo.objects.all()

    return render(request, 'project/home.html', context)