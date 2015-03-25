from django.contrib.auth.models import Group
from django import forms
from guardian.shortcuts import get_perms_for_model
from project.models import Proyecto, Flujo, Sprint, Actividad
from project.models import UserStory


class RolForm(forms.ModelForm):
    perms_proyecto_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Proyecto)]
    perms_userstories_list = [(perm.codename, perm.name) for perm in get_perms_for_model(UserStory)]
    perms_flujo_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Flujo)]
    perms_sprint_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Sprint)]
    perms_actividad_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Actividad)]


    perms_proyecto = forms.MultipleChoiceField(perms_proyecto_list, widget=forms.CheckboxSelectMultiple, label="Permisos de Proyecto", required=False)
    perms_userstory = forms.MultipleChoiceField(perms_userstories_list, widget=forms.CheckboxSelectMultiple, label="Permisos de User Story", required=False)
    perms_flujo = forms.MultipleChoiceField(perms_flujo_list, widget=forms.CheckboxSelectMultiple, label="Permisos de Flujo", required=False)
    perms_sprint = forms.MultipleChoiceField(perms_sprint_list, widget=forms.CheckboxSelectMultiple, label="Permisos de Sprint", required=False)
    perms_actividad = forms.MultipleChoiceField(perms_actividad_list, widget=forms.CheckboxSelectMultiple, label="Permisos de Actividad", required=False)
    class Meta:
        model = Group
        fields = ["name"]
