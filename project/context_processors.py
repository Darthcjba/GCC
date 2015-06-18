from django.contrib.auth.decorators import login_required
from project.models import Proyecto, UserStory


def nav_context_processor(request):
    try:
        user = request.user
        if user.has_perm('project.list_all_projects'):
            nav_projects = Proyecto.objects.order_by('nombre_corto')[:5]
            nav_us = UserStory.objects.order_by('nombre')[:5]
        else:
            nav_projects = user.proyecto_set.order_by('nombre_corto')[:5]
            nav_us = user.userstory_set.order_by('nombre')[:5]
        return {'nav_projects': nav_projects, 'nav_us': nav_us}
    except AttributeError:
        return {'nav_projects': [],
                'nav_us': [],
                }