# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from guardian.mixins import PermissionRequiredMixin, LoginRequiredMixin
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

class VersionList(generic.ListView):
    context_object_name = 'versions'
    template_name = 'project/version/version_list.html'
    us = None

    def get_queryset(self):
        us_pk = self.kwargs['pk']
        self.us = get_object_or_404(UserStory, pk=us_pk)
        return reversion.get_for_object_reference(UserStory, us_pk)

    def get_context_data(self, **kwargs):
        context = super(VersionList, self).get_context_data(**kwargs)
        context['userstory'] = self.us
        return context

class VersionDetail(generic.DetailView):
    model = reversion.models.Version
    context_object_name = 'version'
    template_name = 'project/version/version_detail.html'

    def get_context_data(self, **kwargs):
        context = super(VersionDetail, self).get_context_data(**kwargs)
        context['userstory'] = self.object.field_dict
        return context

class UpdateVersion(LoginRequiredMixin, generic.UpdateView):
    """
    View que actualiza un user story del sistema
    """
    model = UserStory
    form_class = modelform_factory(UserStory,
                                   fields=('nombre', 'descripcion', 'prioridad', 'valor_negocio', 'valor_tecnico',
                                           'tiempo_estimado'))
    template_name = 'project/version/version_form.html'
    version = None

    def get_initial(self):
        version_pk = self.kwargs['version_pk']
        self.version = get_object_or_404(reversion.models.Version, pk=version_pk)
        return self.version.field_dict

    def get_success_url(self):
        """
        :return:la url de redireccion a la vista de los detalles del user story agregado.
        """
        return reverse('project:userstory_detail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        """
        Comprobar validez del formulario. Crea una instancia de user story
        :param form: formulario recibido
        :return: URL de redireccion
        """
        self.object = form.save()
        #self.version.revert()

        return HttpResponseRedirect(self.get_success_url())
