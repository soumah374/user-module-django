import re
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.aggregates import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse  
from django.urls import reverse, reverse_lazy
from django.core.exceptions import ImproperlyConfigured
from django.views import generic
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth.forms import PasswordChangeForm
# from django.contrib.auth.forms import PasswordChangeForm
## Here
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from config.settings import MEDIA_URL, STATIC_ROOT
import posixpath
from ged.models import Content
from instances.helper import seed_content
from user.constance import PAGES, SUPER_ADMINISTRATEUR
from .utils import (checking_user_fonction, determineUserType, getName, 
                    index_user_fonction,
                    genre_user_fonction,
                    message_annotation,
                    get_order)
from .tokens import account_activation_token
from config import settings
from user.forms import *
from user.models import *
from gec.models import Company
import datetime
from django.template.loader import render_to_string
from rolepermissions.roles import assign_role
from django.db.models.functions import TruncMonth

from django.contrib.auth.hashers import make_password
from math import *
#log
from gec.utils import action_log, getSecretaireCentralToInstance

from django.db.models import Max, Q
from notifications.signals import notify
from notifications.models import Notification
from gec.models import SentMail
import json as simplejson
from gec.utils import authorizations
import xlsxwriter
import io
from django.core.files.storage import FileSystemStorage
from .permissions import allPermissions
import json
from itertools import chain
import pandas as pd

class RegistrationView(generic.CreateView):
    form_class = RegistrationForm
    form_valid_message = ('you have successfully signed up')
    success_url = reverse_lazy('user:login')
    model = Utilisateur
    template_name = 'user/register.html'


class LoginView(generic.FormView):
    form_class = LoginForm
    form_valid_message = 'you are logged in'
    model = Utilisateur
    success_url = reverse_lazy('gec:liste_courriers_entrant', kwargs={'src': 1})
    template_name = 'user/login.html'
    user = Utilisateur()
    
    

    def get_success_url(self):
        """
        Returns the supplied URL.
        """
        secretaire_fonction = "Secrétaire Général"
        
        url = None
        if self.success_url:
            for p in PAGES:
                if self.request.user.get_type_utilisateur().home:
                    if p["page"] == self.request.user.get_type_utilisateur().home:
                        if p["parametre"] is not None:
                            url = reverse_lazy(p["lien"], kwargs={'src': p["parametre"]})
                        else:
                            url = reverse_lazy(p["lien"])
                else:
                   url = reverse_lazy('gec:liste_courriers_entrant', kwargs={'src': 3})
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model."
                )
        action_log(self.request,"Connexion - Connexion ", "Connexion ")
        return url

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(self.request, user)
            
            # Save the logged User for Api Security cheking
            # logged_user = CurrentUserForApi()
            # logged_user = user
            # logged_user.save()
            # Save the logged User for Api Security cheking

            return super().form_valid(locals())
        else:
            return self.form_invalid(locals())

    def form_invalid(self, form) -> HttpResponse:
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        print(user)
        if user:
            form.errors.clear()
            form.add_error(None, "Compte Désactivé, Veuillez contacter votre administrateur !")

        return super().form_invalid(form)

    def can_view_dashboard(self,user):
        permi1 = user.hasPermission("view_courrier_normal_entrant_stat")
        permi2 = user.hasPermission("view_courrier_normal_sortant_stat")
        permi3 = user.hasPermission("view_courrier_particulier_entrant_stat")
        permi4 = user.hasPermission("view_courrier_particulier_sortant_stat")
        permi5 = user.hasPermission("view_courrier_normal_done_time_stat")
        permi6 = user.hasPermission("view_courrier_particulier_done_time_stat")
        permi7 = user.hasPermission("view_courrier_normal_done_late_stat")
        permi8 = user.hasPermission("view_courrier_particulier_done_late_stat")
        permi9 = user.hasPermission("view_courrier_normal_transmit_stat")
        permi10 = user.hasPermission("view_courrier_particulier_transmit_stat")
        if permi1 or permi2 or permi3 or permi4 or permi5 or permi6 or permi7 or permi8 or permi9 or permi10:
            return True
        else:
            return False
        
def logout_view(request):

    action_log(request,"Mon compte - Déconnexion", "Déconnexion ")
    # Deleting the logged User for Api Security cheking
    # user_to_log_out = CurrentUserForApi.objects.first()
    # user_to_log_out.delete()
    # Deleting the logged User for Api Security cheking

    logout(request)
    return redirect(reverse_lazy('user:login'))

@login_required
def change_password(request):
    action_log(request,"Mon compte - Changer mon mot de passe", "Affichage de la page changement de mot de passe")
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            action_log(request,"Mon compte - Changer mon mot de passe", "Mise à jour de mot de passe utilisateur")
            
            messages.success(request, ('Votre mot de passe a ete mis a jour!'))
            return redirect('user:login')
        else:
            messages.error(request, ('SVP Corrigez les erreurs ci-dessus!'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user/change_password.html', {
        'form': form,
        'active_profile': True
        })


def create_success(request):
    action_log(request,"Creation de compte ", "Affichage de la page de reussite de la création de compte")
    return render(request, 'user/create_success.html',)


@login_required
def user_account(request, user_id):
    utilisateur = Utilisateur.objects.get(id=user_id)
    action_log(request,"Mon compte ", "Affichage du compte utilisateur")
    return render(request, 'user/user_account.html', {'user': utilisateur, 'active_ass_users': True})


@login_required
def utilisateur_profile(request, user_id):
    user = Utilisateur.objects.get(id=user_id)
    if request.user.type_utilisateur.name == SUPER_ADMINISTRATEUR:
        fonctions = Fonction.objects.filter(instance__isnull = True).all()
        services = Services.objects.filter(instance__isnull = True).all()
        type_utilisateurs = Type_Utilisateur.objects.filter(instance__isnull = True).all()
    else:
        fonctions = Fonction.objects.filter(instance = request.user.instance).all()
        services = Services.objects.filter(instance = request.user.instance).all()
        type_utilisateurs = Type_Utilisateur.objects.filter(instance = request.user.instance).all()
    action_log(request,"Mon compte - Mon profile ", "Affichage de la page du profile utilisateur")


    return render(request, 'user/utilisateur_profile.html', {
        'users': user,
        'services': services,
        'fonctions': fonctions,
        'type_utilisateurs': type_utilisateurs,
        'genders': GENRE_CHOICES,
        'active_profile': True
    })

@login_required
def update_utilistateur_profile(request, user_id):
    user = Utilisateur.objects.get(id=user_id)
    if request.method == 'POST':
        user.email = request.POST.get('email', None).lower()
        user.second_email = request.POST.get('second_email', None).lower()
        user.first_name = request.POST.get('first_name', None)
        user.last_name = request.POST.get('last_name', None)
        user.phone = request.POST.get('phone', '')
        user.address = request.POST.get('address', None)
        user.genre = request.POST.get('gender', None)
        user.fonction = Fonction.objects.get(id=request.POST.get('fonction', None))

        user.save()
       
        action_log(request,"Mon compte - Mon profile  ", "Mise à jour du profile utilisateur")


        messages.success(request, ('Votre profile a ete mis a jour'))
        
        if user.is_admin:
            return redirect('user:utilisateurs')
        elif user.type_utilisateur.name == "Administrateur":
            return redirect('gec:liste_courriers_entrant', 1)
        else:
            return redirect('gec:liste_courriers_entrant', 3)
    else:
        return redirect('gec:utilisateur_profile', user.id)

#@login_required
def register2(request, *args, **kwargs):


    form = UtilisateurForm2(request.POST)
    utilisateur = get_object_or_404(Utilisateur, email=request.POST.get('user_email'))

    if request.method == 'POST':
        form = UtilisateurForm2(request.POST)
        utilisateur = get_object_or_404(Utilisateur, email=request.POST.get('user_email'))
        admin = Utilisateur.objects.get(isAdminInstance=True, instance=utilisateur.instance)

        form_is_valid = False
        check_password = True
        if request.POST.get('matriculgec_minee') == '':
            form_is_valid = False
        elif request.POST.get('first_name')   == '':
            form_is_valid = False
        elif request.POST.get('last_name')    == '':
            form_is_valid = False
        elif request.POST.get('genre')        == '':
            form_is_valid = False
        elif request.POST.get('phone')       == '':
            form_is_valid = False
        elif request.POST.get('type_utilisateur') == '':
            form_is_valid = False
        elif request.POST.get('fonction') == '':
            form_is_valid = False
        elif request.POST.get('password')     == '':
            form_is_valid = False
        elif request.POST.get('confirmation') == '':
            form_is_valid = False
        elif request.POST.get('address')      == '':
            form_is_valid = False
        elif request.POST.get('password') != request.POST.get('confirmation'):
            form_is_valid = False
            check_password = False
        else:
            form_is_valid = True

        if form_is_valid:
            utilisateur.matricule  = request.POST.get('matricule')
            utilisateur.first_name = request.POST.get('first_name')
            utilisateur.last_name  = request.POST.get('last_name')
            utilisateur.genre      = request.POST.get('genre')
            utilisateur.phone     = request.POST.get('phone')
            utilisateur.second_email = request.POST.get('second_email')
            # utilisateur.service = service
            # utilisateur.fonction = fonction
            utilisateur.address    = request.POST.get('address')
            utilisateur.password   = make_password(request.POST.get('password'))
            
            if hasattr(request.user, "isAdminInstance"):
                if request.user.isAdminInstance:
                    utilisateur.instance = request.user.instance
            
            utilisateur.is_active = True
            utilisateur.save()

            ###################
            current_site = get_current_site(request)
            message = render_to_string('mails/user_request_validated.html', {
                'user_registered': utilisateur,
                'user_admin': admin,
                'domain': current_site.domain,
            })
            email = SentMail()
            email.title = 'Validation d\'enregistrement.'
            email.email = admin.email
            email.message = message
            email.save()

            ###################

            #assign_role(utilisateur, 'normal')
            #action_log(request,"Enregistrement  ", "Validaion et Enregistrement d'un nouveau utilisateur")


            messages.success(request, 'Enregistrement effectué avec succes, Veillez vous connectez')
            #return redirect('utilisateur_profile', user_id=utilisateur.id)
            logout(request)
            return redirect(reverse_lazy('user:login'))
    return render(request, 'user/utilisateur_himself.html', {'form': form, 'user': utilisateur})


