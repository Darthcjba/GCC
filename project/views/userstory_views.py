# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import generic
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import get_perms, get_perms_for_model, assign_perm
import reversion
from project.models import UserStory, Proyecto, MiembroEquipo, Sprint, Actividad
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

    def get_permission_object(self):
        if not self.project:
            self.project = get_object_or_404(Proyecto, pk=self.kwargs['project_pk'])
        return self.project

    def get_context_data(self, **kwargs):
        context = super(UserStoriesList, self).get_context_data(**kwargs)
        context['proyecto_perms'] = get_perms(self.request.user, self.project)
        return context

    def get_queryset(self):
        manager = UserStory.objects
        if not self.project:
            self.project = get_object_or_404(Proyecto, pk=self.kwargs['project_pk'])
        return manager.filter(proyecto=self.project)

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
    template_name = 'project/userstory/userstory_form.html'
    permission_required = 'project.create_userstory'

    def get_form_class(self):
        project = get_object_or_404(Proyecto, id=self.kwargs['project_pk'])
        form_fields = ['nombre', 'descripcion', 'valor_negocio', 'valor_tecnico', 'tiempo_estimado']
        if 'prioritize_userstory' in get_perms(self.request.user, project):
            form_fields.insert(2, 'prioridad')
        form_class = modelform_factory(UserStory, fields=form_fields)
        return form_class

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
        self.object.proyecto = get_object_or_404(Proyecto, id=self.kwargs['project_pk'])
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

class UpdateUserStory(LoginRequiredMixin, generic.UpdateView):
    """
    View que actualiza un user story del sistema
    """
    model = UserStory
    template_name = 'project/userstory/userstory_form.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Comprobación de permisos hecha antes de la llamada al dispatch que inicia el proceso de respuesta al request de la url
        :param request: request hecho por el cliente
        :param args: argumentos adicionales posicionales
        :param kwargs: argumentos adicionales en forma de diccionario
        :return: PermissionDenied si el usuario no cuenta con permisos
        """
        if 'edit_userstory' in get_perms(request.user, self.get_object().proyecto):
            return super(UpdateUserStory, self).dispatch(request, *args, **kwargs)
        elif 'edit_my_userstory' in get_perms(self.request.user, self.get_object()):
            return super(UpdateUserStory, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    def get_form_class(self):
        project = self.get_object().proyecto
        form_fields = ['nombre', 'descripcion', 'valor_negocio', 'valor_tecnico', 'tiempo_estimado']
        if 'prioritize_userstory' in get_perms(self.request.user, project):
            form_fields.insert(2, 'prioridad')
        form_class = modelform_factory(UserStory, fields=form_fields)
        return form_class

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

class RegistrarActividadUserStory(LoginRequiredMixin, generic.UpdateView):
    """
    View que permite registrar los cambios aplicados a un user story
    """
    model = UserStory
    template_name = 'project/userstory/userstory_registraractividad_form.html'
    error_template = 'project/userstory/userstory_error.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Comprobación de permisos hecha antes de la llamada al dispatch que inicia el proceso de respuesta al request de la url
        :param request: request hecho por el cliente
        :param args: argumentos adicionales posicionales
        :param kwargs: argumentos adicionales en forma de diccionario
        :return: PermissionDenied si el usuario no cuenta con permisos
        """
        if 'registraractividad_userstory' in get_perms(request.user, self.get_object().proyecto)\
                or ('registraractividad_my_userstory' in get_perms(request.user, self.get_object())):
            if self.get_object().sprint and self.get_object().sprint.fin >= timezone.now():
                if self.get_object().actividad:
                    current_priority = self.get_object().prioridad
                    s = self.get_object().sprint
                    a = self.get_object().actividad
                    d = self.get_object().desarrollador
                    bigger_priorities = UserStory.objects.filter(sprint=s, actividad=a, desarrollador=d, prioridad__gt=current_priority).count()
                    if bigger_priorities == 0:
                        return super(RegistrarActividadUserStory, self).dispatch(request, *args, **kwargs)
                return render(request, self.error_template, {'userstory': self.get_object(), 'error': "MENOR_PRIORIDAD"})
            return render(request, self.error_template, {'userstory': self.get_object(), 'error': "SPRINT_VENCIDO"})
        raise PermissionDenied()

    def get_form_class(self):
        """
        Retorna el tipo de formulario que se mostrará en el template. En caso de que
        el usuario cuente con el permiso de editar userstory se le permitirá cambiar la actividad
        del User Story.
        """
        actual_fields = ['tiempo_registrado', 'estado_actividad']
        if 'edit_userstory' in get_perms(self.request.user, self.get_object().proyecto) or\
            'edit_my_userstory' in get_perms(self.request.user, self.get_object()):
            actual_fields.insert(1, 'actividad')
        return modelform_factory(UserStory, fields=actual_fields)

    def get_form(self, form_class):
        '''
        Personalización del form retornado
        '''

        form = super(RegistrarActividadUserStory, self).get_form(form_class)
        if 'actividad' in form.fields:
            form.fields['actividad'].queryset = Actividad.objects.filter(flujo=self.get_object().actividad.flujo)
        return form

    def form_valid(self, form):
        self.object = form.save(commit=False)
        #movemos el User Story a la sgte actividad en caso de que haya llegado a Done
        if form.cleaned_data['estado_actividad'] == 2:
            try:
                next_actividad = self.object.actividad.get_next_in_order()
            except ObjectDoesNotExist:
                #TODO incluir en la cola a evaluar por el scrum master
                next_actividad = self.object.actividad #temporalmente que mantenga su actividad
            self.object.actividad = next_actividad
            self.object.estado_actividad = 0
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class DeleteUserStory(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.DeleteView):
    """
    Vista de Eliminacion de User Stories
    """
    model = UserStory
    template_name = 'project/userstory/userstory_delete.html'
    permission_required = 'project.remove_userstory'
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
        '''
        Obtiene el user story
        '''
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