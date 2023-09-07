from email.policy import default
from django.db import connection, models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from instances.models import Instance
from .managers import UserManager
from datetime import datetime
import uuid
from django.db.models import Q
import datetime
from django.db.models import JSONField

# Les choix
GENRE_CHOICES = (
    ('Mascluin', 'Masculin'),
    ('Féminin', 'Féminin')
)

PERMISSION_CHOICES = (
    ('Create', 'Create'),
    ('Read', 'Read'),
    ('Update', 'Update'),
    ('Delete', 'Delete'),
    ('Manage', 'Manage')
)

class TimeStampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
# User
class User(AbstractBaseUser, PermissionsMixin,TimeStampModel):
    ''' the user for public worker and admins ... '''
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    #REQUIRED_FIELDS = ['email', 'last_name']

    class Meta:
        abstract = True
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

#Fonctions
class Services(TimeStampModel):
    name = models.CharField(max_length=255, null=True)
    service_tutelle = models.IntegerField(null=True, blank=True)
    instance = models.ForeignKey(Instance, related_name='related_instances_service', null=True, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('name','instance')

    
    def __str__(self):
        return '{}'.format(self.name)
    
    def get_subservices(self):
        return Services.objects.filter(service_tutelle=self.id)
    
    def get_utilisateurs(self):
        return Utilisateur.objects.filter(service=self)
    
    def get_servicetutelle(self):
        if self.get_servicetutelle:
            return Services.objects.get(id=self.service_tutelle) or None
        return None

    def get_utilisateurs_for_excel(self):
        return Utilisateur.objects.filter(service=self).all()

    def get_subservices_for_excel(self):
        return Services.objects.filter(service_tutelle=self.id).all()

#Fonctions
class Fonction(TimeStampModel):
    name = models.CharField(max_length=255, unique=False)
    instance = models.ForeignKey(Instance, blank=True, null=True, related_name="related_instance_fonction", on_delete=models.CASCADE)
    sigle = models.CharField(max_length=255, blank=True, null=True, default='')
    # class Meta:
    #     unique_together = ('name','instance')
    
    def __str__(self):
        return '{}'.format(self.name)
    
    def get_utilisateurs(self):
        return Utilisateur.objects.filter(fonction=self)


class Type_Utilisateur(TimeStampModel):
    name = models.CharField(max_length=100, blank=True, null=True)
    can_create_courrier = models.BooleanField(default=False)
    can_transmit_courrier = models.BooleanField(default=False)
    can_annotate_courrier = models.BooleanField(default=False)
    can_assign_courrier = models.BooleanField(default=False)
    can_treat_courrier = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_see_private_assignement = models.BooleanField(default=False)
    permissions = JSONField(default=list, null=True)
    instance = models.ForeignKey(Instance, related_name='instances_type_users', null=True, on_delete=models.CASCADE)
    home = models.CharField(max_length=100, blank=True, null=True, default="mes courriers")

    class Meta:
        unique_together = ('name','instance')
    
    def __str__(self):
        return '{}'.format(self.name)

#Utilisateur
class Utilisateur(User):
    second_email = models.EmailField(unique=False, blank=True, null=True)
    matricule = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=40, default='', null=True)
    last_name = models.CharField(max_length=40, default='', null=True)
    fonction = models.ForeignKey(Fonction, related_name='fonctions', default='', null=True, on_delete=models.DO_NOTHING)
    type_utilisateur = models.ForeignKey(Type_Utilisateur, blank=True, null=True, related_name='type_utilisateurs', on_delete=models.DO_NOTHING)
    phone = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=100, null=True)
    genre = models.CharField(max_length=100, blank=True, choices=GENRE_CHOICES, default='')
    chief = models.IntegerField(null=True)
    has_chief = models.BooleanField(default=False)
    service = models.ForeignKey(Services, related_name='services', default='', null=True, on_delete=models.DO_NOTHING)
    is_chef = models.BooleanField(default=False)
    is_adjoint = models.BooleanField(default=False)
    is_view_statistique = models.BooleanField(default=False)
    instance = models.ForeignKey(Instance, blank=True, null=True, related_name="instance_related_user", on_delete=models.CASCADE)
    isAdminInstance = models.BooleanField(default=False)
    
    def __str__(self):
        return '{}'.format(self.fonction)

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name
    
    def gen_user_folder_name(self):
        return '{}_{}'.format(self.first_name, uuid.uuid4().hex)

    def get_fonction(self):
        return self.fonction
    
    def get_service(self):
        return self.service or ''

    def get_type_utilisateur(self):
        return self.type_utilisateur
    
    def get_instance_name(self):
        return self.instance.name
   
    @property
    def create_excep(self):
        type_utilisateur = Type_Utilisateur.objects.filter(id=self.type_utilisateur.id).first()
        if "ajout_courrier_particulier" in type_utilisateur.permissions:
            return 'type_utilisateur.permissions'
        else:
            return ''
    @property
    def is_annoteur(self):
        configAnnotationInstance = ConfigAnnotationInstance.objects.filter(user__id=self.id).first()
        annoteur = False
        if configAnnotationInstance:
            annoteur = True
        return annoteur

    def hasPermission(self, permission):
        type_utilisateur = Type_Utilisateur.objects.filter(id=self.type_utilisateur.id).first()
        return permission in type_utilisateur.permissions
    
    @property
    def isAdmin(self):
        admin = ConfigAnnotationInstance.objects.filter(user = self).exists()
        return admin
    

    def getConfigAnnotation(self):
        configAnnotationInstance = ConfigAnnotationInstance.objects.filter(user = self).first()
        return configAnnotationInstance
    
    def get_max_fonction(self):
        index_max_config = ConfigAnnotationInstance.objects.filter(instance = self.instance).values_list('index',flat=True)
        configAnnotationInstance = ConfigAnnotationInstance.objects.filter(user = self).first()
        if max(index_max_config) == configAnnotationInstance.index:
            return True
        return False
