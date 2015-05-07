# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import generic
from guardian.mixins import PermissionRequiredMixin, LoginRequiredMixin
from guardian.admin import *;
from project.forms import FileUploadForm
import reversion
from project.models import MiembroEquipo, Proyecto, UserStory, Adjunto


class GlobalPermissionRequiredMixin(PermissionRequiredMixin):
    '''
    Mixin que permite requerir un permiso
    '''
    accept_global_perms = True
    return_403 = True
    raise_exception = True

class CreateViewPermissionRequiredMixin(GlobalPermissionRequiredMixin):
    '''
    Mixin que permite requerir un permiso
    '''
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


#TODO requerir permisos
#TODO subir archivo dentro de una nota?

class UploadFileView(generic.FormView):
    template_name = 'project/adjunto/upload.html'
    form_class = FileUploadForm
    file = None

    def form_valid(self, form):
        self.file = form.save(commit=False)
        user_story = get_object_or_404(UserStory, pk=self.kwargs['pk'])
        self.file.user_story = user_story
        self.file.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('project:file_detail', kwargs={'pk': self.file.id})


class FileDetail(generic.DetailView):
    model = Adjunto
    template_name = 'project/adjunto/file_view.html'
    context_object_name = 'adjunto'


class FileList(generic.ListView):
    model = Adjunto
    template_name = 'project/adjunto/file_list.html'
    context_object_name = 'adjuntos'
    user_story = None

    def get_queryset(self):
        self.user_story = get_object_or_404(UserStory, pk=self.kwargs['pk'])
        return self.user_story.adjunto_set.all()

    def get_context_data(self, **kwargs):
        context = super(FileList, self).get_context_data(**kwargs)
        context['user_story'] = self.user_story
        return context

def prism(request):
    return render(request, 'project/adjunto/prism.html', {})