# @authorizations('Super administrateur','Administrateur')
def utilisateur_details(request, user_id):
    action_log(request,"Utilisateurs - Détails utilisateurs ", "Affichage des details d'un utilisateur")

    utilisateur = Utilisateur.objects.get(id=user_id)
    chef = None

    if utilisateur.chief:
        chef = Utilisateur.objects.get(id=utilisateur.chief).fonction

    return render(request, 'user/utilisateur_details.html', {'utilisateur': utilisateur, 'chef': chef, 'active_ass_users': True})

# @authorizations('Super administrateur')
def view_statistique(request, user_id):
    action_log(request,"Utilisateurs - Afficher les statistique", "Autoriser l'affichage de la statistique")
    utilisateur = Utilisateur.objects.get(id=user_id)
    
    if utilisateur.is_view_statistique:
        utilisateur.is_view_statistique = False
    else:
        utilisateur.is_view_statistique = True
    utilisateur.save()
    return redirect("/user/details-d-un-utilisateur/{}".format(utilisateur.id))
    

# @authorizations('Super administrateur','Administrateur')
def list_utilisateur(request):
    if(request.user.isAdminInstance):
        all_user = Utilisateur.objects.filter(instance = request.user.instance).all()
    else:
        adminInstance = Utilisateur.objects.filter(isAdminInstance = True) 
        superAdmin =  Utilisateur.objects.filter(is_superuser = True)
        all_user = list(chain( superAdmin, adminInstance))
    action_log(request,"Utilisateurs - Utilisateurs", "Affichage de la listes des utilisateurs")
    excel_export_user = request.GET.get('list_user')
    if(excel_export_user):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output,{'remove_timezone': True})
        worksheet = workbook.add_worksheet()

        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': 1,'valign':   'vcenter'})
        bold.set_align("center")

        # Add a number format for cells with money.
        money_format = workbook.add_format({'num_format': '$#,##0'})

        # Add an Excel date format.
        date_format = workbook.add_format({'num_format': 'd/mm/YYYY','valign':   'vcenter'})
        date_format.set_align('center')
        date_format1 = workbook.add_format({'num_format': 'd/mm/YYYY','valign':   'vcenter'})
        default_format = workbook.add_format({'valign':   'vcenter', 'text_wrap': True})
        default_format.set_align('center')

        # Adjust the column width.
        # worksheet.set_column(1, 1, 15)
        worksheet.set_column(1, 9, 26)

        columns = ['#','Prénoms', 'Nom', 'Genre', "Email", "Télephone","Service","Fonction", "Status", "Activer / Desactiver"]

        merge_format = workbook.add_format({
        'bold':     True,
        'border':   1,
        'align':    'center',
        'valign':   'vcenter',
        'text_wrap': True
        })
        # worksheet.set_column('H:M', 15)
        # worksheet.set_row(1, 30)
        for col_num in range(len(columns)):
            if col_num <= 9:
                worksheet.merge_range(0,col_num,1,col_num, columns[col_num], merge_format)
        
        # Start from the first cell below the headers.
        row = 1
        col = 0
        row_num = 1

        for row in range(len(all_user)):
            row_num += 1
            worksheet.set_row_pixels(row_num, 50)
            worksheet.write_number(row_num, col, row_num-1,default_format)
            worksheet.write_string(row_num,col + 1, all_user[row].first_name,default_format)
            worksheet.write_string(row_num,col + 2, all_user[row].last_name,default_format)
            if all_user[row].genre != None:
                worksheet.write_string(row_num,col + 3, all_user[row].genre,default_format)
            else:
                worksheet.write_string(row_num,col + 3, " ",default_format)

            worksheet.write_string(row_num,col + 4, all_user[row].email,default_format)
            if all_user[row].phone != None:
                worksheet.write_string(row_num,col + 5, all_user[row].phone,default_format)
            else:
                worksheet.write_string(row_num,col + 5, " ",default_format)
            if all_user[row].service_id != None:
                worksheet.write_string(row_num,col + 6, all_user[row].service.name,default_format)
            else:
                worksheet.write_string(row_num,col + 6, " ",default_format)
            worksheet.write_string(row_num,col + 7, all_user[row].fonction.name,default_format)
            if all_user[row].first_name == '' and all_user[row].last_name == '':
                worksheet.write_string(row_num,col + 8, " encours",default_format)
            else:
                worksheet.write_string(row_num,col + 8, "actif",default_format)

            if all_user[row].is_active:
                if all_user[row].last_login is None and all_user[row].first_name == '' and all_user[row].last_name == '':
                    worksheet.write_string(row_num,col + 9, " encours ",default_format)
                else:
                    worksheet.write_string(row_num,col + 9, " Desactivé",default_format)
            else:
                if all_user[row].last_login is None and all_user[row].first_name == '' and all_user[row].last_name == '':
                    worksheet.write_string(row_num,col + 9, " encours ",default_format)
                else:
                    worksheet.write_string(row_num,col + 9, " Activé",default_format)

        workbook.close()
        output.seek(0)
        filename = 'Liste des utilisateurs.xlsx'
        response = HttpResponse(output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

    return render(request, 'user/list_utilisateurs.html', {'all_user': all_user, 'active_ass_users': True})

# @authorizations('Super administrateur','Administrateur')
def update_utilisateur(request, user_id):
    utilisateur = get_object_or_404(Utilisateur, pk=user_id)
    action_log(request,"Utilisateurs - Utilisateurs - Editer ", "Affichage page Mise à jour d'un utilisateur ")
    chef = None

    if utilisateur.chief:
        chef = Utilisateur.objects.get(id=utilisateur.chief).fonction

    form = UpdateUtilisateurForm(utilisateur=utilisateur, current_user=request.user)

    if request.method == 'POST':
        if request.POST.get('fonction') == 'autre':
            fonction = Fonction(name= request.POST.get('other_fonction'), instance=request.user.instance)
            fonction.save()
        else:
            fonction = Fonction.objects.get(id=int(request.POST.get('fonction')))
            

        if request.POST.get('service') == 'autre':
            service = Services(name= request.POST.get('other_service'), instance=request.user.instance)
            service.save()
        else:
            service = Services.objects.get(id=int(request.POST.get('service')))

        if utilisateur.is_superuser == False:
            type_utilisateur = Type_Utilisateur.objects.filter(id=request.POST.get('type_utilisateur'), instance=request.user.instance).first()
        
        if request.user.is_superuser == True:
            type_utilisateur = Type_Utilisateur.objects.filter(id=request.POST.get('type_utilisateur'), instance=utilisateur.instance).first()
            
        utilisateur.matricule = request.POST.get('matricule')
        utilisateur.first_name = request.POST.get('first_name')
        utilisateur.last_name = request.POST.get('last_name')
        utilisateur.email = request.POST.get('email').lower()
        utilisateur.second_email = request.POST.get('second_email').lower()
        utilisateur.genre = request.POST.get('genre')
        utilisateur.service = service
        utilisateur.fonction = fonction
        utilisateur.phone = request.POST.get('phone')
        
        if request.user.isAdminInstance:
            utilisateur.instance = request.user.instance

        is_chef = request.POST.get('is_chef')
        is_adjoint = request.POST.get('is_adjoint')

        if is_chef == 'on':
            utilisateur.is_adjoint = False
            utilisateur.is_chef = True
        elif is_chef == None:
            utilisateur.is_chef = False

        if is_adjoint == 'on':
            utilisateur.is_chef = False
            utilisateur.is_adjoint = True
        elif is_adjoint == None:
            utilisateur.is_adjoint = False

            
        if utilisateur.is_superuser == False:
            utilisateur.type_utilisateur = type_utilisateur
        elif utilisateur.is_superuser == True and not utilisateur.id == request.user.id:
            utilisateur.type_utilisateur = type_utilisateur

        utilisateur.address = request.POST.get('address')

        utilisateur.save()

        content_default = Content.objects.filter(model_de_contenu="ARCHIVES", instance=request.user.instance, parent__isnull=True).first()
        content = Content.objects.filter(model_archive="BASE ACTIVE", instance=request.user.instance, parent=content_default).first()
        
        if content is None and request.user.isAdminInstance:
            seed_content(instance=request.user.instance.id,user=utilisateur)
        
        messages.success(request, 'Vous avez bien modifié l\'utilisateur')

        action_log(request,"Utilisateurs - Utilisateurs ", "Mise à jour d'un utilisateur "+ str(utilisateur))


        return redirect('user:utilisateurs')
    if request.user.instance: 
        type_utilisateurs = Type_Utilisateur.objects.filter(instance = request.user.instance).exclude(name=SUPER_ADMINISTRATEUR).all()
        services = Services.objects.filter(instance = request.user.instance).exclude(name=SUPER_ADMINISTRATEUR).all()
        fonctions = Fonction.objects.filter(instance = request.user.instance).exclude(name=SUPER_ADMINISTRATEUR).all()
    else:
        if utilisateur.instance == None:
            type_utilisateurs = Type_Utilisateur.objects.filter(instance__isnull=True).exclude(name=SUPER_ADMINISTRATEUR).all()
            services = Services.objects.filter(instance__isnull=True).exclude(name=SUPER_ADMINISTRATEUR).all()
            fonctions = Fonction.objects.filter(instance__isnull=True).exclude(name=SUPER_ADMINISTRATEUR).all()
        else:
            type_utilisateurs = Type_Utilisateur.objects.filter(instance=utilisateur.instance).exclude(name=SUPER_ADMINISTRATEUR).all()
            services = Services.objects.filter(instance=utilisateur.instance).exclude(name=SUPER_ADMINISTRATEUR).all()
            fonctions = Fonction.objects.filter(instance=utilisateur.instance).exclude(name=SUPER_ADMINISTRATEUR).all()
    
    return render(request, 'user/update_utilisateur.html', {
        'form': form, 
        'utilisateur': utilisateur, 
        'chef': chef, 
        'active_ass_users': True,
        'type_utilisateurs': type_utilisateurs,
        'services': services,
        'fonctions': fonctions,
    })

# @authorizations('Super administrateur','Administrateur')
def delete_utilistateur(request, user_id):
    if request.user.is_admin:
        user = Utilisateur.objects.get(id=user_id)
        user.delete()

        action_log(request,"Utilisateurs - Utilisateurs ", "Suppression d'un utilisateur " + user)
        messages.success(request, ('Compte utilistateur Supprime avec success'))
        return redirect('user:utilisateurs')

# @authorizations('Super administrateur','Administrateur')
def add_function(request):
    
    form = FonctionForm(request.POST or None)
    action_log(request,"Utilisateurs - Fonctions ", "Affichage de la liste des types de fonctions ")
    prints = request.GET.get('prints')

    if request.user.isAdminInstance:
        fonction = Fonction.objects.filter(instance = request.user.instance).all()
    else:
        fonction = Fonction.objects.filter(instance__isnull=True).all()

    if request.method == "POST":
        if form.is_valid():
            name = form.cleaned_data['name']
            sigle = form.cleaned_data['sigle']
            fonction = Fonction()
            fonction.name = name
            fonction.sigle = sigle
            if request.user.isAdminInstance:
                fonction.instance = request.user.instance
            fonction.save()
            action_log(request,"Utilisateurs - Fonctions ", "Ajout d'une nouvelle Fonction ")
            return redirect('user:function')
    if prints:
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output,{'remove_timezone': True})
        worksheet = workbook.add_worksheet()

        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': 1,'valign':   'vcenter'})
        bold.set_align("center")

        # Add a number format for cells with money.
        money_format = workbook.add_format({'num_format': '$#,##0'})

        # Add an Excel date format.
        date_format = workbook.add_format({'num_format': 'd/mm/YYYY','valign':   'vcenter'})
        date_format.set_align('center')
        date_format1 = workbook.add_format({'num_format': 'd/mm/YYYY','valign':   'vcenter'})
        default_format = workbook.add_format({'valign':   'vcenter', 'text_wrap': True})
        default_format.set_align('center')

        # Adjust the column width.
        # worksheet.set_column(1, 1, 15)
        worksheet.set_column(1, 8, 26)

        columns = ['#','Fonction ', 'Date de Création']

        merge_format = workbook.add_format({
        'bold':     True,
        'border':   1,
        'align':    'center',
        'valign':   'vcenter',
        'text_wrap': True
        })
        # worksheet.set_column('H:M', 15)
        # worksheet.set_row(1, 30)
        for col_num in range(len(columns)):
            if col_num <= 5:
                worksheet.merge_range(0,col_num,1,col_num, columns[col_num], merge_format)
        
        # Start from the first cell below the headers.
        row = 1
        col = 0
        row_num = 1

        for row in range(len(fonction)):
            row_num += 1
            worksheet.set_row_pixels(row_num, 50)
            worksheet.write_number(row_num, col, row_num-1,default_format)
            worksheet.write_string(row_num,col + 1, fonction[row].name,default_format)
            worksheet.write_datetime(row_num,col + 2, fonction[row].created_at, date_format)
        
        workbook.close()
        output.seek(0)
        filename = 'Liste des fonctions des utilisateurs.xlsx'
        response = HttpResponse(output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
    
    return render(request, 'user/liste_functions.html', {'form': form, 'fonctions': fonction, 'active_ass_users': True, 'prints':prints})

# @authorizations('Super administrateur','Administrateur')
def delete_function(request, delete_id):
    fonction = Fonction.objects.get(id=delete_id)
    fonction.delete()
    action_log(request,"Utilisateurs - Fonctions ", "Suppression d'une Fonction ")
    return redirect('user:function')

# @authorizations('Super administrateur','Administrateur')
def update_function(request, function_id):
    fonction = Fonction.objects.get(id=function_id)
    form = FonctionForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data['name']
            sigle = form.cleaned_data['sigle']
            fonction.name = name
            fonction.sigle = sigle
            if request.user.isAdminInstance:
                fonction.instance = request.user.instance
            fonction.save()
            action_log(request,"Utilisateurs - Fonctions ", "Mise a jour d'une Fonction ")
            return redirect('user:function')
    messages.error(request,('Erreur! s\'est produite lors du post'))
    return redirect('user:function')

# @authorizations('Super administrateur','Administrateur')
def list_type_user(request):
    form = TypeUtilisateurForm(request.POST or None)
    form_perm = PermissionForm(request.POST or None)
    prints = request.GET.get('prints')
    action_log(request,"Utilisateurs - Types Utilisateurs ", "Affichage de la liste des types utilisateurs ")
    try:
        if request.user.isAdminInstance or request.user.is_superuser:
            type_utilisateurs = Type_Utilisateur.objects.filter(instance = request.user.instance).all()
        else:
            type_utilisateurs = Type_Utilisateur.objects.filter(instance__isnull=True).all()

    except expression as identifier:
        pass
    
    if request.method == "POST":
        
        if form.is_valid():
            permissions = request.POST.getlist("permissions")
            name = form.cleaned_data['name']
            exist = False
               
            for type_user in type_utilisateurs:
                if type_user.name == name:
                    exist = True
                    break
            if exist:
                messages.error(request, 'Cet type utilisateur existe, donnez un autre type')
                return redirect('user:type_utilisateur')
            else:
                type_utilisateur = Type_Utilisateur()
                type_utilisateur.name = name
                # PERMISSIONS
                type_utilisateur.permissions = permissions
                if request.user.isAdminInstance or request.user.is_superuser:
                    type_utilisateur.instance = request.user.instance
                type_utilisateur.save()
                action_log(request,"Utilisateurs - Type Utilisateurs ", "Ajout d'un Type Utilisateur ")
                messages.success(request, ('Type utilisateur ajoute avec success'))
                return redirect('user:type_utilisateur')
    if prints:
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output,{'remove_timezone': True})
        worksheet = workbook.add_worksheet()

        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': 1,'valign':   'vcenter'})
        bold.set_align("center")

        # Add a number format for cells with money.
        money_format = workbook.add_format({'num_format': '$#,##0'})

        # Add an Excel date format.
        date_format = workbook.add_format({'num_format': 'd/mm/YYYY','valign':   'vcenter'})
        date_format.set_align('center')
        date_format1 = workbook.add_format({'num_format': 'd/mm/YYYY','valign':   'vcenter'})
        default_format = workbook.add_format({'valign':   'vcenter','text_wrap': True })
        default_format.set_align('center')

        # Adjust the column width.
        # worksheet.set_column(1, 1, 15)
        worksheet.set_column(1, 8, 26)

        columns = ['#','Type Utilisateur', 'Date de Création']

        merge_format = workbook.add_format({
        'bold':     True,
        'border':   1,
        'align':    'center',
        'valign':   'vcenter',
        'text_wrap': True
        })
        # worksheet.set_column('H:M', 15)
        # worksheet.set_row(1, 30)
        for col_num in range(len(columns)):
            if col_num <= 5:
                worksheet.merge_range(0,col_num,1,col_num, columns[col_num], merge_format)
        
        # Start from the first cell below the headers.
        row = 1
        col = 0
        row_num = 1

        for row in range(len(type_utilisateurs)):
            row_num += 1
            worksheet.set_row_pixels(row_num, 50)
            worksheet.write_number(row_num, col, row_num-1,default_format)
            worksheet.write_string(row_num,col + 1, type_utilisateurs[row].name,default_format)
            worksheet.write_datetime(row_num,col + 2, type_utilisateurs[row].created_at, date_format)
        
        workbook.close()
        output.seek(0)
        filename = 'Liste des types utilisateurs.xlsx'
        response = HttpResponse(output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

    # types pour faire les select
    types = []
    for t in type_utilisateurs:
       types.append({"id": t.id, "name": t.name})
    
    return render(request, 'user/liste_type_users.html', 
        {'form': form, 
        'form_perm': form_perm, 
        'type_utilisateurs': type_utilisateurs,
        'json_types': json.dumps(types),
        'permissions': allPermissions, 
        'active_ass_users': True, 
        'prints':prints})


# @authorizations('Super administrateur','Administrateur')
def add_type_user(request):
    form = TypeUtilisateurForm(request.POST or None)
    form_perm = PermissionForm(request.POST or None)
    prints = request.GET.get('prints')
    action_log(request,"Utilisateurs - Types Utilisateurs ", "Affichage de la liste des types utilisateurs ")
    try:
        if request.user.isAdminInstance or request.user.is_superuser:
            #permissions = Permission.objects.all()
            type_utilisateurs = Type_Utilisateur.objects.filter(instance = request.user.instance).all()
        else:
            type_utilisateurs = Type_Utilisateur.objects.filter(instance__isnull=True).all()
            

    except expression as identifier:
        pass
    
    if request.method == "POST":
        
        if form.is_valid():
            permissions = []
            for p in allPermissions:
                permissions = permissions + request.POST.getlist("permissions_"+p['group'])
            
            name = form.cleaned_data['name']
            home = form.cleaned_data['home']
            exist = False
            for type_user in type_utilisateurs:
                if type_user.name == name:
                    exist = True
                    break
            if exist:
                messages.error(request, 'Cet type utilisateur existe, donnez un autre type')
                return redirect('user:add_type_user')
            else:
                type_utilisateur = Type_Utilisateur()
                type_utilisateur.name = name
                type_utilisateur.home = home
                # PERMISSIONS
                type_utilisateur.permissions = permissions
                if request.user.isAdminInstance:
                    type_utilisateur.instance = request.user.instance
                type_utilisateur.save()
                action_log(request,"Utilisateurs - Type Utilisateurs ", "Ajout d'un Type Utilisateur ")
                messages.success(request, ('Type utilisateur ajoute avec success'))
                return redirect('user:type_utilisateur')

    # types pour faire les select
    types = []
    for t in type_utilisateurs:
       types.append({"id": t.id, "name": t.name})
    
    return render(request, 'user/add_type_user.html', 
        {'form': form, 
        'form_perm': form_perm, 
        'type_utilisateurs': type_utilisateurs,
        'json_types': json.dumps(types),
        'permissions': allPermissions, 
        'active_ass_users': True, 
        'prints':prints,
        'pages': PAGES
        })

# @authorizations('Super administrateur','Administrateur')
def update_type_user(request,pk):
    form = TypeUtilisateurForm(request.POST or None)
    form_perm = PermissionForm(request.POST or None)
    prints = request.GET.get('prints')
    is_view = request.GET.get('view', None)
    type_utilisateur = get_object_or_404(Type_Utilisateur, id=pk)

    form = TypeUtilisateurForm(request.POST)
    action_log(request,"Utilisateurs - Types Utilisateurs ", "Affichage de la liste des types utilisateurs ")
    try:
        if request.user.isAdminInstance:
            #permissions = Permission.objects.all()
            type_utilisateurs = Type_Utilisateur.objects.filter(instance = request.user.instance).all()
        else:
            type_utilisateurs = Type_Utilisateur.objects.filter(instance__isnull=True).all()
            

    except expression as identifier:
        pass
    
    if request.method == "POST":
        
        if form.is_valid():
            permissions = []
            for p in allPermissions:
                permissions = permissions + request.POST.getlist("permissions_"+p['group'])

            name = form.cleaned_data['name']
            home = form.cleaned_data['home']
            type_utilisateur.name = name
            type_utilisateur.home = home
            # PERMISSIONS
            type_utilisateur.permissions = permissions
            if request.user.isAdminInstance:
                type_utilisateur.instance = request.user.instance
            type_utilisateur.save()
            action_log(request,"Utilisateurs - Type Utilisateurs ", "Ajout d'un Type Utilisateur ")
            messages.success(request, ('Type utilisateur ajoute avec success'))
            return redirect('user:type_utilisateur')

    # types pour faire les select
    types = []
    for t in type_utilisateurs:
       types.append({"id": t.id, "name": t.name})
    
    return render(request, 'user/update_type_user.html', 
        {'form': form, 
        'form_perm': form_perm, 
        'type_utilisateurs': type_utilisateur,
        'json_types': json.dumps(types),
        'permissions': allPermissions, 
        'active_ass_users': True, 
        'is_view': is_view, 
        'prints':prints,
        'pages': PAGES
        })


# @authorizations('Super administrateur','Administrateur')
def delete_type_user(request, delete_id):
    type_utilisateur = Type_Utilisateur.objects.get(id=delete_id)
    utilisateurs = Utilisateur.objects.all()

    for utilisateur in utilisateurs:
        if utilisateur.type_utilisateur == type_utilisateur:
            utilisateur.type_utilisateur = Type_Utilisateur.objects.get(name="Simple Utilisateur")
            utilisateur.save()

    type_utilisateur.delete()
    action_log(request,"Utilisateurs - Type Utilisateurs ", "Suppression d'un Type Utilisateur ")
    messages.success(request, ('Type utilisateur supprime avec success'))
    return redirect('user:type_utilisateur')
   
# # @authorizations('Super administrateur','Administrateur')
# def update_type_user(request, type_utilisateur_id):
#     type_utilisateur = get_object_or_404(Type_Utilisateur, id=type_utilisateur_id)
#     if request.user.isAdminInstance:
#         type_utilisateurs = Type_Utilisateur.objects.filter(instance=request.user.instance).all()
#     else:
#         type_utilisateurs = Type_Utilisateur.objects.filter(instance__isnull=True).all()
#     form = TypeUtilisateurForm(request.POST)

#     if request.method == 'POST':
#         if form.is_valid():
#             type_utilisateur.name = form.cleaned_data['name']
#             type_utilisateur.permissions = request.POST.getlist("permissions_" + str(type_utilisateur.id))
#             type_utilisateur.save()

#             action_log(request,"Utilisateurs - Type Utilisateurs ", "Mise à jour d'un Type Utilisateur ")

#             messages.success(request, 'Cet type utilisateur a ete modifie avec success')
#             return redirect('user:type_utilisateur')

# @authorizations('Super administrateur','Administrateur')
def details_type_user(request, type_utilisateur_id):
    action_log(request,"Utilisateurs - Type Utilisateurs ", "Affichage de la page Détails d'un Type Utilisateur ")


    type_utilisateur = Type_Utilisateur.objects.get(id=type_utilisateur_id)
    return render(request, 'user/details_type_user.html', {'type_utilisateur': type_utilisateur})

# @authorizations('Super administrateur','Administrateur')
@login_required
def request_register(request):
    form = RequestUtilisateurForm(request.user)

    services = Services.objects.filter(instance=request.user.instance).all().order_by('name')

    if request.method == 'POST':
        form = RequestUtilisateurForm(request=request.POST or None, user=request.user)
        if form.is_valid() == False:
            utilisateur = Utilisateur()
            second_email = request.POST['second_email'].lower()
            utilisateur.second_email = second_email
            utilisateur.email = request.POST['email'].lower()
            
            if request.POST.get('type_utilisateur',None) == 'autre':
                type_utilisateur = Type_Utilisateur.objects.create(name=request.POST.get('other_type_utilisateur',None),instance=request.user.instance)
                utilisateur.type_utilisateur = type_utilisateur
            else:
                utilisateur.type_utilisateur_id = request.POST['type_utilisateur']
            
            if request.POST.get('fonctions',None) == 'autre':
                fonction = Fonction.objects.create(name=request.POST.get('other_fonction',None),instance=request.user.instance)
                utilisateur.fonction = fonction
            else:
                utilisateur.fonction_id = request.POST['fonctions']
            
            if request.user.isAdminInstance or request.user.is_superuser:
                utilisateur.instance = request.user.instance
                
            is_chef = request.POST.get('is_chef')
            is_adjoint = request.POST.get('is_adjoint')

            if is_chef == 'on':
                utilisateur.is_adjoint = False
                utilisateur.is_chef = True
            
            elif is_adjoint == 'on':
                utilisateur.is_chef = False
                utilisateur.is_adjoint = True

            if request.POST.get('service',None) == 'autre':
                serv = Services.objects.create(name=request.POST.get('other_service',None),instance=request.user.instance)
            else:
                serv = Services.objects.get(id=request.POST.get('service',None))
            utilisateur.service = serv
            
            utilisateur.chief = None
            utilisateur.set_password('1234')

            utilisateur.is_active = False

            if request.POST['type_utilisateur'] == SUPER_ADMINISTRATEUR:
                utilisateur.is_admin = True

            utilisateur.save()

            ###################

            current_site = get_current_site(request)
            message = render_to_string('mails/user/acc_active_email.html', {
                'user': utilisateur,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(utilisateur.pk)),
                'token': account_activation_token.make_token(utilisateur),
            })
            email = SentMail()
            email.title = 'GEC: Activation et Enregistrement de votre compte'
            email.email = request.POST['email']
            email.message = message
            email.save()

            ###################

            action_log(request,"Création d'un compte  ", "Création d'un Utilisateur " +'<b>'+ str(utilisateur)+'</b>')


            # if can_create:
            messages.success(request, 'Creation d un nouveau utilisateur effectuee avec succes')
            return redirect('user:utilisateurs')
        else:
            messages.error(request, 'Impossible de creer cet utilisateur parce qu un utilisateur existe deja avec les meme informations')
            return render(request, 'user/request_utilisateur.html', {'form': form, 'services': services, 'active_ass_users': True})

    return render(request, 'user/request_utilisateur.html', {'form': form, 'services': services, 'active_ass_users': True})

