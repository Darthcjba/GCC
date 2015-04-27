from django.contrib import admin
from guardian.admin import GuardedModelAdmin
import reversion
from project.models import Proyecto, MiembroEquipo, Flujo, Actividad, UserStory, Nota, Sprint

class MiembroEquipoInLine(admin.TabularInline):
    model = MiembroEquipo
    extra = 0

class ActividadInLine(admin.TabularInline):
    model = Actividad
    extra = 0

class ActividadAdmin(GuardedModelAdmin):
    inlines = [ActividadInLine]

class ProyectoAdmin(GuardedModelAdmin):
    inlines = [MiembroEquipoInLine]

class NotaAdmin(reversion.VersionAdmin):
    pass


admin.site.register(Proyecto, ProyectoAdmin)
admin.site.register(MiembroEquipo)
admin.site.register(Flujo, ActividadAdmin)
admin.site.register(Actividad)
admin.site.register(UserStory)
admin.site.register(Nota, NotaAdmin)
admin.site.register(Sprint)