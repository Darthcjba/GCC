from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from project.models import Proyecto, MiembroEquipo, Flujo, Actividad, UserStory, Nota
from project.models import Proyecto, MiembroEquipo, Flujo, Actividad, UserStory, Nota, Sprint

class MiembroEquipoInLine(admin.TabularInline):
    model = MiembroEquipo
    extra = 0

class ProyectoAdmin(GuardedModelAdmin):
    inlines = [MiembroEquipoInLine]

admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(MiembroEquipo)
admin.site.register(Flujo)
admin.site.register(Actividad)
admin.site.register(UserStory)
admin.site.register(Nota)
admin.site.register(Sprint)