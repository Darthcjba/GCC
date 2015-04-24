# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views import generic
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import get_perms
import reversion
from project.models import UserStory, Proyecto, MiembroEquipo, Sprint
from project.views import CreateViewPermissionRequiredMixin, GlobalPermissionRequiredMixin


class UserStoriesList(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.ListView):
    '''
    Lista de User Stories del proyecto
    '''
    model = UserStory
    template_name = 'project/userstory/userstory_list.html'
    permission_required = 'project.view_project'
    context_object_name = 'userstories'
    project = None
    sprint = None
    sprint_backlog=False

    def get_permission_object(self):
        if not self.sprint_backlog:
            if not self.project:
                self.project = get_object_or_404(Proyecto, pk=self.kwargs['project_pk'])
        else:
            if not self.project:
                self.sprint = get_object_or_404(Sprint, pk=self.kwargs['sprint_pk'])
                self.project = self.sprint.proyecto
        return self.project

    def get_context_data(self, **kwargs):
        context = super(UserStoriesList, self).get_context_data(**kwargs)
        context['proyecto_perms'] = get_perms(self.request.user, self.project)
        return context

    def get_queryset(self):
        manager = UserStory.objects
        if not self.sprint_backlog:
            if not self.project:
                self.project = get_object_or_404(Proyecto, pk=self.kwargs['project_pk'])
            return manager.filter(proyecto=self.project)
        else:
            if not self.sprint:
                self.sprint = get_object_or_404(Sprint, pk=self.kwargs['sprint_pk'])
                self.project = self.sprint.proyecto
            return manager.filter(sprint=self.sprint)

class UserStoryDetail(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.DetailView):
    """
    Vista de Detalles de un user story
    """
    model = UserStory
    permission_required = 'project.view_project'
    template_name = 'project/userstory/userstory_detail.html'
    context_object_name = 'userstory'

    def get_permission_object(self):
        '''
        Retorna el objeto al cual corresponde el permiso
        '''
        return self.get_object().proyecto

class AddUserStory(LoginRequiredMixin, CreateViewPermissionRequiredMixin, generic.CreateView):
    """
    View que agrega un user story al sistema
    """
    model = UserStory
    form_class = modelform_factory(UserStory,
                                   fields=('nombre', 'descripcion', 'prioridad', 'valor_negocio', 'valor_tecnico',
                                           'tiempo_estimado'))
    template_name = 'project/userstory/userstory_form.html'
    permission_required = 'project.create_userstory'

    def get_permission_object(self):
        '''
        Objeto por el cual comprobar el permiso
        '''
        return get_object_or_404(Proyecto, id=self.kwargs['project_pk'])

    def get_success_url(self):
        """
        :return:la url de redireccion a la vista de los detalles del user story agregado.
        """
        return reverse('project:userstory_detail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        """
        Comprobar validez del formulario.
        :param form: formulario recibido
        :return: URL de redireccion
        """
        self.object = form.save(commit=False)
        self.object.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['project_pk'])
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

class UpdateUserStory(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.UpdateView):
    """
    View que actualiza un user story del sistema
    """
    model = UserStory
    form_class = modelform_factory(UserStory,
                                   fields=('nombre', 'descripcion', 'prioridad', 'valor_negocio', 'valor_tecnico',
                                           'tiempo_estimado'))
    template_name = 'project/userstory/userstory_form.html'
    permission_required = 'project.edit_userstory'


    def get_permission_object(self):
        return self.get_object().proyecto

    def get_context_data(self, **kwargs):
        """
        Agregar datos al contexto
        :param kwargs: argumentos clave
        :return: contexto
        """
        context = super(UpdateUserStory, self).get_context_data(**kwargs)
        context['current_action'] = "Actualizar"
        return context

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

        return HttpResponseRedirect(self.get_success_url())


class DeleteUserStory(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.DeleteView):
    """
    Vista de Eliminacion de User Stories
    """
    model = UserStory
    template_name = 'project/userstory/userstory_delete.html'
    permission_required = 'project.delete_userstory'
    context_object_name = 'userstory'

    def get_permission_object(self):
        return self.get_object().proyecto

    def get_success_url(self):
        return reverse_lazy('project:product_backlog', kwargs={'project_pk': self.get_object().proyecto.id})

class VersionList(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.ListView):
    """
    Vista que devuelve una lista de versiones del User Story deseado.
    """
    context_object_name = 'versions'
    template_name = 'project/version/version_list.html'
    us = None
    permission_required = 'project.edit_userstory'

    def get_permission_object(self):
        us_pk = self.kwargs['pk']
        self.us = get_object_or_404(UserStory, pk=us_pk)
        return self.us.proyecto

    def get_queryset(self):
        """
        Obtiene el user story y sus versiones
        """
        return reversion.get_for_object(self.us)

    def get_context_data(self, **kwargs):
        """
        Agrega el user story al contexto.
        """
        context = super(VersionList, self).get_context_data(**kwargs)
        context['userstory'] = self.us
        return context

class UpdateVersion(UpdateUserStory):
    '''
    Vista que permite revertir un User Story a una version anterior.
    '''
    version = None

    def get_initial(self):
        """
        Obtiene la version deseada del User Story.
        :return: diccionarnio con los datos de la version anterior.
        """
        version_pk = self.kwargs['version_pk']
        self.version = get_object_or_404(reversion.models.Version, pk=version_pk)
        initial = self.version.field_dict
        return initial