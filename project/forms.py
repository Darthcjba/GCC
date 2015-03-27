from django.contrib.auth.models import Group, Permission, User
from django import forms
from guardian.shortcuts import get_perms_for_model
from project.models import Proyecto, Flujo, Sprint, Actividad, MiembroEquipo
from project.models import UserStory


class RolForm(forms.ModelForm):

    perms_proyecto_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Proyecto)]
    perms_teammembers_list = [(perm.codename, perm.name) for perm in get_perms_for_model(MiembroEquipo)]
    perms_userstories_list = [(perm.codename, perm.name) for perm in get_perms_for_model(UserStory)]
    perms_flujo_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Flujo)]
    perms_sprint_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Sprint)]
    perms_actividad_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Actividad)]
    perms_user_list = [(perm.codename, perm.name) for perm in get_perms_for_model(User)]
    perms_group_list = [(perm.codename, perm.name) for perm in get_perms_for_model(Group)]

    #perms_list = [(perm.codename, perm.name) for perm in Permission.objects.all()] #alternativa con una sola lista

    perms_proyecto = forms.MultipleChoiceField(perms_proyecto_list, widget=forms.CheckboxSelectMultiple, label=Proyecto._meta.verbose_name_plural, required=False)
    perms_teammembers = forms.MultipleChoiceField(perms_teammembers_list, widget=forms.CheckboxSelectMultiple, label=MiembroEquipo._meta.verbose_name_plural, required=False)
    perms_userstory = forms.MultipleChoiceField(perms_userstories_list, widget=forms.CheckboxSelectMultiple, label=UserStory._meta.verbose_name_plural, required=False)
    perms_flujo = forms.MultipleChoiceField(perms_flujo_list, widget=forms.CheckboxSelectMultiple, label=Flujo._meta.verbose_name_plural, required=False)
    perms_sprint = forms.MultipleChoiceField(perms_sprint_list, widget=forms.CheckboxSelectMultiple, label=Sprint._meta.verbose_name_plural, required=False)
    perms_actividad = forms.MultipleChoiceField(perms_actividad_list, widget=forms.CheckboxSelectMultiple, label=Actividad._meta.verbose_name_plural, required=False)
    perms_user = forms.MultipleChoiceField(perms_user_list, widget=forms.CheckboxSelectMultiple, label=User._meta.verbose_name_plural, required=False)
    perms_group = forms.MultipleChoiceField(perms_group_list, widget=forms.CheckboxSelectMultiple, label=Group._meta.verbose_name_plural, required=False)
    #perms = forms.MultipleChoiceField(perms_list, widget=forms.CheckboxSelectMultiple, label="Permisos", required=False)
    class Meta:
        model = Group
        fields = ["name"]
