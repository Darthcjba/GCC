from django.contrib import admin
from project.models import Proyecto, MiembroEquipo, Flujo, Actividad, UserStory, Nota, Sprint

admin.site.register(Proyecto)
admin.site.register(MiembroEquipo)
admin.site.register(Flujo)
admin.site.register(Actividad)
admin.site.register(UserStory)
admin.site.register(Nota)
admin.site.register(Sprint)