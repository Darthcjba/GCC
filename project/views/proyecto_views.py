# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.forms import CheckboxSelectMultiple
from django.forms import inlineformset_factory
from django.forms.extras import SelectDateWidget
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views import generic
from django.views.generic import DetailView
from django.views.generic import ListView
from guardian.mixins import LoginRequiredMixin
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_perms
from project.models import Proyecto
from project.models import MiembroEquipo
from project.views import GlobalPermissionRequiredMixin
from project.views import CreateViewPermissionRequiredMixin


class ProjectList(LoginRequiredMixin, ListView):
    """
    Listado de Proyectos
    """
    model = Proyecto
    context_object_name = 'projects'
    template_name = 'project/proyecto/project_list.html'
    show_cancelled = False

    def get_queryset(self):
        """
        Obtener proyectos del Sistema.

        :return: lista de proyectos
        """
        if self.request.user.has_perm('project.list_all_projects'):
            proyectos = Proyecto.objects
        else:
            proyectos = self.request.user.proyecto_set
        return proyectos.filter(estado='CA') if self.show_cancelled else proyectos.exclude(estado='CA')

class ProjectDetail(LoginRequiredMixin, GlobalPermissionRequiredMixin, DetailView):
    """
    Vista de Detalles de Proyecto
    """
    model = Proyecto
    context_object_name = 'project'
    permission_required = 'project.view_project'
    template_name = 'project/proyecto/project_detail.html'


    def get_context_data(self, **kwargs):
        context = super(ProjectDetail, self).get_context_data(**kwargs)
        context['team'] = self.object.miembroequipo_set.all()
        context['flows'] = self.object.flujo_set.all()
        context['sprints'] = self.object.sprint_set.all()
        return context


class ProjectCreate(LoginRequiredMixin, CreateViewPermissionRequiredMixin, generic.CreateView):
    """
    Permite la creacion de Proyectos
    """
    model = Proyecto
    permission_required = 'project.add_proyecto'
    form_class = modelform_factory(Proyecto,
                                   widgets={'inicio': SelectDateWidget, 'fin': SelectDateWidget},
                                   fields=('nombre_corto', 'nombre_largo', 'inicio', 'fin', 'duracion_sprint',
                                           'descripcion'),)
    template_name = 'project/proyecto/project_form.html'
    TeamMemberInlineFormSet = inlineformset_factory(Proyecto, MiembroEquipo, can_delete=True,
                                                    fields=['usuario', 'roles'],
                                                    extra=1,
                                                    widgets={'roles': CheckboxSelectMultiple})

    def get_context_data(self, **kwargs):
        context = super(ProjectCreate, self).get_context_data(**kwargs)
        context['formset'] = self.TeamMemberInlineFormSet()
        return context

    def form_valid(self, form):
        """
        Guarda los miembros de equipo especificados asociados al proyecto.

        :param form: formulario del proyecto
        """

        self.object = form.save()
        formset = self.TeamMemberInlineFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(self.get_success_url())

        return render(self.request, self.get_template_names(), {'form': form, 'formset': formset},
                      context_instance=RequestContext(self.request))


class ProjectUpdate(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.UpdateView):
    """
    Permite la Edicion de Proyectos
    """
    model = Proyecto
    permission_required = 'project.change_proyecto'
    template_name = 'project/proyecto/project_form.html'
    TeamMemberInlineFormSet = inlineformset_factory(Proyecto, MiembroEquipo, can_delete=True,
                                                    fields=['usuario', 'roles'],
                                                    extra=1,
                                                    widgets={'roles': CheckboxSelectMultiple})
    form_class = modelform_factory(Proyecto,
                                   widgets={'inicio': SelectDateWidget, 'fin': SelectDateWidget},
                                   fields=('nombre_corto', 'nombre_largo', 'inicio', 'fin', 'duracion_sprint',
                                           'descripcion'),
                                   )


    def form_valid(self, form):
        '''
        actualiza los miembros del equipo del proyecto que se hayan especifico

        :param form: formulario de edición del proyecto
        '''
        self.object = form.save()
        formset = self.TeamMemberInlineFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            # borramos todos los permisos asociados al usuario en el proyecto antes de volver a asignar los nuevos
            project = self.object
            for form in formset:
                if form.has_changed():  #solo los formularios con cambios efectuados
                    user = form.cleaned_data['usuario']
                    if('usuario' in form.changed_data and 'usuario' in form.initial): #si se cambia el usuario, borrar permisos del usuario anterior
                        original_user = get_object_or_404(User, pk=form.initial['usuario'])
                        for perm in get_perms(original_user, project):
                            remove_perm(perm, original_user, project)
                    else:
                        for perm in get_perms(user, project):
                            remove_perm(perm, user, project)

            formset.save()
            return HttpResponseRedirect(self.get_success_url())

        return render(self.request, self.get_template_names(), {'form': form, 'formset': formset},
                      context_instance=RequestContext(self.request))

    def get_context_data(self, **kwargs):
        '''
        Especifica los datos de contexto a pasar al template
        :param kwargs: Diccionario con parametros con nombres clave
        '''
        context = super(ProjectUpdate, self).get_context_data(**kwargs)
        context['formset'] = self.TeamMemberInlineFormSet(instance=self.object)
        return context


class ProjectDelete(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.DeleteView):
    """
    Vista para la cancelacion de proyectos
    """
    model = Proyecto
    template_name = 'project/proyecto/proyect_delete.html'
    success_url = reverse_lazy('project:project_list')
    permission_required = 'project.delete_proyecto'

    def delete(self, request, *args, **kwargs):
        """
        Llama al metodo delete() del objeto
        y luego redirige a la url exitosa.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        if False:
            self.object.delete()
        else:
            self.object.estado = 'CA'
            self.object.save(update_fields=['estado'])
        return HttpResponseRedirect(success_url)

