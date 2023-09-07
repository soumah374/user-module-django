allPermissions = [
     
    {
        "group": "transmission",
        "permissions": [
            {"name": "Transmettre", "value": "can_transmit"},
            {"name": "Annuler la transmission", "value": "can_not_transmit"},
            {"name": "Voir transmission", "value": "view_transmit"},
            {"name": "Commenter transmission", "value": "can_comment_transmission"}
        ]
        
    },
    {
        "group": "Courrier Entrant Normal",
        "permissions": [
            {"name": "Voir courrier", "value": "view_courrier_normal"},
            {"name": "Ajouter un courrier", "value": "ajout_courrier_normal"},
            {"name": "Modifier un courrier", "value": "edit_courrier_normal"},
            {"name": "Supprimer un courrier", "value": "delete_courrier_normal"},
            {"name": "Fermer un courrier", "value": "close_courrier_normal"},
            {"name": "Réouvrir un courrier", "value": "unclosed_courrier_normal"},
            {"name": "voir courriers liés", "value": "courrier_entrant_normal_lier"},
        ]
    },
    {
        "group": "Courrier Entrant Particulier",
        "permissions": [
            {"name": "Voir courrier", "value": "view_courrier_particulier"},
            {"name": "Ajouter un courrier", "value": "ajout_courrier_particulier"},
            {"name": "Modifier un courrier", "value": "edit_courrier_particulier"},
            {"name": "Supprimer un courrier", "value": "delete_courrier_particulier"},
            {"name": "Fermer un courrier", "value": "close_courrier_particulier"},
            {"name": "Réouvrir un courrier", "value": "unclosed_courrier_particulier"},
            {"name": "Voir courriers liés", "value": "courrier_entrant_particulier_lier"},
        ]
        
    },
    {
        "group": "courrier normal sortant",
        "permissions": [
            {"name": "Voir courrier", "value": "view_courrier_normal_sortant"},
            {"name": "Ajouter courrier", "value": "add_courrier_normal_sortant"},
            {"name": "Modifier courrier", "value": "edit_courrier_normal_sortant"},
            {"name": "Supprimer courrier", "value": "delete_courrier_normal_sortant"},
            {"name": "Fermer courrier", "value": "close_courrier_normal_sortant"},
            {"name": "Réouvrir un courrier", "value": "unclosed_courrier_normal_sortant"},
            {"name": "Voir courriers liés", "value": "courrier_sortant_normal_lier"},
        ]
    },
    {
        "group": "courrier particulier sortant",
        "permissions": [
            {"name": "Voir courrier", "value": "view_courrier_particulier_sortant"},
            {"name": "Ajouter courrier", "value": "add_courrier_particulier_sortant"},
            {"name": "Modifier courrier", "value": "edit_courrier_particulier_sortant"},
            {"name": "Supprimer courrier", "value": "delete_courrier_particulier_sortant"},
            {"name": "Fermer courrier", "value": "close_courrier_particulier_sortant"},
            {"name": "Réouvrir un courrier", "value": "unclosed_courrier_particulier_sortant"},
            {"name": "Voir courriers liés", "value": "courrier_sortant_particulier_lier"},
        ]
    },
    {
        "group":"Mes courriers",
        "permissions": [
            {"name": "Voir mes courrier general", "value": "view_mes_courrier_normal"},
            {"name": "Voir mes courrier particulier", "value": "view_mes_courrier_particulier"},
        ]
    }, 
    {
        "group":"Annotation courrier",
        "permissions": [
            {"name": "Ajouter annotation", "value": "add_courrier_annotation"},
            {"name": "Voir annotation", "value": "view_courrier_annotation"},
        ]
    },
    {
        "group":"Configuration",
        "permissions": [
            {"name": "voir identifiant normal", "value": "view_identifiant_normal"},
            {"name": "voir identifiant exceptionnel", "value": "view_identifiant_exceptionnel"},
            {"name": "voir type document", "value": "view_type_document"},
            {"name": "voir expediteur destinateur", "value": "view_expediteur_destinateur"},
            {"name": "voir Rayonnage", "value": "view_rayonnage"},
            {"name": "voir Instance", "value": "view_instance"},
            {"name": "voir Annotation", "value": "view_annotation_config"},
            {"name": "voir Email", "value": "view_send_mail"},
        ]
    },
   {
        "group": "Type courrier",
        "permissions": [
            {"name": "voir Type Courrier", "value": "view_type_courrier"},
            {"name": "Ajouter type Courrier", "value": "add_type_courrier"},
            {"name": "Modifier Type Courrier" , "value": "update_type_courrier"},
            {"name": "Supprimer Type Courrier" , "value": "delete_type_courrier"}
        ]
    }, 
    {
        "group": "Assignation",
        "permissions": [
            {"name": "Assigner", "value": "can_assign"},
            {"name": "Voir Assignations", "value": "view_assignation"},
            {"name": "Assigner interne", "value": "can_assign_interne"},
            {"name": "Voir Assignations interne" , "value": "view_assignation_interne"}
        ]
    },
    {
        "group": "Traitement",
        "permissions": [
            {"name": "Voir Traitements", "value": "view_traitement"},
            {"name": "Voir Traitements Interne", "value": "view_traitement_interne"},
            {"name": "Déléguer Gestion de Traitements", "value": "delegate_traitement"}
        ]
    },
    {
        "group": "Amendement",
        "permissions": [
            {"name": "Amender", "value": "can_amend"},
            {"name": "Ajouter Document supplemetaire", "value": "add_docs_supp"},
            
        ]
        
    },
    {
        "group": "Statistiques",
        "permissions": [
            {"name": "Voir Statistiques", "value": "view_stat"},
            {"name": "Voir Suivi de courriers", "value": "view_suivi_courriers"},
            {"name": "Voir Statitique par courrier", "value": "view_stats_par_courrier"},
            {"name": "Voir Statitique par executant", "value": "view_stats_par_executant"},
            {"name": "Voir Statitique par service", "value": "view_stats_par_service"},
            {"name": "Voir Resume", "value": "view_stats_resume"},
            {"name": "Voir graphes", "value": "view_stats_graphes"}
        ]
        
    },
    {
        "group":"Utilisateur",
        "permissions": [
            {"name":"Voir Les utilisateur","value":"view_user"},
            {"name":"Ajouter un utilisateur","value":"add_user"},
            {"name":"Editer un utilisateur","value":"edit_user"},
            # {"name":"Supprimer un utilisateur","value":"delete_user"},
            {"name":"Activer/Desactiver un utilisateur","value":"activer_user"},
            {"name":"Reinitialiser un utilisateur","value":"reset_password_user"},
            {"name":"Ajouter les secretaires particulier","value":"add_secretaire_particulier"},
            {"name":"Voir les temps Utilisation","value":"view_temps_utilisation"},
            {"name":"Charger des données","value":"load_data"},
        ]
    },
    {
        "group":"Type Utilisateur",
        "permissions": [
            {"name":"Voir Les types utilisateur","value":"view_type_user"},
            {"name":"Ajouter un type utilisateur","value":"add_type_user"},
            {"name":"Editer un type utilisateur","value":"edit_type_user"},
            {"name":"Supprimer un type utilisateur","value":"delete_type_user"},
        ]
    },
    {
        "group":"Tableau de bord",
        "permissions": [
            {"name":"Voir Courrier Normal Entrant","value":"view_courrier_normal_entrant_stat"},
            {"name":"Voir Courrier Normal Sortant","value":"view_courrier_normal_sortant_stat"},
            {"name":"Voir Courrier Particulier Entrant","value":"view_courrier_particulier_entrant_stat"},
            {"name":"Voir Courrier Particulier Sortant","value":"view_courrier_particulier_sortant_stat"},
            {"name":"Voir Courrier Normal Traité à temps","value":"view_courrier_normal_done_time_stat"},
            {"name":"Voir Courrier Particulier Traité à temps","value":"view_courrier_particulier_done_time_stat"},
            {"name":"Voir Courrier Normal Traité en retard","value":"view_courrier_normal_done_late_stat"},
            {"name":"Voir Courrier Particulier Traité en retard","value":"view_courrier_particulier_done_late_stat"},
            {"name":"Voir Courrier Normal Encours de Traitement","value":"view_courrier_normal_transmit_stat"},
            {"name":"Voir Courrier Particulier Encours de Traitement","value":"view_courrier_particulier_transmit_stat"},
        ]
    },
    {
        "group":"Fonction",
        "permissions": [
            {"name":"Ajouter une fonction", "value":"add_fonction"},
            {"name":"Voir fonction", "value":"view_fonction"},
            {"name":"Editer fonction", "value":"edit_fonction"},
            {"name":"Supprimer fonction", "value":"delete_fonction"}
        ]
    },
    {
        "group":"Service",
        "permissions": [
            {"name":"Ajouter un service", "value":"add_service"},
            {"name":"Voir service", "value":"view_service"},
            {"name":"Editer service", "value":"edit_service"},
            {"name":"Supprimer service", "value":"delete_service"}
        ]
    },
    {
        "group":"Archive",
        "permissions": [
            {"name":"Voir Archive", "value":"view_archive"},
            {"name":"Voir Archive Courrier Entrant", "value":"view_courrier_archive_entrant"},
            {"name":"Voir Archive Courrier Entrant Particulier", "value":"view_courrier_archive_entrant_particulier"},
            {"name":"Voir Archive Courrier Sortant", "value":"view_courrier_archive_sortant"},
            {"name":"Voir Archive Courrier Sortant Particulier","value":"view_courrier_archive_sortant_particulier"}
        ]
    },
    {
        "group":"Notification",
        "permissions":[
            {"name":"Voir notifications", "value":"view_notification"}
        ]
    }
    ,{
        "group":"Synthèse des courriers",
        "permissions":[
            {"name":"Voir Synthèse", "value":"view_synthese"},
            {"name":"Ajouter Synthèse", "value":"add_synthese"},
            {"name":"Modifier Synthèse", "value":"edit_synthese"}
        ]
    }
    ,{
        "group":"Filtre des courriers",
        "permissions":[
            {"name":"Assignés", "value":"view_filtre_assigne"},
            {"name":"Traités", "value":"view_filtre_traite"},
        ]
    },{
        "group":"Courrier en attente",
        "permissions":[
            {"name": "Voir un courrier en attente", "value": "view_courrier_attente"},
            {"name":"Validation du courrier en attente", "value":"validation_en_attente"},
            {"name":"Supprimer le courrier en atternte", "value":"supprimer_en_attente"},
            {"name":"Réjeter le courrier en atternte", "value":"rejeter_en_attente"},
        ]
    }
]

