# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views import generic
from guardian.mixins import PermissionRequiredMixin, LoginRequiredMixin
from guardian.admin import *;
from project.forms import UploadFileForm, FileUploadForm
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

def handle_uploaded_file(f):
    with open('name.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponse("Good Job")
    else:
        form = UploadFileForm()
    return render_to_response('upload.html', {'form': form})


class UploadFileView(generic.FormView):
    template_name = 'project/upload.html'
    form_class = FileUploadForm
    file = None

    def form_valid(self, form):
        self.file = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('project:file_view', args=(self.file,))


class FileDetail(generic.DetailView):
    model = Adjunto
    template_name = 'project/file_view.html'
    context_object_name = 'adjunto'

class FileList(generic.ListView):
    model = Adjunto
    template_name = 'project/file_list.html'
    context_object_name = 'adjuntos'
    user_story = None

    def get_queryset(self):
        self.user_story = get_object_or_404(UserStory, pk=self.kwargs['pk_userstory'])
        return self.user_story.adjunto_set.all()

    def get_context_data(self, **kwargs):
        context = super(FileDetail, self).get_context_data(**kwargs)
        context['user_story'] = self.user_story
        return context