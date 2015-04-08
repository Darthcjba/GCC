
from guardian.shortcuts import assign_perm


def add_permissions_team_member(sender, **kwargs):
    instance = kwargs['instance']
    #Copiar permisos del grupo al usuario para la instancia del proyecto
    for role in instance.rol.all():
        for perm in role.permissions.all():
            assign_perm(perm.codename, instance.usuario, instance.proyecto)


