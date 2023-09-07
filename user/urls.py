from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
# from . import views
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path

from .forms import PasswordResetForm
# from django.urls import include, path

from .views import (#full_names, activate, add_function, add_service, add_type_user,
    activate, add_function, add_service, add_type_user, change_password, compagny_configuration_assignation, company_add_annotation, company_info,
    company_name, create_success, delete_function, delete_service, delete_type_user,
    delete_utilistateur, details_type_user, details_users_timing_action,
    export_liste_actions_logs_xls, export_liste_users_timing_xls, full_name,
    list_requestutilisateur, list_type_user, list_utilisateur, LoginView, loadData, logout_view, register, register2,
    RegistrationView, request_register, resend_request_register, statut_utilisateur,
    update_company_info, update_function, update_password, update_service, update_type_user,
    update_utilisateur, update_utilistateur_profile, users_action_tracking, users_timing_action,
    utilisateur_details, utilisateur_profile, view_statistique,list_utilisateurSpc)
app_name = "user"
urlpatterns = [
    url(r'^$', LoginView.as_view(), name='login'),
    url(r'^password_reset/$', PasswordResetView.as_view(form_class=PasswordResetForm), name='password_reset'),
    url(r'password_reset_done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path(r'password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'password_reset_complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    url(r'^enregistrement/$', RegistrationView.as_view(), name='register'),
    url(r'^deconnection/$', logout_view, name='logout'),
    url(r'^mon-profile/(?P<user_id>[0-9]+)/$', utilisateur_profile, name='utilisateur_profile'),
    url(r'^mise-a-jour-des-informations-de-l-utilisateur/(?P<user_id>[0-9]+)$', update_utilistateur_profile, name='update_utilistateur_profile'),
    url(r'^suppression-de-l-utilisateur/(?P<user_id>[0-9]+)$', delete_utilistateur, name='delete_utilistateur'),
    url(r'^changement-de-mot-de-passe/$', change_password, name='change_password'),
    url(r'^creation-avec-success/$', create_success, name='create_success'),
    url(r'^supprimer-fonction/(?P<delete_id>[0-9]+)$', delete_function, name='delete_function'),
    url(r'^ajouter-fonction/$', add_function, name='function'),
    url(r'^mise-a-jour-d-une-fonction/(?P<function_id>[0-9]+)$', update_function, name='update_function'),

    url(r'^companies/$', company_info, name='companies'),
    url(r'^compagnies_configuration_assignation/$', compagny_configuration_assignation, name='companies_configuration_assignation'),
    url(r'^mise-a-jour-company/(?P<company_id>[0-9]+)$', update_company_info, name='update_company_info'),
    url(r'^company-add-annotation/(?P<company_id>[0-9]+)$', company_add_annotation, name='company_add_annotation'),
    url(r'^company-name/$', company_name, name='company_name'),

    url(r'^ajouter-service/$', add_service, name='service'),
    url(r'^mise-a-jour-d-une-service/(?P<service_id>[0-9]+)$', update_service, name='update_service'),
    url(r'^supprimer-service/(?P<service_id>[0-9]+)$', delete_service, name='delete_service'),

    url(r'^supprimer-un-type-d-utilisateur/(?P<delete_id>[0-9]+)$', delete_type_user, name='delete_type_utilisateur'),
    url(r'^list-type-d-utilisateur/$', list_type_user, name='type_utilisateur'),
    url(r'^add-type-d-utilisateur/$', add_type_user, name='add_type_user'),
    url(r'^update-type-d-utilisateur/(?P<pk>[0-9]+)$', update_type_user, name='update_type_user'),
    # url(r'^mise-a-jour-d-un-type-d-utilisateur/(?P<type_utilisateur_id>[0-9]+)$', update_type_user, name='update_type_utilisateur'),
    url(r'^details-d-un-type-d-utilisateur/(?P<type_utilisateur_id>[0-9]+)$', details_type_user, name='details_type_utilisateur'),

    url(r'^enregistrement/$', register, name='register'),
    url(r'^enregistrement-d-un-utilisateur/$', register2, name='register2'),
    url(r'^demande-d-enregistrement/$', request_register, name='request_register'),
    url(r'^renvoi-d-une-demande-d-enregistrement/(?P<user_id>[0-9]+)$', resend_request_register, name='resend_request_register'),
    url(r'^liste-des-demandes/$', list_requestutilisateur, name='list_requests'),
    url(r'^liste-des-utilisateurs/$', list_utilisateur, name='utilisateurs'),
    url(r'^mise-a-jour-d-un-utilisateur/(?P<user_id>[0-9]+)$', update_utilisateur, name='update_utilisateur'),
    url(r'^statuts-d-un-utilisateur/(?P<user_id>[0-9]+)$', statut_utilisateur, name='statut_utilisateur'),
    url(r'^details-d-un-utilisateur/(?P<user_id>[0-9]+)$', utilisateur_details, name='utilisateur_details'),
    url(r'^view-statistique-utilisateur/(?P<user_id>[0-9]+)$', view_statistique, name='view_statistique'),
    
    url(r'^liste-des-actions-sur-gec-mine/$', users_action_tracking, name='users_action_tracking'),
    url(r'^liste-des-temps-utilisations/$', users_timing_action, name='users_timing_action'),
    url(r'^detail-temps-utilisations/(?P<utilisateur_id>[0-9]+)$', details_users_timing_action, name='details_users_timing_action'),
    url(r'^activation/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
        activate, name='activate'),
        
    url(r'^export_liste_actions_logs_xls/$', export_liste_actions_logs_xls, name='export_liste_actions_logs_xls'), 
    url(r'^export_liste_users_timing_xls/$', export_liste_users_timing_xls, name='export_liste_users_timing_xls'),

    #url(r'full_name/', full_names, name='full_names'),
    url(r'user_full_name/(?P<id_user>[0-9]+)$', full_name, name='full_name' ),
    url(r'update_password_user/(?P<user_id>[0-9]+)$', update_password, name='update_password_user' ),
    
    url(r'list_utilisateur-spc/(?P<user_id>[0-9]+)$', list_utilisateurSpc, name='list_utilisateur_spc'),
    url(r'list_utilisateur-spc/$', list_utilisateurSpc, name='list_utilisateur_spc'),
    
    url(r'load-data/$', loadData, name='load_data')

]
