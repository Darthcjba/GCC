# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views import generic
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import get_perms
from project.models import UserStory, Proyecto, MiembroEquipo
from project.views import CreateViewPermissionRequiredMixin, GlobalPermissionRequiredMixin


class UserStoriesList(LoginRequiredMixin, generic.ListView):
    '''
    Lista de User Stories del proyecto
    '''
    model = UserStory
    template_name = 'project/userstory/userstory_list.html'
    context_object_name = 'userstories'
    project = None

    def get_context_data(self, **kwargs):
        context = super(UserStoriesList, self).get_context_data(**kwargs)
        context['proyecto_perms'] = get_perms(self.request.user, self.project)
        return context

    def get_queryset(self):
        project_pk = self.kwargs['project_pk']
        self.project = get_object_or_404(Proyecto, pk=project_pk)
        return UserStory.objects.filter(proyecto=self.project)

class UserStoryDetail(LoginRequiredMixin, generic.DetailView):
    """
    Vista de Detalles de un user story
    """
    model = UserStory
    template_name = 'project/userstory/userstory_detail.html'
    context_object_name = 'userstory'

class AddUserStory(LoginRequiredMixin, CreateViewPermissionRequiredMixin, generic.CreateView):
    """
    View que agrega un user story al sistema
    """
    model = UserStory
    form_class = modelform_factory(UserStory,
                                   fields=('nombre', 'descripcion', 'prioridad', 'valor_negocio', 'valor_tecnico',
                                           'tiempo_estimado', 'desarrollador', 'sprint'))
    template_name = 'project/userstory/userstory_form.html'
    permission_required = 'project.create_userstory'

    def get_form(self, form_class):
        form = super(AddUserStory, self).get_form(form_class)
        project = get_object_or_404(Proyecto, id=self.kwargs['project_pk'])
        form.fields['desarrollador'].queryset = User.objects.filter(miembroequipo__proyecto=project)
        return form

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
                                           'tiempo_estimado', 'desarrollador', 'sprint'))
    template_name = 'project/userstory/userstory_form.html'
    permission_required = 'project.edit_userstory'

    def get_form(self, form_class):
        form = super(UpdateUserStory, self).get_form(form_class)
        project = self.object.proyecto
        form.fields['desarrollador'].queryset = User.objects.filter(miembroequipo__proyecto=project)
        return form

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
        return reverse_lazy('project:userstory_list', kwargs={'project_pk': self.get_object().proyecto.id})