# @authorizations('Super administrateur','Administrateur')
def resend_request_register(request, user_id):
    utilisateur = get_object_or_404(Utilisateur, pk=user_id)
    utilisateur.is_active = False

    ###################

    current_site = get_current_site(request)
    message = render_to_string('mails/acc_reactive_email.html', {
        'user': utilisateur,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(utilisateur.pk)),
        'token': account_activation_token.make_token(utilisateur),
    })
    email = SentMail()
    email.title = 'GEC: Reactivation et Enregistrement de votre compte'
    email.email = utilisateur.email
    email.message = message
    email.save()

    ###################
    action_log(request,"Réactivation d'un compte  ", "Réactivation d'un compte Utilisateur ")


    return redirect('user:utilisateurs')

# @authorizations('Super administrateur','Administrateur')
def statut_utilisateur(request, user_id):
    user = Utilisateur.objects.get(id=user_id)

    if user.is_active:
        user.is_active = False
        user.save()
        statut = 'Désactivé'

        ################### Send email
        message = render_to_string('mails/statut_utilisateur.html', {
            'user': user,
            'statut': statut,
        })
        email = SentMail()
        email.title = 'GEC: Activation / Desactivation de votre compte'
        email.email = user.email
        email.message = message
        email.save()
        ###################
    else:
        user.is_active = True
        user.save()
        statut = 'Activé'

        ################### Send email
        message = render_to_string('mails/statut_utilisateur.html', {
            'user': user,
            'statut': statut,
        })
        email = SentMail()
        email.title = 'GEC: Activation / Desactivation de votre compte'
        email.email = user.email
        email.message = message
        email.save()
        ###################
    action_log(request,"Activation/Réactivation ", "Activation / Réactivation d'un compte Utilisateur ")
    return redirect('user:utilisateurs')

