# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, post_save
from django.shortcuts import get_object_or_404
from guardian.shortcuts import assign_perm, remove_perm, get_perms_for_model, get_perms
from django.core.urlresolvers import reverse_lazy
import reversion


class Proyecto(models.Model):
    """
    Modelo de Proyecto del sistema.

    """
    estado_choices = (
        ('EP', 'En Produccion'), ('CO', 'Completado'), ('AP', 'Aprobado'), ('CA', 'Cancelado'), ('IN', 'Inactivo'))
    nombre_corto = models.CharField(max_length=20)
    nombre_largo = models.CharField(max_length=40)
    estado = models.CharField(choices=estado_choices, max_length=2, default='IN')
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    creacion = models.DateTimeField(auto_now_add=True)
    duracion_sprint = models.PositiveIntegerField(default=30)
    descripcion = models.TextField()
    equipo = models.ManyToManyField(User, through='MiembroEquipo')

    class Meta:
        # Los permisos estaran asociados a los proyectos, por lo que todos los permisos de ABM de las entidades
        #dependientes del proyecto, deben crearse como permisos de proyecto
        #en vez de 'add', 'change' y 'delete', los permisos personalizados seran 'create', 'edit' y 'remove' para
        #evitar confusiones con los por defecto.

        permissions = (
            ('list_all_projects', 'listar los proyectos disponibles'),
            ('view_project', 'ver el proyecto'),

            ('create_sprint', 'agregar sprint'),
            ('edit_sprint', 'editar sprint'),
            ('remove_sprint', 'eliminar sprint'),

            ('create_flujo', 'agregar flujo'),
            ('edit_flujo', 'editar flujo'),
            ('remove_flujo', 'eliminar flujo'),

            ('create_userstory', 'agregar userstory'),
            ('edit_userstory', 'editar userstory'),
            ('remove_userstory', 'eliminar userstory'),
            ('prioritize_userstory', 'asignar prioridad a userstories'),
            ('registraractividad_userstory', 'registrar avances en userstories')

            #TODO: Hace falta definir permisos para Notas y Adjuntos?
        )

    def __unicode__(self):
        return self.nombre_corto

    def get_absolute_url(self):
        return reverse_lazy('project:project_detail', args=[self.pk])

    def clean(self):
        try:
            if self.inicio > self.fin:
                raise ValidationError({'inicio': 'Fecha de inicio no puede ser mayor '
                                                 'que la fecha de terminacion.'})
        except TypeError:
            pass  # si una de las fechas es null, clean_field() se encarga de lanzar error


class MiembroEquipo(models.Model):
    """
    Miembros del equipo de un proyecto con un rol específico
    """
    usuario = models.ForeignKey(User)
    proyecto = models.ForeignKey(Proyecto)
    roles = models.ManyToManyField(Group)
    '''
    def __unicode__(self):
        return "{} - {}:{}".format(self.proyecto, self.usuario, self.roles.all())
    '''

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(MiembroEquipo, self).save(force_insert, force_update, using, update_fields)
        # Agregamos el permiso view_proyect al usuario
        assign_perm('view_project', self.usuario, self.proyecto)


    # nota: si se quiere hacer un bulk delete a través de un queryset no hacerlo directamente
    #llamar al delete de cada objeto para remover los permisos
    def delete(self, using=None):
        for role in self.roles.all():
            for perm in role.permissions.all():
                remove_perm(perm.codename, self.usuario, self.proyecto)
        super(MiembroEquipo, self).delete(using)

    class Meta:
        default_permissions = ()
        verbose_name_plural = 'miembros equipo'
        unique_together = ('usuario', 'proyecto')


class Sprint(models.Model):
    """
    Manejo de los sprints del proyecto
    """
    nombre = models.CharField(max_length=20)
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    proyecto = models.ForeignKey(Proyecto, null=False)

    class Meta:
        default_permissions = ()
        verbose_name = 'sprint'
        verbose_name_plural = 'sprints'

    def __unicode__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse_lazy('project:sprint_detail', args=[self.pk])


