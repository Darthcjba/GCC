# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MiembroEquipo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('proyecto', models.ForeignKey(to='project.Proyecto')),
                ('rol', models.ManyToManyField(to='auth.Group')),
                ('usuario', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': (),
                'verbose_name_plural': 'miembros equipo',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='miembroproyecto',
            name='proyecto',
        ),
        migrations.RemoveField(
            model_name='miembroproyecto',
            name='rol',
        ),
        migrations.RemoveField(
            model_name='miembroproyecto',
            name='usuario',
        ),
        migrations.DeleteModel(
            name='MiembroProyecto',
        ),
        migrations.AlterModelOptions(
            name='flujo',
            options={'default_permissions': (), 'verbose_name_plural': 'flujos', 'permissions': (('add_flow_template', 'agregar plantilla de flujo'), ('change_flow_template', 'editar plantilla de flujo'), ('delete_flow_template', 'eliminar plantilla de flujo'))},
        ),
        migrations.AlterModelOptions(
            name='proyecto',
            options={'permissions': (('list_all_projects', 'listar los proyectos disponibles'), ('create_miembroequipo', 'agregar miembro del equipo'), ('edit_miembroequipo', 'editar miembro del equipo'), ('remove_miembroequipo', 'eliminar miembro del equipo'), ('create_sprint', 'agregar sprint'), ('edit_sprint', 'editar sprint'), ('remove_sprint', 'eliminar sprint'), ('create_flujo', 'agregar flujo'), ('edit_flujo', 'editar flujo'), ('remove_flujo', 'eliminar flujo'), ('create_actividad', 'agregar actividad'), ('edit_actividad', 'editar actividad'), ('remove_actividad', 'eliminar actividad'), ('create_userstory', 'agregar userstory'), ('edit_userstory', 'editar userstory'), ('remove_userstory', 'eliminar userstory'))},
        ),
        migrations.AlterModelOptions(
            name='sprint',
            options={'default_permissions': ()},
        ),
        migrations.AlterModelOptions(
            name='userstory',
            options={'default_permissions': (), 'verbose_name_plural': 'user stories'},
        ),
    ]