# @authorizations('Super administrateur')
def users_action_tracking(request):
    page = request.GET.get('page')
    prints = request.GET.get('prints')
    date_debut = request.GET.get('dateStart')
    date_fin = request.GET.get('dateEnd')
    search = request.GET.get('q')
    search_filter = request.GET.get('search_filter')
    action_log(request,"Mon compte - Historiques","Acces a la page  Historique des actions utilisateurs")
    if request.user.is_admin:
        only_superuser = Track_Actions.objects.all().order_by('-date_action', '-heure')
    elif request.user.isAdminInstance:
        only_superuser = Track_Actions.objects.filter(instance=request.user.instance).order_by('-date_action', '-heure')
    else:
        only_superuser = Track_Actions.objects.filter(user=request.user, instance=request.user.instance).order_by('-date_action', '-heure')

    if request.GET:
        if date_debut and date_fin:
            date_debut = request.GET.get('dateStart')
            date_fin = request.GET.get('dateEnd')
            date_format = "%d/%m/%Y"
            start_date_string = None
            end_date_string   = None
            str_month1 = '0'
            str_day1   = '0'
            str_month2 = '0'
            str_day2   = '0'
            if  date_debut != '' and  date_fin != '':
                start = datetime.datetime.strptime(date_debut, date_format)
                if start.month < 10 :
                    str_month1 += str(start.month) 
                else:
                    str_month1 = str(start.month)
                if start.day < 10:
                    str_day1 += str(start.day)
                else:
                    str_day1 = str(start.day)
                end  = datetime.datetime.strptime(date_fin, date_format)
                if end.month < 10:
                    str_month2 += str(end.month)
                else:
                    str_month2 = str(end.month)
                if end.day < 10:
                    str_day2 += str(end.day)
                else:
                    str_day2 = str(end.day)    
                start_date_string = str(start.year)  + "-" + str(str_month1) + "-" + str(str_day1) 
                end_date_string = str(end.year)  + "-" + str(str_month2) + "-" + str(str_day2)
                
                if request.user.is_admin:
                    only_superuser = Track_Actions.objects.filter(date_action__range= [start_date_string, end_date_string]).order_by('-date_action', '-heure')
                else:
                    only_superuser = Track_Actions.objects.filter(user = request.user, date_action__range= [start_date_string, end_date_string]).order_by('-date_action', '-heure')    
    
    if((search)):
        if search_filter == 'all':
            only_superuser = only_superuser.filter(Q(page__icontains = search) | Q(action_effectue__icontains = search)).all()
        elif int(search_filter) == 1:
            only_superuser = only_superuser.filter(page__icontains = search).all()
        elif int(search_filter) == 2:
            only_superuser = only_superuser.filter(action_effectue__icontains = search).all()
    # if prints is None:
    weekEnd = datetime.datetime.now()
    paginator = Paginator(only_superuser, 25) # Show 25 contacts per page
    try:
        only_superuser = paginator.page(page)
    except PageNotAnInteger:
        only_superuser = paginator.page(1)
    except EmptyPage:
        only_superuser = paginator.page(paginator.num_pages)
    if (date_debut) is None:
        date_debut = ''
    if (date_fin) is None:
        date_fin = ''
    if (search_filter) is None:
        search_filter = ''

    if prints is None:
        return render(request, 'user/action_tracking.html', {
            'only_superuser':only_superuser,
            'user':request.user,
            'weekStart': weekEnd - datetime.timedelta(days=6),
            'weekEnd': weekEnd,
            'date_debut':date_debut,
            'date_fin':date_fin,
            'page': page,
            'search':search,
            'search_filter': search_filter
        })
    else:
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output,{'remove_timezone': True})
        worksheet = workbook.add_worksheet()
        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': 1,'valign':   'vcenter'})
        bold.set_align("center")
        # Add a number format for cells with money.
        money_format = workbook.add_format({'num_format': '$#,##0'})
        # Add an Excel date format.
        date_format = workbook.add_format({'num_format': 'd/mm/YYYY','valign':   'vcenter'})
        date_format.set_align('center')
        date_format1 = workbook.add_format({'num_format': 'd/mm/YYYY','valign':   'vcenter'})
        default_format = workbook.add_format({'valign':   'vcenter', 'text_wrap': True})
        default_format.set_align('center')
        # Adjust the column width.
        # worksheet.set_column(1, 1, 15)
        worksheet.set_column(1, 6, 40)
        # worksheet.set_row(1, 40)
        columns = ['#','Page Visitée ', 'Actions ','Date de visite', 'Prénoms','Nom']
        merge_format = workbook.add_format({
        'bold':     True,
        'border':   1,
        'align':    'center',
        'valign':   'vcenter',
        'text_wrap': True
        })
        # worksheet.set_column('H:M', 15)
        # worksheet.set_row(1, 30)
        for col_num in range(len(columns)):
            if col_num <= 6:
                worksheet.merge_range(0,col_num,1,col_num, columns[col_num], merge_format)
        
        # Start from the first cell below the headers.
        row = 1
        col = 0
        row_num = 1
        for row in range(len(only_superuser)):
            row_num += 1 
            worksheet.set_row_pixels(row_num, 50)
            worksheet.write_number(row_num, col, row_num-1,default_format)
            worksheet.write_string(row_num,col + 1, only_superuser[row].page,default_format)
            worksheet.write_string(row_num,col + 2, only_superuser[row].action_effectue,default_format)
            worksheet.write_datetime(row_num,col + 3, only_superuser[row].date_action,date_format)
            worksheet.write_string(row_num,col + 4, only_superuser[row].user.first_name,default_format)
            worksheet.write_string(row_num,col + 5, only_superuser[row].user.last_name,default_format)
            # worksheet.write_datetime(row_num,col + 3, services[row].created_at, date_format) 
        workbook.close()
        output.seek(0)
        filename = 'Liste des actions des utilisateurs.xlsx'
        response = HttpResponse(output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
    
# @authorizations('Super administrateur','Administrateur')
def users_timing_action(request):
    datestart = None
    dateEnd = None
    only_superuser = []
    if request.GET:
        datestartArr = request.GET.get('dateStart').split('/')
        dateEndArr = request.GET.get('dateEnd').split('/')
        if len(datestartArr) > 0 and len(dateEndArr) > 0:    
            datestart = datetime.datetime(int(datestartArr[2]),int(datestartArr[1]),int(datestartArr[0]))
            dateEnd = datetime.datetime(int(dateEndArr[2]),int(dateEndArr[1]),int(dateEndArr[0]))
            if request.user.instance:
                only_superuser = Track_Actions.objects.distinct('user').filter(date_action__range=[datestart,dateEnd],user__instance=request.user.instance)
            else:
                only_superuser = Track_Actions.objects.distinct('user').filter(date_action__range=[datestart,dateEnd])
    else:
        action_by_month = Track_Actions.objects.annotate(month=TruncMonth('date_action')).values('month','user').order_by('-month').annotate(nbr=Count('id'))
        for action in action_by_month:
            if request.user.instance:
                user_action = Track_Actions.objects.filter(date_action__year=action['month'].year, date_action__month=action['month'].month, user_id=action['user']).first()
            else:
                user_action = Track_Actions.objects.filter(date_action__year=action['month'].year, date_action__month=action['month'].month, user_id=action['user']).first()
            
            if request.user.instance :
                if user_action.user.instance == request.user.instance:
                    only_superuser.append(user_action)
            else:
                only_superuser.append(user_action)
        
        # only_superuser = Track_Actions.objects.distinct('user')
    
        
    action_log(request,"Utilisateur - Temps d'utilisation","Acces aux temps d'utilisations dans l'application")
    return render(request, 'user/action_timing.html', {'only_superuser':only_superuser,'datestart':datestart,'dateEnd':dateEnd})

# @authorizations('Super administrateur','Administrateur')
def details_users_timing_action(request, utilisateur_id):
    detail = Track_Actions.objects.filter(user__id=utilisateur_id).first()
    details_users_timing = Utilisateur.objects.get(pk=utilisateur_id)
    users_actions = Track_Actions.objects.filter(user_id=utilisateur_id, action_effectue="Connexion ",date_action__year=detail.date_action.year, date_action__month=detail.date_action.month).order_by('-date_action')
    return render(request, 'user/details_users_timing_action.html', {'details_users_timing': details_users_timing, 'only_superuser': users_actions})

def activate(request, uidb64, token):
    #if request.user.isAdminInstance:
    #    services = Services.objects.filter(instance=request.user.instance).all()
    #    fonctions = Fonction.objects.filter(instance=request.user.instance).all()
    #else:
    #    services = Services.objects.filter(instance__isnull=True).all()
    #    fonctions = Fonction.objects.filter(instance__isnull=True).all()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Utilisateur.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Utilisateur.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):

        form = UtilisateurForm2(user=request.user)
        #user.is_active = True
        #user.save()
        #login(request, user)
        user.is_active = False
        user.last_login = None
        user.save()
        user_type = Type_Utilisateur.objects.get(id=user.type_utilisateur_id)

        messages.success(request, 'Veuillez vous enregistrez')
       
        return render(request, 'user/utilisateur_himself.html', {'form': form, 
        'user': user, 
        #'services': services, 
        #'fonctions': fonctions, 
        'user_email': user.email, 'user_type': user_type})
    else:
        return HttpResponse('Activation link is invalid!')

def get_client_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        elif request.META.get('HTTP_X_REAL_IP'):
            ip = request.META.get('HTTP_X_REAL_IP')
        else:
            ip = request.META.get('REMOTE_ADDR')
    except:
        ip = ""
    return ip


############# Stand by ################
# @authorizations('Super administrateur','Administrateur')
def register(request):
    form = PasswordCheck()

    if request.method == 'POST':
        form = UtilisateurForm(request.POST, user=request.user.instance)

        if form.is_valid():
            utilisateur = Utilisateur()

            utilisateur.matricule = form.cleaned_data['matricule']
            utilisateur.first_name = form.cleaned_data['first_name']
            utilisateur.last_name = form.cleaned_data['last_name']
            utilisateur.email = form.cleaned_data['email']
            utilisateur.genre = form.cleaned_data['genre']
            utilisateur.fonction = form.cleaned_data['fonction']
            utilisateur.phone = form.cleaned_data['phone']
            utilisateur.type_utilisateur = form.cleaned_data['type_utilisateur']
            utilisateur.address = form.cleaned_data['address']

            utilisateur.set_password('1234')
            if request.user.isAdminInstance:
                utilisateur.instance = request.user.instance
            #utilisateur.is_active = False

            utilisateur.save()

            ###################

            current_site = get_current_site(request)
            message = render_to_string('mails/acc_active_email.html', {
                'user': utilisateur,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(utilisateur.pk)),
                'token': account_activation_token.make_token(utilisateur),
            })
            email = SentMail()
            email.title = 'GEC: Activation de votre compte'
            email.email = form.cleaned_data['email']
            email.message = message
            email.save()

            ###################

            #assign_role(utilisateur, 'normal')
            action_log(request,"Enregistrement d'un utilisateur ", "Enregistrement d'un nouveau Utilisateur " +'<b>'+ str(utilisateur)+'</b>')


            messages.success(request, 'Vous avez bien ajouté un utilistateur')
            messages.success(
                request, 'Un email d activation a ete envoye a l utilisteur cree')
            return redirect('user:utilisateurs')


    return render(request, 'user/utilisateur.html', {'form': form})

