# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.views import generic
from guardian.mixins import LoginRequiredMixin
from project.forms import PlantillaCreateForm, ActividadFormSet
from project.models import Flujo
from project.views import CreateViewPermissionRequiredMixin, GlobalPermissionRequiredMixin


class PlantillaList(LoginRequiredMixin, generic.ListView):
    """
    Vista de Listado de Plantillas en el sistema
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_list.html'
    context_object_name = 'plantillas'
    queryset = Flujo.objects.filter(proyecto_id=None)


class PlantillaDetail(LoginRequiredMixin, generic.DetailView):
    """
    Vista de Detalles de una Plantilla
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_detail.html'
    context_object_name = 'plantilla'


class AddPlantilla(LoginRequiredMixin, CreateViewPermissionRequiredMixin, generic.CreateView):
    """
    View que agrega un flujo al sistema
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_form.html'
    form_class = PlantillaCreateForm
    permission_required = 'project.add_flow_template'

    def get_context_data(self, **kwargs):
        """
        Agregar datos al contexto
        :param kwargs: argumentos clave
        :return: contexto
        """
        context = super(AddPlantilla, self).get_context_data(**kwargs)
        context['current_action'] = "Agregar"
        if (self.request.method == 'GET'):
            context['actividad_form'] = ActividadFormSet()
        return context

    def get_success_url(self):
        """
        :return:la url de redireccion a la vista de los detalles del flujo agregado.
        """
        return reverse('project:plantilla_detail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        """
        Comprobar validez del formulario. Crea una instancia de flujo para asociar con la actividad
        :param form: formulario recibido
        :param actividad_form: formulario recibido de actividad
        :return: URL de redireccion
        """
        self.object = form.save()
        actividad_form = ActividadFormSet(self.request.POST, instance=self.object)
        if actividad_form.is_valid():
            actividad_form.save()
            order = [form.instance.id for form in actividad_form.ordered_forms]
            self.object.set_actividad_order(order)

            return HttpResponseRedirect(self.get_success_url())

        return self.render(self.request, self.get_template_names(), {'form': form,
                                                                     'actividad_form': actividad_form},
                           context_instance=RequestContext(self.request))


class UpdatePlantilla(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.UpdateView):
    """
    View que agrega un flujo al sistema
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_form.html'
    form_class = PlantillaCreateForm
    permission_required = 'project.change_flow_template'

    def get_context_data(self, **kwargs):
        """
        Agregar datos al contexto
        :param kwargs: argumentos clave
        :return: contexto
        """
        context = super(UpdatePlantilla, self).get_context_data(**kwargs)
        context['current_action'] = "Actualizar"
        if (self.request.method == 'GET'):
            context['actividad_form'] = ActividadFormSet(instance=self.object)

        return context

    def get_success_url(self):
        """
        :return:la url de redireccion a la vista de los detalles del flujo agregado.
        """
        return reverse('project:plantilla_detail', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        """
        Comprobar validez del formulario. Crea una instancia de flujo para asociar con la actividad
        :param form: formulario recibido
        :param actividad_form: formulario recibido de actividad
        :return: URL de redireccion
        """
        self.object = form.save()
        actividad_form = ActividadFormSet(self.request.POST, instance=self.object)
        if actividad_form.is_valid():
            actividad_form.save()
            order = [form.instance.id for form in actividad_form.ordered_forms]
            self.object.set_actividad_order(order)

            return HttpResponseRedirect(self.get_success_url())

        return self.render(self.request, self.get_template_names(), {'form': form,
                                                                     'actividad_form': actividad_form},
                           context_instance=RequestContext(self.request))


class DeletePlantilla(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.DeleteView):
    """
    Vista de Eliminacion de Plantillas
    """
    model = Flujo
    template_name = 'project/plantilla/plantilla_delete.html'
    context_object_name = 'plantilla'
    success_url = reverse_lazy('project:plantilla_list')
    permission_required = 'project.delete_flow_template'


