# -*- coding: utf-8 -*-
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
from django.contrib.auth.models import Group, Permission, User
from django import forms
from guardian.shortcuts import get_perms_for_model
from project.models import Proyecto, Flujo, Sprint, Actividad, MiembroEquipo
from project.models import UserStory

def general_perms_list():
    '''

    :return: lista con los permisos que pueden asignarse a nivel general
    :rtype: list
    '''
    permlist = []
    permlist.append(Permission.objects.get(codename="list_all_projects"))
    permlist.append(Permission.objects.get(codename="add_flow_template"))
    permlist.append(Permission.objects.get(codename="change_flow_template"))
    permlist.append(Permission.objects.get(codename="delete_flow_template"))
    return permlist





class UserEditForm(UserChangeForm):
    '''
    Formulario para edición de usuarios
    '''
    password = ReadOnlyPasswordHashField(label=("Password"),
        help_text=("Solo se almacena un hash del password, no hay manera de verla. "
                   "Para modificarla seleccionar la opcion <strong>Cambiar Password</strong>"))

    general_perms_list = [(perm.codename, perm.name) for perm in general_perms_list()]
    perms_user_list = [(perm.codename, perm.name) for perm in get_perms_for_model(User)]
    perms_group_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Group)]
    general_perms_list.extend(perms_user_list)
    general_perms_list.extend(perms_group_list)
    general_perms = forms.MultipleChoiceField(general_perms_list, widget=forms.CheckboxSelectMultiple, label="General permissions", required=False)


class RolForm(forms.ModelForm):
    '''
    Formulario para el manejo de roles
    '''

    perms_proyecto_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Proyecto) if 'proyecto' in perm.codename]
    perms_teammembers_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Proyecto) if 'miembroequipo' in perm.codename]
    perms_userstories_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Proyecto) if 'userstory' in perm.codename]
    perms_flujo_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Proyecto) if 'flujo' in perm.codename and not('template' in perm.codename)]
    perms_sprint_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Proyecto) if 'sprint' in perm.codename]
    perms_actividad_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Proyecto) if 'actividad' in perm.codename]

    #perms_list = [(perm.codename, perm.name) for perm in Permission.objects.all()] #alternativa con una sola lista

    perms_proyecto = forms.MultipleChoiceField(perms_proyecto_list, widget=forms.CheckboxSelectMultiple, label=Proyecto._meta.verbose_name_plural.title(), required=False)
    perms_teammembers = forms.MultipleChoiceField(perms_teammembers_list, widget=forms.CheckboxSelectMultiple, label=MiembroEquipo._meta.verbose_name_plural.title(), required=False)
    perms_userstory = forms.MultipleChoiceField(perms_userstories_list, widget=forms.CheckboxSelectMultiple, label=UserStory._meta.verbose_name_plural.title(), required=False)
    perms_flujo = forms.MultipleChoiceField(perms_flujo_list, widget=forms.CheckboxSelectMultiple, label=Flujo._meta.verbose_name_plural.title(), required=False)
    perms_sprint = forms.MultipleChoiceField(perms_sprint_list, widget=forms.CheckboxSelectMultiple, label=Sprint._meta.verbose_name_plural.title(), required=False)
    perms_actividad = forms.MultipleChoiceField(perms_actividad_list, widget=forms.CheckboxSelectMultiple, label=Actividad._meta.verbose_name_plural.title(), required=False)
    #perms = forms.MultipleChoiceField(perms_list, widget=forms.CheckboxSelectMultiple, label="Permisos", required=False)

    class Meta:
        model = Group
        fields = ["name"]

class UserCreateForm(UserCreationForm):
    '''
    Formulario para la creación de usuarios
    '''
    email = forms.EmailField(required=True)

    general_perms_list = [(perm.codename, perm.name) for perm in general_perms_list()]
    perms_user_list = [(perm.codename, perm.name) for perm in get_perms_for_model(User)]
    perms_group_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Group)]
    general_perms_list.extend(perms_user_list)
    general_perms_list.extend(perms_group_list)
    general_perms = forms.MultipleChoiceField(general_perms_list, widget=forms.CheckboxSelectMultiple, label="General permissions", required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username')