#Permission
class Permission(TimeStampModel):
    name_permission = models.CharField(max_length=100, blank=True, choices=PERMISSION_CHOICES)
    instance = models.ForeignKey(Instance, blank=True,null=True,related_name="instance_premission", on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.name_permission)

#Type_Utilisateur_Permission
class Type_Utilisateur_Permission(TimeStampModel):
    type_utilisateur = models.ForeignKey(Type_Utilisateur, related_name='type_user_permission', on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, related_name='permission_type_user', on_delete=models.CASCADE)
    instance = models.ForeignKey(Instance, blank=True,null=True,related_name="instance_user_permission", on_delete=models.CASCADE)


#Track_Actions
class Track_Actions(TimeStampModel):
    user = models.ForeignKey(Utilisateur, related_name='trackActions', on_delete=models.CASCADE)
    page = models.CharField(max_length=900)
    ip_addresse = models.CharField(max_length=900)
    navigateur = models.CharField(max_length=900)
    action_effectue = models.CharField(max_length=900)
    date_action = models.DateField(auto_now_add=True)
    heure = models.TimeField(auto_now_add=True)
    instance = models.ForeignKey(Instance, blank=True,null=True,related_name="instance_track_action", on_delete=models.CASCADE)
    
    @property
    def user_time(self):
        users_action_ids = [track.id for track in Track_Actions.objects.filter(user_id=self.user_id, action_effectue="Déconnexion ",date_action__year=self.date_action.year, date_action__month=self.date_action.month).order_by('id')]
        users_connection = [track.id for track in Track_Actions.objects.filter(user_id=self.user_id, action_effectue="Connexion ",date_action__year=self.date_action.year, date_action__month=self.date_action.month).order_by('id')]
        users_actions = [track.id for track in Track_Actions.objects.filter(user_id=self.user_id,date_action__year=self.date_action.year, date_action__month=self.date_action.month).order_by('id')]

        times = datetime.timedelta(seconds=0)

        for time in users_connection:
            firt_id = time 
            last_id = time
            time_add = 0
            if(users_connection.index(time)<len(users_connection)-1):
                next_id = users_connection[users_connection.index(time)+1]
                deconnection = users_actions[users_actions.index(next_id)-1]
                if deconnection in users_action_ids:
                    last_id = deconnection
                else:
                    last_id = deconnection
                    time_add = 3600
            elif len(users_action_ids)>0:
                if(users_action_ids[len(users_action_ids)-1]==users_actions[len(users_actions)-1]):
                    last_id = users_actions[len(users_actions)-1]
                else:
                    last_id = time
            
                    # return None
            connection = Track_Actions.objects.filter(user_id=self.user_id,pk = firt_id).all() 
            tracks_deconnections = Track_Actions.objects.filter(user_id=self.user_id,pk = last_id).all() 
            heure_debut = connection[0].heure
            heure_fin = tracks_deconnections[0].heure
            date_debut =connection[0].date_action
            date_fin = tracks_deconnections[0].date_action
            
            first_t = datetime.datetime.combine(date_debut,heure_debut)
            last_t = datetime.datetime.combine(date_fin,heure_fin)
            
            days, hr = divmod((last_t - first_t).total_seconds() +time_add, 86400)
            hr, min = divmod(hr,3600)
            min, sec = divmod(min,60)
            times += datetime.timedelta(hours=hr, minutes=min, seconds=sec)
        days, hr = divmod(times.total_seconds(), 86400)
        hr, min = divmod(hr,3600)
        min, sec = divmod(min,60)   
        return " %d Jours - %d Heures  - %02d Munites  - %02d Seconds " % (days, hr, min, sec)

    @property
    def calcul_time_by_day(self):
        users_action_ids = [track.id for track in Track_Actions.objects.filter(user_id=self.user_id, action_effectue="Déconnexion ",date_action__year=self.date_action.year, date_action__month=self.date_action.month).order_by('id')]
        users_connection = [track.id for track in Track_Actions.objects.filter(user_id=self.user_id, action_effectue="Connexion ",date_action__year=self.date_action.year, date_action__month=self.date_action.month).order_by('id')]
        users_actions = [track.id for track in Track_Actions.objects.filter(user_id=self.user_id).order_by('id')]
        firt_id = self.id 
        last_id = self.id
        time_add = 0
        if(users_connection.index(self.id)<len(users_connection)-1):
            next_id = users_connection[users_connection.index(self.id)+1]
            deconnection = users_actions[users_actions.index(next_id)-1]
            if deconnection in users_action_ids:
                last_id = deconnection
            else:
                last_id = deconnection
                time_add = 3600
        else:
            if(users_action_ids[len(users_action_ids)-1]==users_actions[len(users_actions)-1]):
                last_id = users_actions[len(users_actions)-1]
            else:
                last_id = self.id
                return None

        # print(users_connection.index(self.id))
        connection = Track_Actions.objects.filter(user_id=self.user_id,pk = firt_id).all() 
        tracks_deconnections = Track_Actions.objects.filter(user_id=self.user_id,pk=last_id).all() 
        heure_debut = connection[0].heure
        heure_fin = tracks_deconnections[0].heure
        date_debut =connection[0].date_action
        date_fin = tracks_deconnections[0].date_action
        
        first_t = datetime.datetime.combine(date_debut,heure_debut)
        last_t = datetime.datetime.combine(date_fin,heure_fin)
        
        days, hr = divmod((last_t - first_t).total_seconds() +time_add , 86400)
        hr, min = divmod(hr,3600)
        min, sec = divmod(min,60)
        
        return "Heures %d - Munites %02d - Seconds %02d" % (hr, min, sec)
    
    def heure_connexion(self):
        firt_id = self.id
        connection = Track_Actions.objects.filter(user_id=self.user_id,pk = firt_id).all() 
        heure_debut = connection[0].heure
        return heure_debut.strftime("%H:%M:%S")
    
    def heure_deconnexion(self):
        users_action_ids = [track.id for track in Track_Actions.objects.filter(user_id=self.user_id, action_effectue="Déconnexion ").order_by('id')]
        users_connection = [track.id for track in Track_Actions.objects.filter(user_id=self.user_id, action_effectue="Connexion ").order_by('id')]
        last_id = self.id
        users_actions = [track.id for track in Track_Actions.objects.filter(user_id=self.user_id).order_by('id')]
        time_add = 0
        if(users_connection.index(self.id)<len(users_connection)-1):
            next_id = users_connection[users_connection.index(self.id)+1]
            deconnection = users_actions[users_actions.index(next_id)-1]
            if deconnection in users_action_ids:
                last_id = deconnection
            else:
                last_id = deconnection
                time_add = 3600
        else:
            if(users_action_ids[len(users_action_ids)-1]==users_actions[len(users_actions)-1]):
                last_id = users_actions[len(users_actions)-1]
            else:
                last_id = self.id
                return None

        tracks_deconnections = Track_Actions.objects.filter(user_id=self.user_id,pk=last_id).all() 
        def addSecs(tm, secs):
            fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
            fulldate = fulldate + datetime.timedelta(seconds=secs)
            return fulldate.time()
        heure_fin = addSecs(tracks_deconnections[0].heure , time_add) 

        return heure_fin.strftime("%H:%M:%S")   


