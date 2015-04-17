# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from guardian.mixins import PermissionRequiredMixin
from guardian.admin import *;
from project.models import MiembroEquipo, Proyecto

class GlobalPermissionRequiredMixin(PermissionRequiredMixin):
    accept_global_perms = True
    return_403 = True
    raise_exception = True

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