class Flujo(models.Model):
    """
    Administración de los flujos que forman parte de un proyecto.
    Las plantillas de flujo se manejan como Flujos sin proyecto asignado.
    """
    nombre = models.CharField(max_length=20)
    proyecto = models.ForeignKey(Proyecto, null=True, blank=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = 'flujos'
        default_permissions = ()
        permissions = (
            ('add_flow_template', 'agregar plantilla de flujo'),
            ('change_flow_template', 'editar plantilla de flujo'),
            ('delete_flow_template', 'eliminar plantilla de flujo'),
        )

    def get_absolute_url(self):
        return reverse_lazy('project:flujo_detail', args=[self.pk])


class Actividad(models.Model):
    """
    Las actividades representan las distintas etapas de las que se componen un flujo
    """
    name = models.CharField(max_length=20)
    flujo = models.ForeignKey(Flujo)

    def __unicode__(self):
        return self.name

    class Meta:
        order_with_respect_to = 'flujo'
        verbose_name_plural = 'actividades'


class UserStory(models.Model):
    """
    Manejo de los User Stories. Los User Stories representan a cada
    funcionalidad desde la perspectiva del cliente que debe realizar el sistema.
    """
    estado_actividad_choices = ((0, 'ToDo'), (1, 'Doing'), (2, 'Done'), )
    estado_choices = ((0, 'Inactivo'), (1, 'En curso'), (2, 'Pendiente Aprobacion'), (3, 'Aprobado'), )
    priority_choices = ((0, 'Baja'), (1, 'Media'), (2, 'Alta'))
    nombre = models.CharField(max_length=60)
    descripcion = models.TextField()
    prioridad = models.IntegerField(choices=priority_choices, default=0)
    valor_negocio = models.IntegerField()
    valor_tecnico = models.IntegerField()
    tiempo_estimado = models.PositiveIntegerField()
    tiempo_registrado = models.PositiveIntegerField(default=0)
    ultimo_cambio = models.DateTimeField(auto_now=True)
    estado = models.IntegerField(choices=estado_choices, default=0)
    estado_actividad = models.IntegerField(choices=estado_actividad_choices, default=0)
    proyecto = models.ForeignKey(Proyecto)
    desarrollador = models.ForeignKey(User, null=True, blank=True)
    sprint = models.ForeignKey(Sprint, null=True, blank=True)
    actividad = models.ForeignKey(Actividad, null=True, blank=True)

    def __unicode__(self):
        return self.nombre

    def get_absolute_url(self):
        return reverse_lazy('project:userstory_detail', args=[self.pk])

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        old_developer = None

        if self.pk is not None:
            old_instance = get_object_or_404(UserStory, pk=self.pk)
            old_developer = old_instance.desarrollador
        super(UserStory, self).save(force_insert, force_update, using, update_fields)
        #borramos los permisos del antiguo desarrollador
        if old_developer:
            for perm in get_perms(old_developer, self):
                print(perm)
                remove_perm(perm, old_developer, self)
        #copiamos al user story recién creado los permisos de user story
        if self.proyecto and self.desarrollador:
            membership = get_object_or_404(MiembroEquipo, usuario=self.desarrollador, proyecto=self.proyecto)
            permisos_us = get_perms_for_model(UserStory)
            for rol in membership.roles.all():
                for perm in rol.permissions.all():
                    if perm in permisos_us:
                        assign_perm(perm.codename, self.desarrollador, self)

    class Meta:
        verbose_name_plural = 'user stories'
        default_permissions = ()
        permissions = (
            ('edit_my_userstory', 'editar mis userstories'),
            ('registraractividad_my_userstory', 'registrar avances en mis userstories')
        )


reversion.register(UserStory,
                   fields=['nombre', 'descripcion', 'prioridad', 'valor_negocio', 'valor_tecnico', 'tiempo_estimado'])
#importamos recién acá la señal para que no haya la dependencia circular entre la señal y UserStory
from project.signals import add_permissions_team_member
m2m_changed.connect(add_permissions_team_member, sender=MiembroEquipo.roles.through,
                    dispatch_uid='add_permissions_signal')

class Nota(models.Model):
    """
    Manejo de notas adjuntas relacionadas a un User Story, estás entradas representan
    constancias de los cambios, como cantidad de horas trabajadas, en un user story.
    """
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    desarrollador = models.ForeignKey(User, null=True)
    sprint = models.ForeignKey(Sprint, null=True)
    actividad = models.ForeignKey(Actividad, null=True)
    estado_actividad = models.IntegerField(choices=UserStory.estado_actividad_choices, null=True)
    user_story = models.ForeignKey(UserStory)


class Adjunto(models.Model):
    """
    Modelo para la administración de archivos adjuntos a un User Story.
    """
    nombre = models.CharField(max_length=20)
    descripcion = models.TextField()
    # path = models.FilePathField()
    creacion = models.DateTimeField(auto_now_add=True)
    user_story = models.ForeignKey(UserStory)