CATEGORY_COMPANY = (
    ('Departement','Departement'),
    ('Gouvernement','Gouvernement'),
    ('Institution','Institution'),
    ('Direction','Direction'),
)
class Company(TimeStampModel):
    name = models.CharField(max_length=5000,  default='APPLICATION DE GESTION DE COURRIERS')
    logo = models.CharField(max_length=255,blank=True)
    sigle = models.CharField(max_length=255,blank=True, null=True)
    type = models.CharField(max_length=255,blank=True, null=True, default='oui')
    category = models.CharField(max_length=255,blank=True, null=True, choices=CATEGORY_COMPANY)
        
    def __str__(self):
        self.name = self.name.upper()
        return '{}'.format(self.name)
    

class CompanyFonction(TimeStampModel):
    fonction = models.ForeignKey(Fonction,related_name='company_function_related',on_delete=models.CASCADE, blank=True)
    company = models.ForeignKey(Company,related_name='company_related_name', on_delete=models.CASCADE, blank=True,null=True)
    user = models.ForeignKey(Utilisateur,related_name='utilisateur_related_name', on_delete=models.CASCADE, blank=True,null=True)
    order = models.IntegerField(blank=True, null=True)
    genre = models.CharField(max_length=255, blank=True, null=True)
    message_annotation = models.TextField(blank=True)
    
    def __str__(self):
        return self.fonction.name
    
    
class ConfigAnnotationInstance(TimeStampModel):
    instance = models.ForeignKey(Instance,blank=True, null=True, related_name="instance_fonction_annotation", on_delete=models.CASCADE)
    user = models.ForeignKey(Utilisateur, blank=True, null=True, related_name="user_instance_annotation", on_delete=models.CASCADE)
    index = models.IntegerField(blank=True, null=True)
    genre = models.CharField(max_length=255, blank=True, null=True)
    message_annotation = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-index']
