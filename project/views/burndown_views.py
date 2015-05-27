from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import generic
from guardian.mixins import PermissionRequiredMixin, LoginRequiredMixin
from guardian.admin import *;
from project.models import MiembroEquipo, Proyecto, UserStory, Adjunto, Nota, Sprint
from random import randint
from project.views import GlobalPermissionRequiredMixin


class SprintBurndown(LoginRequiredMixin, GlobalPermissionRequiredMixin, generic.DetailView):
    """
    Vista del burndown chart
    """
    model = Sprint
    template_name = 'project/sprint/sprint_burndown.html'
    permission_required = 'project.view_project'

    def get_permission_object(self):
        """
        Obtener el permiso de un objeto
        :param: self
        :return: retorna el objeto proyecto donde se comprueba el permiso
        """
        return self.get_object().proyecto

    def get_context_data(self, **kwargs):
        """
        Agregar datos al contexto
        :param:**kwargs : argumentos clave
        :return: retorna el contexto
        """
        context = super(SprintBurndown, self).get_context_data(**kwargs)
        burndown_context = get_sprint_burndown(self.object)
        context.update(burndown_context)
        return context


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


# Solo para prueba
def generarNotas(request, sprint_pk):
    # project = get_object_or_404(Proyecto, pk=project_pk)
    sprint = get_object_or_404(Sprint, pk=sprint_pk)
    project = sprint.proyecto
    us = sprint.userstory_set.first()
    total = sprint.userstory_set.aggregate(sum=Sum('tiempo_estimado'))['sum']
    dias = project.duracion_sprint
    ini = sprint.inicio
    sprint.nota_set.all().delete()
    m = total / dias
    for dt in range(0, dias + 1):
        nota = Nota(user_story=us, desarrollador=us.desarrollador, sprint=sprint)
        d = ini + timedelta(dt)
        nota.fecha = d
        nota.horas_registradas = randint(0, m + 2)
        nota.estado = 4 if randint(0, 100) > 90 else 2
        nota.save(force_insert=True)
        while (randint(0, 100) > 60):
            nota = Nota(user_story=us, desarrollador=us.desarrollador, sprint=sprint)
            nota.fecha = d
            nota.horas_registradas = randint(0, m + 3)
            nota.estado = 4 if randint(0, 100) > 90 else 2
            nota.save(force_insert=True)
    return redirect(reverse('project:sprint_burndown', kwargs={'pk': sprint.id}))


def get_sprint_burndown(sprint):
    project = sprint.proyecto
    h_restante = h_total = sprint.userstory_set.aggregate(sum=Sum('tiempo_estimado'))['sum']  # Horas estimadas de US
    lh_real = [h_total]  # Lista de horas registradas
    lh_ideal = [h_total]  # Lista de horas reales
    m = float(h_total) / project.duracion_sprint  # Velocidad ideal
    us_restante = us_total = sprint.userstory_set.count()  # User Stories del sprint
    lus_restante = [us_total]  # Lista de user stories que faltan
    lus_completado = [0]  # Lista de user stories que se terminaron
    # TODO: si todavia no termino el sprint, se muestra hasta hoy o hasta el fin de sprint?
    today = timezone.now()
    fin = today if today < sprint.fin else sprint.fin
    for dia in daterange(sprint.inicio, sprint.fin):
        notas = sprint.nota_set.filter(fecha__year=dia.year, fecha__month=dia.month, fecha__day=dia.day)
        completados = notas.filter(estado=4).count()  # User Stories terminados en el dia
        hwork = notas.aggregate(sum=Sum('horas_registradas'))['sum']  # Total de horas registradas en el dia
        hwork = hwork if hwork else 0  # Por si aggregate devuelve None
        # TODO: controlar si se registran mas horas de lo estimado
        h_restante -= hwork if h_restante >= hwork else 0  # Si se terminan las horas antes del fin
        h_total -= m
        us_restante -= completados
        lh_real.append(h_restante)
        lh_ideal.append(round(h_total, 1))
        lus_restante.append(us_restante if us_restante > 0 else 0)
        lus_completado.append(completados)

    return {'ideal': lh_ideal, 'real': lh_real, 'us_faltante': lus_restante,
            'us_terminado': lus_completado}
