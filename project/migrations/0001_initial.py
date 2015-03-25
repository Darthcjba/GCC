# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
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
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('nombre', models.CharField(max_length=20)),
                ('descripcion', models.TextField()),
                ('creacion', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Flujo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('nombre', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name_plural': 'flujos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MiembroProyecto',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Nota',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('descripcion', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('nombre_corto', models.CharField(max_length=20)),
                ('nombre_largo', models.CharField(max_length=40)),
                ('estado', models.CharField(default='IN', max_length=2, choices=[('EP', 'En Produccion'), ('CO', 'Completado'), ('AP', 'Aprobado'), ('CA', 'Cancelado'), ('IN', 'Inactivo')])),
                ('inicio', models.DateTimeField()),
                ('fin', models.DateTimeField()),
                ('creacion', models.DateTimeField(auto_now_add=True)),
                ('duracion_sprint', models.IntegerField(default=0)),
                ('descripcion', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('inicio', models.DateTimeField()),
                ('fin', models.DateTimeField()),
                ('proyecto', models.ForeignKey(to='project.Proyecto')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserStory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('nombre', models.CharField(max_length=20)),
                ('descripcion', models.TextField()),
                ('prioridad', models.IntegerField(default=1, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)])),
                ('valor_negocio', models.IntegerField()),
                ('valor_tecnico', models.IntegerField()),
                ('tiempo_estimado', models.TimeField()),
                ('tiempo_registrado', models.TimeField()),
                ('ultimo_cambio', models.DateTimeField(auto_now=True)),
                ('estado', models.IntegerField(default=0, choices=[(0, 'ToDo'), (1, 'Doing'), (2, 'Done'), (3, 'Pendiente Aprobacion'), (4, 'Aprobado')])),
                ('actividad', models.ForeignKey(null=True, to='project.Actividad')),
                ('desarrollador', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL)),
                ('proyecto', models.ForeignKey(to='project.Proyecto')),
                ('sprint', models.ForeignKey(null=True, to='project.Sprint')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('nombre', models.CharField(max_length=20)),
                ('descripcion', models.TextField()),
                ('valor_negocio', models.IntegerField()),
                ('valor_tecnico', models.IntegerField()),
                ('tiempo_estimado', models.TimeField()),
                ('modificacion', models.DateTimeField(auto_now_add=True)),
                ('user_story', models.ForeignKey(to='project.UserStory')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='nota',
            name='user_story',
            field=models.ForeignKey(to='project.UserStory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='miembroproyecto',
            name='proyecto',
            field=models.ForeignKey(to='project.Proyecto'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='miembroproyecto',
            name='rol',
            field=models.ForeignKey(to='auth.Group'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='miembroproyecto',
            name='usuario',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flujo',
            name='proyecto',
            field=models.ForeignKey(null=True, to='project.Proyecto'),
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
