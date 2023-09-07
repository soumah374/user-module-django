from rolepermissions.roles import AbstractUserRole

class SuperAdmin(AbstractUserRole):
   available_permissions = {
       'view_utilisateur': True,
       'delete_utilisateur': True
   }

class Administrateur(AbstractUserRole):
   available_permissions = {
       'create_utilisateur': True,
   }
class Secretaire(AbstractUserRole):
    available_permissions = {
        'create_courrier': True,
        'view_courrier': True,
    }

class Executant(AbstractUserRole):
    available_permissions = {
        'view_courrier': True,
    }
