from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError


def validate_dates(start, end):
    if start > end:
        raise ValidationError('La fecha de inicio no puede ser mayor que la de fin')


class Proyecto(models.Model):
    """
    Stores a single project.

    """
    estado_choices = (
        ('EP', 'En Produccion'), ('CO', 'Completado'), ('AP', 'Aprobado'), ('CA', 'Cancelado'), ('IN', 'Inactivo'))
    nombre_corto = models.CharField(max_length=20)
    nombre_largo = models.CharField(max_length=40)
    estado = models.CharField(choices=estado_choices, max_length=2, default='IN')
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    creacion = models.DateTimeField(auto_now_add=True)
    duracion_sprint = models.IntegerField(default=0)
    descripcion = models.TextField()

    class Meta:
        permissions = (
            ('list_all_projects', 'list all available projects'),
        )



    def __unicode__(self):
        return self.nombre_corto


class MiembroEquipo(models.Model):
    usuario = models.ForeignKey(User)
    proyecto = models.ForeignKey(Proyecto)
    rol = models.ForeignKey(Group)

    def __unicode__(self):
        return "{} - {}:{}".format(self.proyecto, self.usuario, self.rol)

    class Meta:
        verbose_name_plural = 'miembros equipo'


class Sprint(models.Model):
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    proyecto = models.ForeignKey(Proyecto)


class Flujo(models.Model):
    nombre = models.CharField(max_length=20)
    proyecto = models.ForeignKey(Proyecto, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'flujos'
        permissions = (
            ('add_flow_template', 'add flow template'),
            ('change_flow_template', 'change flow template'),
            ('delete_flow_template', 'delete flow template')
        )


class Actividad(models.Model):
    name = models.CharField(max_length=20)
    flujo = models.ForeignKey(Flujo)

    def __unicode__(self):
        return self.name

    class Meta:
        order_with_respect_to = 'flujo'
        verbose_name_plural = 'actividades'


class UserStory(models.Model):
    estado_choices = ((0, 'ToDo'), (1, 'Doing'), (2, 'Done'), (3, 'Pendiente Aprobacion'), (4, 'Aprobado'))
    nombre = models.CharField(max_length=20)
    descripcion = models.TextField()
    prioridad = models.IntegerField(choices=((i, i) for i in range(1, 11)), default=1)
    valor_negocio = models.IntegerField()
    valor_tecnico = models.IntegerField()
    tiempo_estimado = models.TimeField()
    tiempo_registrado = models.TimeField()
    ultimo_cambio = models.DateTimeField(auto_now=True)
    estado = models.IntegerField(choices=estado_choices, default=0)
    proyecto = models.ForeignKey(Proyecto)
    desarrollador = models.ForeignKey(User, null=True)
    sprint = models.ForeignKey(Sprint, null=True)
    actividad = models.ForeignKey(Actividad, null=True)

    class Meta:
        verbose_name_plural = 'user stories'


class Version(models.Model):
    nombre = models.CharField(max_length=20)
    descripcion = models.TextField()
    valor_negocio = models.IntegerField()
    valor_tecnico = models.IntegerField()
    tiempo_estimado = models.TimeField()
    modificacion = models.DateTimeField(auto_now_add=True)
    user_story = models.ForeignKey(UserStory)


class Nota(models.Model):
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    # usuario = models.ForeignKey(User)
    user_story = models.ForeignKey(UserStory)


class Adjunto(models.Model):
    nombre = models.CharField(max_length=20)
    descripcion = models.TextField()
    # path = models.FilePathField()
    creacion = models.DateTimeField(auto_now_add=True)
    user_story = models.ForeignKey(UserStory)