# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name_plural': 'actividades',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Adjunto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=20)),
                ('descripcion', models.TextField()),
                ('filename', models.CharField(max_length=100, null=True, editable=False)),
                ('binario', models.BinaryField(null=True, blank=True)),
                ('content_type', models.CharField(max_length=50, null=True, editable=False)),
                ('creacion', models.DateTimeField(auto_now_add=True)),
                ('tipo', models.CharField(default=b'misc', max_length=10, choices=[(b'img', b'Imagen'), (b'text', b'Texto'), (b'misc', b'Otro'), (b'src', b'Codigo')])),
                ('lenguaje', models.CharField(max_length=10, null=True, choices=[(b'clike', b'C'), (b'python', b'Python'), (b'ruby', b'Ruby'), (b'css', b'CSS'), (b'php', b'PHP'), (b'scala', b'Scala'), (b'sql', b'SQL'), (b'bash', b'Bash'), (b'javascript', b'JavaScript')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Flujo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=20)),
            ],
            options={
                'default_permissions': (),
                'verbose_name_plural': 'flujos',
                'permissions': (('add_flow_template', 'agregar plantilla de flujo'), ('change_flow_template', 'editar plantilla de flujo'), ('delete_flow_template', 'eliminar plantilla de flujo')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MiembroEquipo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name_plural': 'miembros equipo',
                'default_permissions': (),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Nota',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mensaje', models.TextField(help_text=b'Mensaje de descripcion de los avances')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('horas_registradas', models.IntegerField(default=0)),
                ('estado_actividad', models.IntegerField(null=True, choices=[(0, b'ToDo'), (1, b'Doing'), (2, b'Done')])),
                ('actividad', models.ForeignKey(to='project.Actividad', null=True)),
                ('desarrollador', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre_corto', models.CharField(max_length=20)),
                ('nombre_largo', models.CharField(max_length=40)),
                ('estado', models.CharField(default=b'IN', max_length=2, choices=[(b'EP', b'En Produccion'), (b'CO', b'Completado'), (b'AP', b'Aprobado'), (b'CA', b'Cancelado'), (b'IN', b'Inactivo')])),
                ('inicio', models.DateTimeField()),
                ('fin', models.DateTimeField()),
                ('creacion', models.DateTimeField(auto_now_add=True)),
                ('duracion_sprint', models.PositiveIntegerField(default=30)),
                ('descripcion', models.TextField()),
                ('equipo', models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='project.MiembroEquipo')),
            ],
            options={
                'permissions': (('list_all_projects', 'listar los proyectos disponibles'), ('view_project', 'ver el proyecto'), ('create_sprint', 'agregar sprint'), ('edit_sprint', 'editar sprint'), ('remove_sprint', 'eliminar sprint'), ('create_flujo', 'agregar flujo'), ('edit_flujo', 'editar flujo'), ('remove_flujo', 'eliminar flujo'), ('create_userstory', 'agregar userstory'), ('edit_userstory', 'editar userstory'), ('remove_userstory', 'eliminar userstory'), ('prioritize_userstory', 'asignar prioridad a userstories'), ('registraractividad_userstory', 'registrar avances en userstories'), ('aprobar_userstory', 'aprobar userstories completados')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=20)),
                ('inicio', models.DateTimeField()),
                ('fin', models.DateTimeField()),
                ('proyecto', models.ForeignKey(to='project.Proyecto', blank=True)),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'sprint',
                'verbose_name_plural': 'sprints',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserStory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nombre', models.CharField(max_length=60)),
                ('descripcion', models.TextField()),
                ('prioridad', models.IntegerField(default=0, choices=[(0, b'Baja'), (1, b'Media'), (2, b'Alta')])),
                ('valor_negocio', models.IntegerField()),
                ('valor_tecnico', models.IntegerField()),
                ('tiempo_estimado', models.PositiveIntegerField()),
                ('tiempo_registrado', models.PositiveIntegerField(default=0)),
                ('ultimo_cambio', models.DateTimeField(auto_now=True)),
                ('estado', models.IntegerField(default=0, choices=[(0, b'Inactivo'), (1, b'En curso'), (2, b'Pendiente Aprobacion'), (3, b'Aprobado')])),
                ('estado_actividad', models.IntegerField(default=0, choices=[(0, b'ToDo'), (1, b'Doing'), (2, b'Done')])),
                ('actividad', models.ForeignKey(blank=True, to='project.Actividad', null=True)),
                ('desarrollador', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('proyecto', models.ForeignKey(to='project.Proyecto')),
                ('sprint', models.ForeignKey(blank=True, to='project.Sprint', null=True)),
            ],
            options={
                'default_permissions': (),
                'verbose_name_plural': 'user stories',
                'permissions': (('edit_my_userstory', 'editar mis userstories'), ('registraractividad_my_userstory', 'registrar avances en mis userstories')),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='nota',
            name='sprint',
            field=models.ForeignKey(to='project.Sprint', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nota',
            name='user_story',
            field=models.ForeignKey(to='project.UserStory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='miembroequipo',
            name='proyecto',
            field=models.ForeignKey(to='project.Proyecto'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='miembroequipo',
            name='roles',
            field=models.ManyToManyField(to='auth.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='miembroequipo',
            name='usuario',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='miembroequipo',
            unique_together=set([('usuario', 'proyecto')]),
        ),
        migrations.AddField(
            model_name='flujo',
            name='proyecto',
            field=models.ForeignKey(blank=True, to='project.Proyecto', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='adjunto',
            name='user_story',
            field=models.ForeignKey(to='project.UserStory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actividad',
            name='flujo',
            field=models.ForeignKey(to='project.Flujo'),
            preserve_default=True,
        ),
        migrations.AlterOrderWithRespectTo(
            name='actividad',
            order_with_respect_to='flujo',
        ),
    ]
