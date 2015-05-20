# -*- coding: utf-8 -*-
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import generic
from guardian.mixins import PermissionRequiredMixin, LoginRequiredMixin
from guardian.admin import *;
from project.models import MiembroEquipo, Proyecto, UserStory, Adjunto


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


def burndown(request, project_pk):
    project = get_object_or_404(Proyecto, pk=project_pk)
    sprint = project.sprint_set.first()
    restante = total = project.get_horas_estimadas()
    actuales = [total]
    dias = project.duracion_sprint
    for d in daterange(sprint.inicio, sprint.fin):
        notas = sprint.nota_set.filter(fecha__year=d.year, fecha__month=d.month, fecha__day=d.day)
        hwork = notas.aggregate(total=Sum('horas_registradas'))['total']
        restante -= hwork if hwork else 0
        actuales.append(restante)

    m = float(total) / dias
    data = [{'d': i, 'ideal': round(total - m * i, 2), 'actual': actuales[i]} for i in range(0, dias+1)]

    ctx = {'project': project, 'sprint': sprint, 'data': data}
    return render(request, 'project/morris.html', ctx)