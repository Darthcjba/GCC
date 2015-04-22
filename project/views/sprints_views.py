# -*- coding: utf-8 -*-
from django.forms import formset_factory
from django.forms.extras import SelectDateWidget
from django.forms.models import modelform_factory, inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from guardian.mixins import LoginRequiredMixin
from project.forms import CreateSprintForm
from project.models import Sprint, Proyecto, Actividad
from project.views import CreateViewPermissionRequiredMixin
from django.views import generic
from django.core.urlresolvers import reverse

__author__ = 'santiortizpy'

class SprintDetail(LoginRequiredMixin, generic.DetailView):
    model = Sprint
    template_name = 'project/sprint/sprint_detail.html'
    context_object_name = 'sprint'

    def get_context_data(self, **kwargs):
        context= super(SprintDetail, self).get_context_data(**kwargs)
        context['userStory']= self.object.userstory_set.all()




class AddSprintView(LoginRequiredMixin, CreateViewPermissionRequiredMixin, generic.CreateView):
    model = Sprint
    template_name = 'project/sprint/sprint_form.html'
    permission_required = 'project.create_sprint'
    form_class = CreateSprintForm

    def get_permission_object(self):
        return get_object_or_404(Proyecto, id=self.kwargs['project_pk'])

    def get_success_url(self):
        return reverse('project:sprint_detail', kwargs={'pk': self.sprint.id})


    def form_valid(self, form):

        new_flujo = form.cleaned_data['flujo']
        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['project_pk'])
        new_userStory = form.cleaned_data['userStory']
        new_desarrollador = form.cleaned_data['desarrollador']
        new_flujo.proyecto = proyecto
        new_flujo.save()
        self.flujo = new_flujo
        sprint = Sprint
        sprint.nombre= form.cleaned_data['nombre']
        sprint.inicio= form.cleaned_data['inicio']
        sprint.fin = form.cleaned_data['fin']
        sprint.proyecto= proyecto
        sprint.save()
        new_userStory.desarrollador= new_desarrollador
        new_userStory.proyecto= proyecto
        new_userStory.sprint= sprint
        new_userStory.actividad= self.flujo.actividad_set.all().get(flujo = new_flujo, id=1)
        new_userStory.save()
        self.userstory = new_userStory
        return HttpResponseRedirect(self.get_success_url())
