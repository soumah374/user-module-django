import django_elasticsearch_dsl
from ged.models import Type_Document
from django import forms
#
#
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import *
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML, Field
from instances.constance import ADMINISTRATEUR_INSTANCE
from user.constance import OTHER, SUPER_ADMINISTRATEUR
from .models import *
from gec.models import Company
import datetime
from django.urls import reverse
from django.contrib.postgres.forms import SimpleArrayField
from django.contrib.auth.forms import PasswordResetForm
from django.template import loader
from django.core.mail import EmailMultiAlternatives
# constantes
GENDER_CHOICES = (
    ('Masculin', 'Masculin'),
    ('Féminin', 'Féminin')
)

class RegistrationForm(UserCreationForm):

    class Meta:
        model = Utilisateur
        fields = ('email', 'first_name', 'last_name', 'password1',
                'password2', 'matricule', 'genre')
        labels = {
            'matricule': ('Matricule'),
            'email': ('Email'),
            'first_name': ('First Name'),
            'last_name': ('Last Name'),
            'genre': ('Genre')
        }

    def __init__(self, user_obj, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'matricule',
            'first_name',
            'last_name',
            'genre',
            'email',
            'password1',
            'password2',
            ButtonHolder(
                Submit('register', ('Register'))
            )
        )

        if user_obj.is_controller:
            self.initial['ministry'] = user_obj.ministry.id
            self.fields['ministry'].disabled = True


class LoginForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ('email', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                ('Connexion'),
                Field('username', css_class='validate', id='username-field', placeholder=' votre adresse email'),
                Field('password', css_class='validate', id='password-field', placeholder=' votre mot de passe')
            ),
            ButtonHolder(
                HTML('<button type="submit" class="btn btn-material btn-large">\
                    <i class="fa fa-unlock"></i> Se connecter</button>'                                                                       )
            )
        )


class FonctionForm(forms.ModelForm):
    class Meta:
        model = Fonction
        fields = ['name','sigle']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'validate'
            }),
            'sigle': forms.TextInput(attrs={
                'class':'validate'
            })
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Services
        fields = ['name',]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'validate',
            }),
        }
class TypeDocumentForm(forms.ModelForm):
    class Meta:
        model = Type_Document
        fields = ['name', 'cycle_vie']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'validate',
            })
        }

class TypeUtilisateurForm(forms.ModelForm):
    class Meta:
        model = Type_Utilisateur
        fields = ['name', 'home']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'validate'
            }),
            'home': forms.TextInput(attrs={
                'class': 'validate'
            })
        }

class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['name_permission']

        widgets = {
            'name_permission': forms.SelectMultiple(attrs={
                'class': 'validate'
            })
        }
    
class UtilisateurForm(forms.ModelForm):
    def __init__(self, user,*args, **kwargs):
        super(UtilisateurForm, self).__init__(*args, **kwargs)
        self.user = user
        #type utilisateur
        self.other_user = Type_Utilisateur.objects.filter(name=OTHER,instance=self.user.instance).first()
        type_utilisateurs = Type_Utilisateur.objects.filter(instance = self.user.instance).exclude(name__in=[SUPER_ADMINISTRATEUR,OTHER]).all()
        type_utilisateurs.append(self.other_user)
        self.request = kwargs.pop('request',None)
        self.fields['type_utilisateur'].queryset = type_utilisateurs
        # Fonction 
        self.other_fonction = Fonction.objects.filter(name=OTHER,instance = self.user.instance).first()
        fonctions = Fonction.objects.filter(instance = self.user.instance).all()
        fonctions.append(self.other_fonction)
        self.fields['fonctions'].queryset = fonctions
        
        self.fields['fonction'].queryset = Utilisateur.objects.filter(fonction_id__in=[1, 2, 3])
            
    class Meta:
        model = Utilisateur
        fields = ('matricule', 'first_name', 'last_name', 'phone', 'address', 'email','password' )

        widgets = {
            'matricule': forms.fields.TextInput(attrs={
                'class': 'validate'
            }),
            'first_name': forms.fields.TextInput(attrs={
                'class': 'validate'
            }),
            'last_name': forms.fields.TextInput(attrs={
                'class': ''
            }),
            'email': forms.fields.EmailInput(attrs={
                'class': 'validate'
            }),
            'phone': forms.fields.TextInput(attrs={
                'class': 'validate',
                'type': 'tel',
                'id' : 'phone',
                'min' : '600000000',
                'max' : '699999999',
                'pattern' : '^6(3|2|6|5|8|1)[0-9]{7}',
                'title' : 'S\'il vous plait veuiller respecter le format de téléphone guineen'
            }),
            'address': forms.Textarea(attrs={
                'class': 'validate materialize-textarea',
            })
        }

    CHOICES = (
        ('Masculin', 'Masculin'),
        ('Féminin', 'Féminin')
    )


    genre = forms.ChoiceField(choices = CHOICES, label="Genre", initial='', widget=forms.Select(attrs={'class':'validate'}), required=True)

    service = forms.ModelChoiceField(
                    queryset=None,
                    widget=forms.Select(attrs={'class':'validate'}),
                    required=True
                    )
    fonction = forms.ModelChoiceField(
                    queryset=None,
                    widget=forms.Select(attrs={'class':'validate'})
                    )
    type_utilisateur = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'validate'})
    )