# @authorizations('Super administrateur','Administrateur')
def list_requestutilisateur(request):
    requests = Utilisateur.objects.filter(first_name='')

    action_log(request,"Utilisateurs - Utilisateurs ", "Affichage liste des demandes d'enregistrement d un utilisateur ")


    return render(request, 'user/list_request_utilisateurs.html', {'requests': requests})

# @authorizations('Super administrateur','Administrateur')
def add_service(request):
    action_log(request,"Utilisateurs - Services ", "Affichage de la liste des services ")
    prints = request.GET.get('prints')
    if request.user.isAdminInstance:
        services = Services.objects.filter(instance = request.user.instance).all()
    else:
        services = Services.objects.filter(instance__isnull=True).all()
    form = ServiceForm()

    if request.method == "POST":
            
        name = request.POST.get('name', None)
        service_tutelle = request.POST.get('service_tutelle', None)
        hidden_service_tutelle  = request.POST.get('hidden_service_tutelle', None)

        if name:
            service = Services()
            service.name = name
            if request.user.isAdminInstance:
                service.instance = request.user.instance
            succes_message = 'Le service '+ name +' a été crée avec succès '
            
            if hidden_service_tutelle:
                s_tutelle  =  Services.objects.filter(id=hidden_service_tutelle)
                if s_tutelle:
                    service.service_tutelle = s_tutelle.first().id
                    succes_message = succes_message + ' sous ' + s_tutelle.first().name
            
            service.save()
            action_log(request,"Utilisateurs - Services ", "Ajout d' un nouveau service ")


            messages.success(request, succes_message)

            return redirect('user:service')
    if prints:
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output,{'remove_timezone': True})
        worksheet = workbook.add_worksheet()

        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': 1,'valign':   'vcenter'})
        bold.set_align("center")

        # Add a number format for cells with money.
        money_format = workbook.add_format({'num_format': '$#,##0'})

        # Add an Excel date format.
        date_format = workbook.add_format({'num_format': 'd/mm/YYYY','valign':   'vcenter'})
        date_format.set_align('center')
        date_format1 = workbook.add_format({'num_format': 'd/mm/YYYY','valign':   'vcenter'})
        default_format = workbook.add_format({'valign':   'vcenter', 'text_wrap': True})
        default_format.set_align('center')

        # Adjust the column width.
        # worksheet.set_column(1, 1, 15)
        worksheet.set_column(1, 5, 40)

        columns = ['#','Service ', 'Service Tutel','Nombre de sous service',"Nombre d'Utilisateur" ,'Date de Création']

        merge_format = workbook.add_format({
        'bold':     True,
        'border':   1,
        'align':    'center',
        'valign':   'vcenter',
        'text_wrap': True
        })
        # worksheet.set_column('H:M', 15)
        # worksheet.set_row(1, 30)
        for col_num in range(len(columns)):
            if col_num <= 5:
                worksheet.merge_range(0,col_num,1,col_num, columns[col_num], merge_format)
        
        # Start from the first cell below the headers.
        row = 1
        col = 0
        row_num = 1

        for row in range(len(services)):
            row_num += 1
            worksheet.set_row_pixels(row_num, 50)
            worksheet.write_number(row_num, col, row_num-1,default_format)
            worksheet.write_string(row_num,col + 1, services[row].name,default_format)
            if services[row].service_tutelle != None:
                worksheet.write_string(row_num,col + 2, services[row].service_tutelle,default_format)
            else:
                worksheet.write_string(row_num,col + 2, " ",default_format)

            worksheet.write_string(row_num,col + 3, str(services[row].get_subservices_for_excel().count()),default_format)
            worksheet.write_string(row_num,col + 4, str(services[row].get_utilisateurs_for_excel().count()),default_format)
            worksheet.write_datetime(row_num,col + 5, services[row].created_at, date_format) 
        
        workbook.close()
        output.seek(0)
        filename = 'Liste des services.xlsx'
        response = HttpResponse(output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
        

    return render(request, 'user/liste_services.html', {'form': form, 'services': services, 'active_ass_users': True,'prints':prints})

# @authorizations('Super administrateur','Administrateur')
def delete_service(request, service_id):
    try:
        service = Services.objects.get(id=service_id)
        
        sous_services = Services.objects.filter(service_tutelle=service.id)
        
        for sous_service in sous_services:
            sous_service.delete()
        
        service.delete()

        action_log(request,"Utilisateurs - Services ", "Suppression d' un service ")
        

        messages.success(request, 'Service supprimé avec succès')

        return redirect('user:service')
    except expression as identifier:
        pass

# @authorizations('Super administrateur','Administrateur')
def update_service(request, service_id):
    try:
        service = Services.objects.get(id=service_id)
        form = ServiceForm(request.POST)
        
        if request.method == 'POST':
            
            name = request.POST.get('name', None)
            service_tutelle = request.POST.get('service_tutelle', None)
            hidden_service_tutelle  = request.POST.get('hidden_service_tutelle', None)
            
            succes_message = 'Le service '+ name +' a été modifié avec succès '
            
            if name:
                # name = form.cleaned_data['name']
                service.name = name

                if hidden_service_tutelle:
                    s_tutelle  =  Services.objects.filter(id=hidden_service_tutelle)
                    if s_tutelle:
                        service.service_tutelle = s_tutelle.first().id
                        succes_message = succes_message + ' sous ' + s_tutelle.first().name
                
                service.save()

                action_log(request,"Utilisateurs - Services ", "Mise à jour d' un service ")
                
                
                messages.success(request, succes_message)
                return redirect('user:service')
        
        return redirect('user:service')
    
    except expression as identifier:
        pass

# update user password
def update_password(request,user_id):
    # form = PasswordCheck(request.POST)
    password1 = request.POST.get('password', None)
    password2 = request.POST.get('confirmation', None)
    utilisateur = Utilisateur.objects.get(pk=user_id)
    last_password = utilisateur.password
    new_password = request.POST.get('password')
    action_log(request,"Mon compte - changer mon mot de passe ", "Mise à jour du mot de passe d' un utilisateur ")

    
    if password1 != password2:
        messages.error(request, ('Les deux mots de passe ne correspondent pas!'))
    else:
        if request.method == 'POST':
            last_password = utilisateur.password
            utilisateur.set_password(new_password)
            utilisateur.save()
            if utilisateur:
                messages.success(request, ('Le mot de passe a ete mis a jour! avec success!'))
                return redirect('user:utilisateurs')
            else:
                messages.error(request, ('Corrigez les erreurs ci-dessus!'))
    return render(request, 'user/update_password.html')


def full_name(request, id_user):
    try:
        user = Utilisateur.objects.get(pk=id_user)
        full_name = {
            'id': user.id,
            'full_name': user.get_full_name(),
            'instance_name': user.get_instance_name(),
        }
        return HttpResponse(simplejson.dumps(full_name), content_type="application/json")
    except:
        return HttpResponse(simplejson.dumps(None), content_type="application/json")

def export_liste_actions_logs_xls(request):

    action_log(request,"Historique Des actions ", "Export de l'historique des actions")
    if request.user.is_admin:
        only_superuser = Track_Actions.objects.all().order_by('-date_action', '-heure')
    else:
        only_superuser = Track_Actions.objects.filter(instance_id = request.user.instance.id).order_by('-date_action', '-heure')
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output,{'remove_timezone': True})
    worksheet = workbook.add_worksheet()
    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': 1,'valign':   'vcenter'})
    bold.set_align("center")
    # Add a number format for cells with money.
    money_format = workbook.add_format({'num_format': '$#,##0'})
    # Add an Excel date format.
    date_format = workbook.add_format({'num_format': 'd/mm/YYYY','valign':   'vcenter'})
    heure_format = workbook.add_format({'num_format': 'HH:mm:ss','valign':   'vcenter'})
    date_format.set_align('center')
    date_format1 = workbook.add_format({'num_format': 'd/mm/YYYY','valign':   'vcenter'})
    default_format = workbook.add_format({'valign':   'vcenter', 'text_wrap': True})
    default_format.set_align('center')
    # Adjust the column width.
    # worksheet.set_column(1, 1, 15)
    worksheet.set_column(1, 6, 40)
    # worksheet.set_row(1, 40)
    columns = ['#','Page Visitée ', 'Actions ','Date de visite', 'Temps','Prénoms','Nom','Navigateur']
    merge_format = workbook.add_format({
    'bold':     True,
    'border':   1,
    'align':    'center',
    'valign':   'vcenter',
    'text_wrap': True
    })
    # worksheet.set_column('H:M', 15)
    # worksheet.set_row(1, 30)
    for col_num in range(len(columns)):
        if col_num <= 8:
            worksheet.merge_range(0,col_num,1,col_num, columns[col_num], merge_format)
    
    # Start from the first cell below the headers.
    row = 1
    col = 0
    row_num = 1
    

    for row in range(len(only_superuser)):
        row_num += 1 
        worksheet.set_row_pixels(row_num, 50)
        worksheet.write_number(row_num, col, row_num-1,default_format)
        worksheet.write_string(row_num,col + 1, only_superuser[row].page,default_format)
        worksheet.write_string(row_num,col + 2, only_superuser[row].action_effectue,default_format)
        worksheet.write_datetime(row_num,col + 3, only_superuser[row].date_action,date_format)
        worksheet.write_datetime(row_num,col + 4, only_superuser[row].heure,heure_format)
        worksheet.write_string(row_num,col + 5, only_superuser[row].user.first_name,default_format)
        worksheet.write_string(row_num,col + 6, only_superuser[row].user.last_name,default_format)
        worksheet.write_string(row_num,col + 7, only_superuser[row].navigateur,default_format)
        # worksheet.write_datetime(row_num,col + 3, services[row].created_at, date_format) 
    workbook.close()
    output.seek(0)
    filename = 'Liste des actions des utilisateurs.xlsx'
    response = HttpResponse(output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

# @authorizations('Super administrateur','Administrateur')
def export_liste_users_timing_xls(request):
    action_log(request,"Temps d''utilisation", "Export de la liste temps d'utilisation")
    only_superuser = Track_Actions.objects.distinct('user')
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output,{'remove_timezone': True})
    worksheet = workbook.add_worksheet()
    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': 1,'valign':   'vcenter'})
    bold.set_align("center")
    # Add a number format for cells with money.
    money_format = workbook.add_format({'num_format': '$#,##0'})
    # Add an Excel date format.
    date_format = workbook.add_format({'num_format': 'd/mm/YYYY HH:mm:ss','valign':   'vcenter'})
    date_format.set_align('center')
    date_format1 = workbook.add_format({'num_format': 'd/mm/YYYY','valign':   'vcenter'})
    default_format = workbook.add_format({'valign':   'vcenter', 'text_wrap': True})
    default_format.set_align('center')
    # Adjust the column width.
    # worksheet.set_column(1, 1, 15)
    worksheet.set_column(1, 6, 40)
    # worksheet.set_row(1, 40)
    columns = ['#','Prénoms ', 'Noms ','Date de Connexion','Temps total']
    merge_format = workbook.add_format({
    'bold':     True,
    'border':   1,
    'align':    'center',
    'valign':   'vcenter',
    'text_wrap': True
    })
    # worksheet.set_column('H:M', 15)
    # worksheet.set_row(1, 30)
    for col_num in range(len(columns)):
        if col_num <= 5:
            worksheet.merge_range(0,col_num,1,col_num, columns[col_num], merge_format)
    
    # Start from the first cell below the headers.
    row = 1
    col = 0
    row_num = 1

    for track in only_superuser:
        row_num += 1 
        worksheet.set_row_pixels(row_num, 50)
        worksheet.write_number(row_num, col, row_num-1,default_format)
        worksheet.write_string(row_num,col + 1, track.user.first_name,default_format)
        worksheet.write_string(row_num,col + 2, track.user.last_name,default_format)
        worksheet.write_datetime(row_num,col + 3, track.date_action,date_format1)
        worksheet.write_string(row_num,col + 4, track.user_time,default_format)

    workbook.close()
    output.seek(0)
    filename = "Liste des temps d'utilisation des utilisateurs.xlsx"
    response = HttpResponse(output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

# @authorizations('Super administrateur','Administrateur')
@login_required
def company_info(request):
    
    form = CompanyForm(request.POST or None)
    action_log(request,"Utilisateurs - Company ", "Affichage des infos de la structure ")
    
    fonctions = Fonction.objects.all()
    company = Company.objects.first()
    company_fonctions = CompanyFonction.objects.filter(company=company).all()
    fonction_arr = []
    for ft in fonctions:
        fonction_arr.append({
            "fonction": ft,
            "option": get_order(ft,company_fonctions)
        })
    fonction_index = [idx + 1 for idx in range(len(fonctions))]
    if company_fonctions:
        fonction_ids = [int(fct.fonction_id) for fct in company_fonctions]
        fonction_orders = [int(fct.order) if fct.order else None for fct in company_fonctions]
        fonction_genres = [fct.genre for fct in company_fonctions]
    else:
        fonction_ids = []
        fonction_orders = [] 
        fonction_genres = []
    
   
    return render(request, 'user/company.html', {
        'form': form,
        'company': company, 
        'active_ass_users': True,
        'fonctions':fonction_arr,
        'fonction_ids':fonction_ids,
        'fonction_orders':fonction_orders,
        'fonction_genres':fonction_genres,
        "fonction_index":fonction_index
        })


# @authorizations('Super administrateur','Administrateur')
@login_required
def update_company_info(request, company_id):
    try:
        company = Company.objects.get(id=company_id)
        form = CompanyForm(request.POST)
        if request.method == 'POST':
            if form.is_valid():
                upload = request.FILES.get('logo',None)
                if upload:
                    fss = FileSystemStorage('gec/static/images')
                    file = fss.save(upload.name, upload)
                    fss.url(file)
                    company.logo = upload.name
                     
                name = form.cleaned_data['name']
                company.name = name
                company.sigle = form.cleaned_data['sigle']
                company.type = form.cleaned_data['type']
                company.category = form.cleaned_data['category']
                company.save()
                
                action_log(request,"Utilisateurs - Company ", "Mise a jour de structure ")
                return redirect('user:companies')
    except expression as identifier:
        pass


# @authorizations('Super administrateur','Administrateur')
@login_required
def company_add_annotation(request,company_id):
    company = Company.objects.get(id=company_id)
    fonctions_input = request.POST.getlist('fonctions');
    if request.method == 'POST':
        input_index = [index for index in request.POST.getlist('order') if index != 0]
        input_genre = [genre for genre in request.POST.getlist('genre') if genre != '']
        input_messages = [message for message in request.POST.getlist('message_annotation') if message != '']
       
        if len(fonctions_input) > 0:
            if len(input_index) == len(input_genre) and len(input_index) == len(input_messages):
                if CompanyFonction.objects.count() > 0:
                    CompanyFonction.objects.all().delete()
                for i in range(len(fonctions_input)):
                    company_fonction = CompanyFonction(
                        fonction_id = int(fonctions_input[i].split('-')[0]),
                        order = int(input_index[i]),
                        genre = input_genre[i],
                        message_annotation = input_messages[i],
                        company = company,
                        user_id = int(fonctions_input[i].split('-')[1])
                    )
                    company_fonction.save()
                else:
                    return redirect('user:companies') 
            else:
                messages.error(request, ('Une erreur s\'est produite lors du parametrage de la fiche annotattion'))
                return redirect('user:companies_configuration_assignation')
        else:
            action_log(request,"Utilisateurs - Company ", "Mise a jour de structure ")
            messages.error(request, ('Une erreur s\'est produite lors du parametrage de la fiche annotattion'))
            return redirect('user:companies')  
    messages.error(request, ('Une erreur s\'est produite lors du parametrage de la fiche annotattion'))
    return redirect('user:companies')

# @authorizations('Super administrateur','Administrateur')
@login_required
def compagny_configuration_assignation(request):
    form = CompanyForm(request.POST or None)
    action_log(request,"Utilisateurs - Company ", "Affichage des infos de la structure ")
    users = Utilisateur.objects.exclude(is_superuser=True)
    company = Company.objects.first()
    company_fonctions = CompanyFonction.objects.filter(company=company).all()
    fonction_arr = []
    for user in users:
        name =  '{} - {}'.format(user.fonction.name,user.service.name ) if user.fonction and user.service else ""
        user_id = user.id
        fonction_arr.append({
            "fonction": user.fonction if user.fonction else None,
            "fonction_name": name,
            "user_id": user_id,
            "option": get_order(user.fonction,company_fonctions) if user.fonction else False,
            "checking": checking_user_fonction(user.fonction.id,user.id) if user.fonction else False,
            "index": index_user_fonction(user.fonction.id,user.id) if user.fonction else 0,
            "genre": genre_user_fonction(user.fonction.id,user.id) if user.fonction else "",
            "message_annotation": message_annotation(user.fonction.id, user.id) if user.fonction else "",
        })
    fonction_index = [ idx + 1 for idx in range(len(users))]
    if company_fonctions:
        fonction_ids = [int(fct.fonction_id) for fct in company_fonctions]
        fonction_orders = [int(fct.order) if fct.order else 0 for fct in company_fonctions]
        fonction_genres = [fct.genre for fct in company_fonctions]
    else:
        fonction_ids = []
        fonction_orders = [] 
        fonction_genres = []
    # except expression as identifier:
    #     pass
    return render(request, 'user/configuration_assignation.html', {
        'form': form,
        'company': company, 
        'active_ass_users': True,
        'fonctions':fonction_arr,
        'fonction_ids':fonction_ids,
        'fonction_orders':fonction_orders,
        'fonction_genres':fonction_genres,
        "fonction_index":fonction_index
        })
    
def company_name(request):
    try:
        if request.user.is_authenticated:
            if request.user.instance:
                instance = Instance.objects.get(pk = request.user.instance.id)
                return HttpResponse(simplejson.dumps({
                    "name": instance.name,
                    "logo": f"{settings.MEDIA_URL}{instance.logo}"
                    }), content_type="application/json")
            else:
                return HttpResponse(simplejson.dumps({
                    "name": 'GEC GLOBAL',
                    "logo": '/static/images/Coat_of_arms_of_Guinea.png'
                    }), content_type="application/json")
        else:
            return HttpResponse(simplejson.dumps({
                "name": 'Gestion Electronique des Courriers',
                "logo": '/static/images/Coat_of_arms_of_Guinea.png'
            }), content_type="application/json")
    except:
        return HttpResponse(simplejson.dumps(None), content_type="application/json")

@login_required
def list_utilisateurSpc(request,user_id = None):
    admin_select = request.GET.get('admin',None)
    current_user = request.user
    if user_id:
        user = Utilisateur.objects.filter(pk=user_id).first()
        if user.chief:
            user.chief = None
        else:
            user.chief = request.user.id
        if admin_select:
            user.chief = int(admin_select)
        user.save()
        return redirect('user:list_utilisateur_spc')
    else:
        action_log(request,"Utilisateurs - Utilisateurs", "Affichage de la listes des utilisateurs")
        configAnnotation = [config.user.id for config in ConfigAnnotationInstance.objects.filter(instance=request.user.instance)]
        if(request.user.instance):
            if request.user.isAdminInstance and admin_select:
                chefService = Utilisateur.objects.get(id=admin_select)
                all_user = Utilisateur.objects.filter(instance = request.user.instance,isAdminInstance = False, service=chefService.service).exclude(pk__in=configAnnotation).all()
            else:
                all_user = Utilisateur.objects.filter(instance = request.user.instance,isAdminInstance = False, service=request.user.service).exclude(pk__in=configAnnotation).all()
        else:
            all_user = Utilisateur.objects.filter(instance__isnull=True).exclude(pk__in=configAnnotation).all()
        return render(request, 'user/list_utilisateur_scp.html',{'all_user':all_user,'admin_select':admin_select,'current_user':current_user})

def loadData(request):
    action_log(request,"Utilisateurs - Données ", "Chargement de données")
    
    # Si aucun fichier n'est chargé
    if request.FILES.get("dataLoaded") is None:
        messages.error(request, ('Veuillez choisir un fichier !'))
        return redirect('user:utilisateurs')

    errorWhenLoad = []
    print("Fichier")
    file = pd.read_excel(request.FILES.get("dataLoaded"))

    print("Excel File")

    col_prenoms = []
    #col_noms = []
    col_emails = []
    col_services = []
    col_service_tutelle = []
    col_fonctions = []
    col_typeUsers = []

    try:
        col_prenoms = list(file['prenom'])
        col_noms = list(file['nom'])
        col_emails = list(file['email'])
        col_services = list(file['service'])
        col_service_tutelle = list(file['service tutelle'])
        col_fonctions = list(file['fonction'])
        col_typeUsers = list(file['type'])
    except KeyError as err: # Si le nom d'une colonne n'est pas correcte
        print("++++++++++++++++++++Erreur de colonne:", err)
        messages.error(request, ('Veuillez respecter le nom de la colonne: ' + str(err) + ' conformement au template (y compris la casse)'))
        return redirect('user:utilisateurs')

    # Verification du fichier excel, s'il n' y a pas de cellules vides
    formatEmail = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    for i, email in enumerate(col_emails):
        erreur = ""
        if str(email) not in "nan" and str(col_prenoms[i]) not in "nan":
            
            if str(col_prenoms[i]) == "nan":
                print("Cellule Vide à la ligne : (" + str(i + 1) + "), colonne: (prenom)")
                erreur = {"line": str(i + 1) , "culumn": "prenom", "type": "vide"}
            elif str(col_noms[i]) == "nan":
                print("Cellule Vide à la ligne : (" + str(i + 1) + "), colonne: (nom)")
                erreur = {"line": str(i + 1) , "culumn": "nom", "type": "vide"}
            elif str(col_fonctions[i]) == "nan":
                print("Cellule Vide à la ligne : (" + str(i + 1) + "), colonne: (fonction)")
                erreur = {"line": str(i + 1) , "culumn": "fonction", "type": "vide"}
            elif str(col_services[i]) == "nan":
                print("Cellule Vide à la ligne : (" + str(i + 1) + "), colonne: (service)")
                erreur = {"line": str(i + 1) , "culumn": "service", "type": "vide"}
            elif str(email) == "nan":
                print("Cellule Vide à la ligne : (" + str(i + 1) +"), colonne: (email)")
                erreur = {"line": str(i + 1) , "culumn": "email", "type": "vide"}
            elif re.match(formatEmail, str(email)) is None:
                print("Email invalide à la ligne : (" + str(i + 1) +"), colonne: (email)")
                erreur = {"line": str(i + 1) , "culumn": "email", "type": "email invalide"}
            else:
                print(i+1)

        if len(erreur) > 0:
            errorWhenLoad.append(erreur)
    
    # S'il y a des erreur dans le fichier, renvoyez sans charger les données
    if len(errorWhenLoad) > 0:
        if(request.user.isAdminInstance):
            all_user = Utilisateur.objects.filter(instance = request.user.instance).all()
        else:
            adminInstance = Utilisateur.objects.filter(isAdminInstance = True) 
            superAdmin =  Utilisateur.objects.filter(is_superuser = True)
            all_user = list(chain( superAdmin, adminInstance))
        return render(request, 'user/list_utilisateurs.html', 
        {
            'all_user': all_user,
            'active_ass_users': True,
            'loadError': errorWhenLoad,
            'errorWhenLoad': json.dumps(errorWhenLoad)
            })

    # Ajout des service
    for i, service in enumerate(col_services):
        if str(col_services[i]) not in "nan":
            exist = Services.objects.filter(name=service, instance=request.user.instance).first()
            
            # Enregistre le service s'il n'existe pas
            if exist is None:
                newService = Services(name=service, instance=request.user.instance)
                # Si le service n'a pas de tutelle
                if str(col_service_tutelle[i]) == "nan" or col_service_tutelle[i] == col_services[i]:
                    newService.name = service
                    newService.instance = request.user.instance
                # Si le service a une tutelle
                else:
                    tutelle = Services.objects.filter(name=col_service_tutelle[i], instance=request.user.instance).first()
                    # Si la tutelle n'existe pas on l'ajoute d'abord
                    if tutelle is None:
                        tutelle = Services.objects.create(name=col_service_tutelle[i], instance=request.user.instance)
                    newService.name = service
                    newService.instance = request.user.instance
                    newService.service_tutelle = tutelle.id
    
                newService.save()

    # Ajout des fonctions
    for i, fonction in enumerate(col_fonctions):
        if str(col_fonctions[i]) not in "nan":
            exist  = Fonction.objects.filter(name= fonction, instance=request.user.instance).first()
            if exist is None:
                newFonction = Fonction(name= fonction, instance=request.user.instance)
                newFonction.save()
    
    # Ajout des utilisateurs
    for i, email in enumerate(col_emails):
        if re.match(formatEmail, str(email)) and Utilisateur.objects.filter(email=email.strip()).first() == None:

            # first_name = ""
            # last_name = ""

            # if str(col_prenoms[i]) not in "nan":
            #     longName = getName(col_prenoms[i])
            #     first_name = longName["first_name"]
            #     last_name = longName["last_name"]

            user = Utilisateur(
                email=email.strip(),
                first_name=col_prenoms[i],
                last_name=col_noms[i],
                service=Services.objects.filter(name=col_services[i], instance=request.user.instance).first(),
                fonction=Fonction.objects.filter(name= col_fonctions[i], instance=request.user.instance).first(),
                instance=request.user.instance,
                password="pbkdf2_sha256$20000$2nQjdtoy4qiN$+mbER+cbXOReNlNGoqBXRsAWVlLHIFvhCBe0TRx7qEw="
            )

            if str(col_typeUsers[i]) == "nan":
                user.type_utilisateur = determineUserType(request, col_fonctions[i], col_services[i])
            else:
                user.type_utilisateur = Type_Utilisateur.objects.filter(id=col_typeUsers[i]).first()

            user.save()

    return redirect('user:utilisateurs')
