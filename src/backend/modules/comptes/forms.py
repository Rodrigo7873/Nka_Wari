from django import forms
from django.core.exceptions import ValidationError
from .models.argent import CompteArgent
from .models.or_ import CompteOr

class CompteArgentForm(forms.ModelForm):
    class Meta:
        model = CompteArgent
        fields = ['nom', 'type_compte', 'solde', 'dette_liee']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # On ne propose que les dettes de l'utilisateur qui ne sont pas encore liées à un compte
            from modules.dettes.models import Dette
            self.fields['dette_liee'].queryset = Dette.objects.filter(cree_par=user, archive=False)
            self.fields['dette_liee'].label = "Lier à une dette existante (Optionnel)"
            self.fields['dette_liee'].required = False

class CompteOrForm(forms.ModelForm):
    class Meta:
        model = CompteOr
        fields = ['nom', 'poids_grammes', 'carat']

    def clean_poids_grammes(self):
        poids = self.cleaned_data.get('poids_grammes')
        if poids is not None:
            # Convert weight to string and check decimal places
            s_poids = str(poids).rstrip('0').rstrip('.')
            if '.' in s_poids:
                # Get the part after the dot
                decimals = s_poids.split('.')[1]
                if len(decimals) > 2:
                    raise ValidationError("Le poids ne peut pas avoir plus de 2 décimales.")
        return poids
