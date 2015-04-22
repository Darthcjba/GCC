from django.contrib.auth.decorators import login_required
from project.models import Proyecto

def nav_context_processor(request):
    try:
        user = request.user
        if user.has_perm('project.list_all_projects'):
            nav_projects = Proyecto.objects.all()[:5]
        else:
            nav_projects = user.proyecto_set.all()[:5]
        return {'nav_projects': nav_projects}
    except AttributeError:
        return {}