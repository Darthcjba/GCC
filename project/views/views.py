# -*- coding: utf-8 -*-
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import generic
from guardian.mixins import PermissionRequiredMixin, LoginRequiredMixin
from guardian.admin import *;
from project.models import MiembroEquipo, Proyecto, UserStory, Adjunto, Nota, Sprint
from random import randint


class GlobalPermissionRequiredMixin(PermissionRequiredMixin):
    '''
    Mixin que permite requerir un permiso
    '''
    accept_global_perms = True
    return_403 = True
    raise_exception = True


class CreateViewPermissionRequiredMixin(GlobalPermissionRequiredMixin):
    '''
    Mixin que permite requerir un permiso
    '''

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
    return current_list


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def generarNotas(request, sprint_pk):
    #project = get_object_or_404(Proyecto, pk=project_pk)
    sprint = get_object_or_404(Sprint, pk=sprint_pk)
    project = sprint.proyecto
    us = sprint.userstory_set.first()
    total = sprint.userstory_set.aggregate(sum=Sum('tiempo_estimado'))['sum']
    dias = project.duracion_sprint
    ini = sprint.inicio
    sprint.nota_set.all().delete()
    m = total / dias
    nota = Nota(pk=0, user_story=us, desarrollador=us.desarrollador, sprint=sprint)
    for dt in range(0, dias + 1):
        d = ini + timedelta(dt)
        nota.fecha = d
        nota.horas_registradas = randint(0, m + 2)
        nota.estado = 4 if randint(0, 100) > 90 else 2
        nota.pk += 1
        nota.save()
        while (randint(0, 100) > 60):
            nota.horas_registradas = randint(0, m + 3)
            nota.estado = 4 if randint(0, 100) > 90 else 2
            nota.pk += 1
            nota.save()
    return redirect(reverse('project:sprint_burndown', kwargs={'sprint_pk': sprint.id}))


def highchart(request, sprint_pk):
    # project = get_object_or_404(Proyecto, pk=project_pk)
    sprint = get_object_or_404(Sprint, pk=sprint_pk)
    project = sprint.proyecto
    h_restante = h_total = sprint.userstory_set.aggregate(sum=Sum('tiempo_estimado'))['sum']  # Horas estimadas de US
    h_real = [h_total]  # Lista de horas registradas
    h_ideal = [h_total]  # Lista de horas reales
    m = float(h_total) / project.duracion_sprint  # Velocidad ideal
    us_restante = us_total = sprint.userstory_set.count()  # User Stories del sprint
    us_faltante = [us_total]  # Lista de user stories que faltan
    us_completado = [0]  # Lista de user stories que se terminaron
    # today = timezone.now()
    today = sprint.fin
    for dia in daterange(sprint.inicio, sprint.fin):
        notas = sprint.nota_set.filter(fecha__year=dia.year, fecha__month=dia.month, fecha__day=dia.day)
        completados = notas.filter(estado=4).count()  # User Stories terminados en el dia
        hwork = notas.aggregate(sum=Sum('horas_registradas'))['sum']  # Total de horas registradas en el dia
        hwork = hwork if hwork else 0  # Por si aggregate devuelve None
        h_restante -= hwork if h_restante >= hwork else 0  # Si se terminan las horas antes del fin
        h_real.append(h_restante)
        h_total -= m
        h_ideal.append(round(h_total, 1))
        us_restante -= completados
        us_faltante.append(us_restante if us_restante > 0 else 0)
        us_completado.append(completados)

    ctx = {'project': project, 'sprint': sprint, 'ideal': h_ideal, 'real': h_real, 'us_faltante': us_faltante,
           'us_terminado': us_completado}
    return render(request, 'project/highchart.html', ctx)