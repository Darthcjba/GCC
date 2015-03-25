from django.contrib import admin
from project.models import Proyecto, MiembroEquipo, Flujo, Actividad, UserStory, Nota

admin.site.register(Proyecto)
admin.site.register(MiembroEquipo)
admin.site.register(Flujo)
admin.site.register(Actividad)
admin.site.register(UserStory)
admin.site.register(Nota)