# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0007_auto_20150528_0142'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proyecto',
            options={'permissions': (('list_all_projects', 'listar los proyectos disponibles'), ('view_project', 'ver el proyecto'), ('aprobar_proyecto', 'aprobar el proyecto'), ('create_sprint', 'agregar sprint'), ('edit_sprint', 'editar sprint'), ('remove_sprint', 'eliminar sprint'), ('create_flujo', 'agregar flujo'), ('edit_flujo', 'editar flujo'), ('remove_flujo', 'eliminar flujo'), ('create_userstory', 'agregar userstory'), ('edit_userstory', 'editar userstory'), ('remove_userstory', 'eliminar userstory'), ('prioritize_userstory', 'asignar prioridad a userstories'), ('registraractividad_userstory', 'registrar avances en userstories'), ('aprobar_userstory', 'aprobar userstories completados'), ('cancelar_userstory', 'cancela userstories completados'))},
        ),
        migrations.AlterField(
            model_name='nota',
            name='mensaje',
            field=models.TextField(help_text=b'Mensaje de descripcion de los avances', null=True, blank=True),
        ),
    ]
