# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.forms import formset_factory
from django.forms.extras import SelectDateWidget
from django.forms.models import modelform_factory, modelformset_factory, inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from guardian.mixins import LoginRequiredMixin
from project.forms import AddToSprintForm
from project.models import Sprint, Proyecto, Actividad, Flujo, UserStory
from project.views import CreateViewPermissionRequiredMixin
from django.views import generic
from django.core.urlresolvers import reverse
from django.utils import timezone
import datetime

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
                                   widgets={'inicio': SelectDateWidget},
                                   fields={'nombre', 'inicio'})
    formset = formset_factory(AddToSprintForm, extra=1)

    proyecto = None

    def get_permission_object(self):
        return get_object_or_404(Proyecto, id=self.kwargs['project_pk'])

    def get_success_url(self):
        return reverse('project:sprint_detail', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context=super(AddSprintView,self).get_context_data(**kwargs)
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['project_pk'])
        context['current_action'] = "Agregar"
        if self.request.method == 'GET':
            formset=self.formset()
            for userformset in formset.forms:
                userformset.fields['desarrollador'].queryset = User.objects.filter(miembroequipo__proyecto=self.proyecto)
                userformset.fields['flujo'].queryset = Flujo.objects.filter(proyecto=self.proyecto)
                userformset.fields['userStory'].queryset = UserStory.objects.filter(proyecto=self.proyecto)
            context['formset']= formset
        return context


    def form_valid(self, form):
        self.proyecto = get_object_or_404(Proyecto, id=self.kwargs['project_pk'])
        self.object= form.save(commit=False)
        self.object.proyecto= self.proyecto
        self.object.fin= self.object.inicio + datetime.timedelta(days=self.proyecto.duracion_sprint)
        self.object.save()
        formsetb= self.formset(self.request.POST)
        if formsetb.is_valid():
            for subform in formsetb :
                new_flujo = subform.cleaned_data['flujo']
                self.flujo = new_flujo
                new_userStory = subform.cleaned_data['userStory']
                print(new_userStory)
                new_desarrollador = subform.cleaned_data['desarrollador']
                new_userStory.desarrollador= new_desarrollador
                new_userStory.sprint= self.object
                 #new_userStory.actividad= self.flujo.actividad_set.get(id=1)
                new_userStory.save()
            return HttpResponseRedirect(self.get_success_url())
        return render(self.request, self.get_template_names(), {'form': form, 'formset': formsetb},
                      context_instance=RequestContext(self.request))