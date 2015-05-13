
from django.views import generic
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from os.path import splitext
from project.forms import FileUploadForm
from project.models import UserStory, Adjunto


lang = {'.c': 'clike', '.py': 'python', '.rb': 'ruby', '.css': 'css', '.php': 'php', '.scala': 'scala', '.sql': 'sql',
        '.sh': 'bash', '.js': 'javascript', '.html': 'html'}


# TODO requerir permisos
# TODO subir archivo dentro de una nota?
class UploadFileView(generic.FormView):
    template_name = 'project/adjunto/upload.html'
    form_class = FileUploadForm
    attachment = None

    def upload_handler(self, uploaded_file):
        self.attachment.filename = uploaded_file.name

        if uploaded_file.content_type.startswith('image'):
            self.attachment.tipo = 'img'
        else:
            _, ext = splitext(uploaded_file.name)
            if ext in lang:
                self.attachment.lenguaje = lang[ext]
                self.attachment.tipo = 'src'
            elif uploaded_file.content_type == 'text/plain':
                self.attachment.tipo = 'text'

        self.attachment.content_type = uploaded_file.content_type
        self.attachment.binario = uploaded_file.read()
        self.attachment.save()

    def form_valid(self, form):
        self.attachment = form.save(commit=False)
        user_story = get_object_or_404(UserStory, pk=self.kwargs['pk'])
        self.attachment.user_story = user_story
        self.upload_handler(self.request.FILES['file'])

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('project:file_detail', kwargs={'pk': self.attachment.id})


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

#TODO controlar permisos de descarga
def download_attachment(request, pk):
    attachment = Adjunto.objects.get(pk=pk)
    response = HttpResponse(attachment.binario, content_type=attachment.content_type)
    if attachment.tipo == 'img':
        response['Content-Disposition'] = 'filename=%s' % attachment.filename
    else:
        response['Content-Disposition'] = 'attachment; filename=%s' % attachment.filename
    return response