# -*- coding: utf-8 -*-
from django.forms import formset_factory
from django.forms.extras import SelectDateWidget
from django.forms.models import modelform_factory, modelformset_factory, inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from guardian.mixins import LoginRequiredMixin
from project.forms import AddToSprintForm
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
    form_class = modelform_factory(Sprint,
                                   widgets={'inicio': SelectDateWidget, 'fin': SelectDateWidget},
                                   fields={'nombre', 'inicio', 'fin'})
    formset = formset_factory(AddToSprintForm, extra=1)

    def get_permission_object(self):
        return get_object_or_404(Proyecto, id=self.kwargs['project_pk'])

    def get_success_url(self):
        return reverse('project:sprint_detail', kwargs={'pk': self.sprint.id})

    def get_context_data(self, **kwargs):
        context=super(AddSprintView,self).get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['formset']= self.formset()
        return context


    def form_valid(self, form):

        proyecto = get_object_or_404(Proyecto, pk=self.kwargs['project_pk'])
        self.object= form.save(commit=False)
        self.object.proyecto= proyecto
        self.object.save()
        formset= self.formset(self.request.POST, instance=self.object)
        if formset.is_valid():
            new_flujo = formset.cleaned_data['flujo']
            new_userStory = form.cleaned_data['userStory']
            new_desarrollador = form.cleaned_data['desarrollador']
            new_userStory.desarrollador= new_desarrollador
            new_userStory.proyecto= proyecto
            new_userStory.sprint= self.object
            new_userStory.actividad= new_flujo.actividad_set.all().get(id=1)
            new_userStory.save()
            self.userstory = new_userStory
            return HttpResponseRedirect(self.get_success_url())
        return render(self.request, self.get_template_names(), {'form': form, 'formset': formset},
                      context_instance=RequestContext(self.request))