# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views import generic
from guardian.mixins import PermissionRequiredMixin
from guardian.admin import *;
import reversion
from project.models import MiembroEquipo, Proyecto, UserStory


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
    return current_list

def version_list(request, pk):
    us = get_object_or_404(UserStory, pk=pk)
    versions = reversion.get_for_object(us)
    context = {'user_story': us, 'versions': versions}
    return render(request, 'project/version/version_list.html', context)


class VersionDetail(generic.DetailView):
    model = reversion.models.Version
    context_object_name = 'version'
    template_name = 'project/version/version_detail.html'

    def get_context_data(self, **kwargs):
        context = super(VersionDetail, self).get_context_data(**kwargs)
        context['userstory'] = self.object.field_dict
        return context

def version_detail(request, pk):
    us = get_object_or_404(reversion.models.Version, pk=pk)
    return render(request, 'project/version/version_detail.html', {'userstory': us.field_dict})