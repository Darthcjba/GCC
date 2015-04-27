# -*- coding: utf-8 -*-
from guardian.shortcuts import assign_perm, get_perms, remove_perm


def add_permissions_team_member(sender, **kwargs):
    '''
    Signal que se ejecuta cuando se agrega un rol a un miembro de equipo
    que hace que los permisos asociados al rol se asigne.

    :param sender: Clase que envia la signal
    :param kwargs: Diccionario con parámetros
    '''
    instance = kwargs['instance']
    action = kwargs['action']
    exceptions = ['edit_my_userstory', 'registraractividad_my_userstory'] #Permisos a no copiar en el proyecto
    if(action=="post_add"):
        print('add_permissions_team_member triggered')
        #Copiar permisos del grupo al usuario para la instancia del proyecto
        for role in instance.roles.all():
            #print('rol presente en el modelo: ' + role.name)
            for perm in role.permissions.all():
                if not perm.codename in exceptions:
                    assign_perm(perm.codename, instance.usuario, instance.proyecto)