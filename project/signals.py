
from guardian.shortcuts import assign_perm, get_perms, remove_perm


def add_permissions_team_member(sender, **kwargs):
    instance = kwargs['instance']
    action = kwargs['action']
    if(action=="post_add"):
        #Copiar permisos del grupo al usuario para la instancia del proyecto
        for role in instance.rol.all():
            for perm in role.permissions.all():
                assign_perm(perm.codename, instance.usuario, instance.proyecto)