class UtilisateurForm2(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(UtilisateurForm2, self).__init__(*args, **kwargs)
        self.user = user
        self.request = kwargs.pop('request', None)
        #self.fields['service'] = Services.objects.filter(instance = self.user.instance).order_by('name')
        #self.fields['fonction'] = Fonction.objects.filter(instance = self.user.instance).order_by('name')
    class Meta:
        model = Utilisateur
        fields = ('matricule', 'first_name', 'last_name', 'second_email',
                  'phone', 'address', 'email', 'type_utilisateur')

        widgets = {
            'matricule': forms.fields.TextInput(attrs={
                'class': 'validate'
            }),
            'first_name': forms.fields.TextInput(attrs={
                'class': 'validate'
            }),
            'last_name': forms.fields.TextInput(attrs={
                'class': ''
            }),
            'second_email': forms.fields.EmailInput(attrs={
                'class': 'validate',
                'required': False
            }),
            'email': forms.fields.EmailInput(attrs={
                'class': 'validate',
                'readonly': True,
            }),
            'phone': forms.fields.TextInput(attrs={
                'class': 'validate',
                'type': 'tel',
                'id': 'phone',
                'min': '600000000',
                'max': '699999999',
                'pattern': '^6(3|2|6|5)[0-9]{7}',
                'title': 'S\'il vous plait veuiller respecter le format de téléphone guineen'
            }),
            'address': forms.Textarea(attrs={
                'class': 'validate materialize-textarea'
            }),
            'type_utilisateur': forms.fields.TextInput(attrs={
                'class': 'validate',
                'readonly': True,
            }),

        }

    CHOICES = (
        ('Masculin', 'Masculin'),
        ('Féminin', 'Féminin')
    )


    genre = forms.ChoiceField(choices=CHOICES, label="Genre", initial='', widget=forms.Select(attrs={}), required=True)

    #service = forms.ModelChoiceField(
    #    queryset= None, 
    #    widget=forms.Select(attrs={}),required=True
    #)
    #fonction = forms.ModelChoiceField(
    #    queryset=None,
    #    widget=forms.Select(attrs={'class': 'validate'})
    #)


class UpdateUtilisateurForm(forms.ModelForm):
    def __init__(self, utilisateur,current_user,* args, **kwargs):
        super(UpdateUtilisateurForm, self).__init__(*args, **kwargs)
        self.current_user = current_user
        self.fields['type_utilisateur'] = Type_Utilisateur.objects.filter(instance = self.current_user.instance).exclude(name = SUPER_ADMINISTRATEUR)
        self.fields['fonction'] = Fonction.objects.filter(instance = self.current_user.instance)
        self.fields['service'] = Services.objects.filter(instance = self.current_user.instance)
        
        self.initial['matricule']        = utilisateur.matricule
        self.initial['first_name']       = utilisateur.first_name
        self.initial['last_name']        = utilisateur.last_name
        self.initial['service']          = utilisateur.service
        self.initial['fonction']         = utilisateur.fonction
        self.initial['phone']            = utilisateur.phone
        self.initial['address']          = utilisateur.address
        self.initial['email']            = utilisateur.email
        self.initial['second_email']     = utilisateur.second_email
        self.initial['type_utilisateur'] = utilisateur.type_utilisateur
        self.initial['genre']            = utilisateur.genre
        self.initial['is_chef']          = utilisateur.is_chef
        self.initial['is_adjoint']       = utilisateur.is_adjoint
        
    
    class Meta:
        model = Utilisateur
        fields  = ['matricule', 'first_name', 'last_name', 'service', 'fonction', 'type_utilisateur', 'phone', 'address', 'email', 'second_email', 'genre', 'is_chef', 'is_adjoint']

        widgets = {
            'matricule': forms.TextInput(attrs={
                'class': 'validate'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'validate'
            }),
            'last_name': forms.TextInput(attrs={
                'class': ''
            }),
            'fonction': forms.Select(
                attrs={
                'class': 'validate'
            }),
            'email': forms.fields.EmailInput(attrs={
                'class': 'validate'
            }),
            'second_email': forms.fields.EmailInput(attrs={
                'class': 'validate',
                'required': False
            }),
            'type_utilisateur': forms.Select(attrs={
                'class': 'validate',
                'readonly': False,
            }),
            'genre': forms.Select(attrs={
                'class': 'validate',
                'id':'genre',
            }),
            # 'is_chef': forms.BooleanField(),
            # 'is_adjoint': forms.BooleanField(),
        }
    phone = forms.CharField(
        widget=forms.fields.TextInput(attrs={
                    'class': 'validate',
                    'type': 'tel',
                    'id': 'phone',
                    'min': '600000000',
                    'max': '699999999',
                    'pattern': '^6(3|2|6|5)[0-9]{7}',
                    'title': 'S\'il vous plait veuiller respecter le format de téléphone guineen',
            }),
        required=False
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
        'class': 'validate materialize-textarea',
            }),
        required=False
    )
        

class RequestUtilisateurForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.request = kwargs.pop('request',None)
        super(RequestUtilisateurForm,self).__init__(*args, **kwargs)
        self.configAnnotationInstance = [config.user.fonction.id for config in ConfigAnnotationInstance.objects.filter(instance=self.user.instance)]
        self.type_other = Type_Utilisateur.objects.filter(name=OTHER,instance=self.user.instance)
        # type utilisateur
        type_utilisateurs = Type_Utilisateur.objects.filter(instance = self.user.instance).exclude(name__in=[SUPER_ADMINISTRATEUR,ADMINISTRATEUR_INSTANCE,OTHER])
        self.fields['type_utilisateur'].queryset = type_utilisateurs
        self.fields['fonctions'].queryset = Fonction.objects.filter(instance = self.user.instance).all()
        self.fields['fonction'].queryset = Utilisateur.objects.filter(fonction_id__in=self.configAnnotationInstance,instance=self.user.instance)
        self.fields['service'].queryset = Services.objects.filter(instance=self.user.instance).exclude(name=OTHER)
       
    class Meta:
        model = Utilisateur
        fields = ['email','second_email','type_utilisateur','fonction','fonctions']

        widgets = {
            'email': forms.fields.EmailInput(attrs={
                'class': 'validate'
            })
        }
        
    second_email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'validate'}),
        required=False
    )
    
    type_utilisateur = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'validate','id':'type_utilisateur'})
    )
    fonctions = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'validate','id':'fonctions'}), required=True
    )
    fonction = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'validate','id':'fonction'}), required=False
    )
    service = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'validate','id':'service'}), required=True
    )


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name','sigle','logo','type','category']
        
        fonctions = forms.ModelChoiceField(
            queryset=Fonction.objects.all(),
            widget=forms.Select(attrs={'class': 'validate'})
        )

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'validate'
            }),
            'sigle': forms.TextInput(attrs={
                'class': 'validate'
            })
        }

class PasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject =loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlineslocalhost
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
  
        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        if context['user'].second_email:
            email_message_2 = EmailMultiAlternatives(subject, body, from_email, [context['user'].second_email])
            if html_email_template_name is not None:
                html_email = loader.render_to_string(html_email_template_name, context)
                email_message_2.attach_alternative(html_email, "text/html")
        email_message.content_subtype = "html"
        email_message.send()
        if context['user'].second_email:
            email_message_2.send()
