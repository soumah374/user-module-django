from user.constance import ADMINISTRATEUR
from user.models import CompanyFonction, Type_Utilisateur, Utilisateur

def get_fonction_key(obj):
      return obj['order']

def get_order(fonction, company_fonctions):
    if company_fonctions:
        for c_fct in company_fonctions:
            fonction_id = int(c_fct.fonction_id)
            if(fonction_id == fonction.id):
                return {"fonction_id": int(c_fct.fonction_id), "order": int(c_fct.order), "genre": c_fct.genre,"message_annotation":c_fct.message_annotation}
    return False

def order_current_user(array_fct,fonction_id):
    for fct in array_fct:
        if fonction_id == int(fct['fonction_id']):
            return int(fct.get('order' or None))
    return None

def checking_user_fonction(fonction_id,user_id):
    if CompanyFonction.objects.filter(fonction_id = fonction_id, user_id = user_id).exists():
        return True
    return False
    
def index_user_fonction(fonction_id, user_id):
    if CompanyFonction.objects.filter(fonction_id = fonction_id, user_id = user_id).exists():
        return CompanyFonction.objects.filter(fonction_id = fonction_id,user_id = user_id).first().order
    return 0

def genre_user_fonction(fonction_id,user_id):
    if CompanyFonction.objects.filter(fonction_id = fonction_id, user_id = user_id).exists():
        return CompanyFonction.objects.filter(fonction_id = fonction_id,user_id = user_id).first().genre
    return ""

def message_annotation(fonction_id,user_id):
    if CompanyFonction.objects.filter(fonction_id = fonction_id, user_id = user_id).exists():
        return CompanyFonction.objects.filter(fonction_id = fonction_id,user_id = user_id).first().message_annotation
    return ""

def company_fonction(fonction_id, user_id):
    return CompanyFonction.objects.filter(fonction_id = fonction_id,user_id = user_id).first()

def determineUserType(request, fonction, service):
    types = Type_Utilisateur.objects.all()
    typeAdministrateur = types.filter(instance=request.user.instance, name=ADMINISTRATEUR).first()
    typeChefSecretaireCentral = types.filter(instance=request.user.instance, name="Chef Secrétaire Central").first()
    typeSecretaireCentral = types.filter(instance=request.user.instance, name="Secrétaire Central").first()
    typeSecretaireParticulier = types.filter(instance=request.user.instance, name="Secrétaire Particulier").first()
    typeArchiveur = types.filter(instance=request.user.instance, name="Archiveur").first()
    typeChef = types.filter(instance=request.user.instance, name="Chef de service").first()
    typeChefAdjoint = types.filter(instance=request.user.instance, name="Chef adjoint de service").first()
    typeDirecteur = types.filter(instance=request.user.instance, name="Directeur").first()
    typeDirecteurAdjoint = types.filter(instance=request.user.instance, name="Directeur Adjoint").first()
    typeExecutant = types.filter(instance=request.user.instance, name="Exécutant").first()
    typeSimpleUtilisateur = types.filter(instance=request.user.instance, name="Simple Utilisateur").first()

    if str(fonction) == "nan":
        fonction = str(fonction)

    if request.user.instance.type == "Direction":

        if fonction.lower() == "directeur general":
            return typeAdministrateur
        elif fonction.lower() == "directeur general adjoint"  or (" adjoint" in fonction.lower() and "directeur" in fonction.lower()):
            return typeAdministrateur
        elif "directeur" in fonction.lower():
            return typeDirecteur
        elif fonction.lower() == "chef de service" or fonction.lower() == "chef de division" or ("chef " in fonction.lower() and fonction.lower() not in "chef secrétaire central"):
            return typeChef
        elif fonction.lower() == "chef de service adjoint" or (" adjoint" in fonction.lower() and "chef " in fonction.lower()):
            return typeChefAdjoint
        elif fonction.lower() == "chef secrétaire central":
            return typeChefSecretaireCentral
        elif fonction.lower() == "Secrétaire Central":
            return typeSecretaireCentral
        elif fonction.lower() == "archiveur":
            return typeArchiveur
        elif fonction.lower() == "simple utilisateur":
            return typeSimpleUtilisateur
        else:
            return typeExecutant
    elif request.user.instance.type == "Departement":

        if fonction.lower() == "ministre":
            return typeAdministrateur
        elif "chef de cabinet" in fonction.lower() or "cheffe de cabinet" in fonction.lower():
            return typeAdministrateur
        elif "secrétaire général" in fonction.lower() or "secretaire general" in fonction.lower():
            return typeAdministrateur
        elif fonction.lower() == "directeur general":
            return typeDirecteur
        elif fonction.lower() == "directeur general adjoint" or (" adjoint" in fonction.lower() and "directeur" in fonction.lower()):
            return typeDirecteurAdjoint
        elif "directeur" in fonction.lower():
            return typeDirecteur
        elif fonction.lower() == "chef de service" or fonction.lower() == "chef de division" or ("chef " in fonction.lower() and fonction.lower() not in "chef secrétaire central"):
            return typeChef
        elif fonction.lower() == "chef de service adjoint" or (" adjoint" in fonction.lower() and "chef " in fonction.lower()):
            return typeChefAdjoint
        elif fonction.lower() == "chef secrétaire central":
            return typeChefSecretaireCentral
        elif fonction.lower() == "Secrétaire Central":
            return typeSecretaireCentral
        elif fonction.lower() == "archiveur":
            return typeArchiveur
        elif fonction.lower() == "simple utilisateur":
            return typeSimpleUtilisateur
        else:
            return typeExecutant

def getName(name):
    long_name = dict()
    names = name.split(" ")
    long_name["first_name"] = ""
    #long_name["last_name"] = names[len(names)-1]
    long_name["last_name"] = names[0]
    for i, n in enumerate(names):
        if i > 0 and i < len(names):
            long_name["first_name"] += names[i] + " "

    long_name["first_name"]  =  long_name["first_name"].strip()

    return long_name