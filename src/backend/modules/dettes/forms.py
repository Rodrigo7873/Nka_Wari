from django import forms
from modules.dettes.models import Dette
from modules.comptes.models import CompteArgent

class DetteForm(forms.ModelForm):
    compte_debit = forms.ModelChoiceField(
        queryset=CompteArgent.objects.none(),
        required=False,
        label="Compte à débiter",
        widget=forms.Select(attrs={'class': 'field-input'})
    )

    class Meta:
        model = Dette
        fields = ['sens', 'personne', 'montant', 'motif', 'echeance', 'garantie', 'compte_debit']
        widgets = {
            'sens': forms.HiddenInput(),  # On va gérer le sens via les boutons comme avant
            'personne': forms.TextInput(attrs={'class': 'field-input', 'placeholder': 'Nom de la personne'}),
            'montant': forms.TextInput(attrs={'class': 'field-input', 'placeholder': '0', 'oninput': 'formatMontant(this)', 'inputmode': 'numeric'}),
            'motif': forms.Textarea(attrs={'class': 'field-input', 'placeholder': 'Raison de cette dette...', 'rows': 3}),
            'echeance': forms.DateInput(attrs={'class': 'field-input', 'type': 'date'}),
            'garantie': forms.TextInput(attrs={'class': 'field-input', 'placeholder': 'Ex: Téléphone, terrain...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Afficher uniquement les comptes Argent avec solde > 0 du USER (Exclure les comptes DETTE)
            self.fields['compte_debit'].queryset = CompteArgent.objects.filter(
                cree_par=user, archive=False, solde__gt=0
            ).exclude(type_compte='DETTE')
            # Personnaliser l'affichage du libellé
            self.fields['compte_debit'].label_from_instance = lambda obj: f"{obj.nom} ({obj.solde:,.0f} GNF)"

    def clean(self):
        cleaned_data = super().clean()
        sens = cleaned_data.get('sens')
        montant = cleaned_data.get('montant')
        compte = cleaned_data.get('compte_debit')

        if sens == 'ON_ME_DOIT':
            if not compte:
                self.add_error('compte_debit', "Un compte doit être sélectionné pour une créance (On me doit).")
            elif montant and compte.solde < montant:
                self.add_error('compte_debit', f"Solde insuffisant sur le compte sélectionné ({compte.solde:,.0f} GNF).")
        
        return cleaned_data
