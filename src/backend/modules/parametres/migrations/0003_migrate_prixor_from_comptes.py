from django.db import migrations, models


def copy_prix_from_comptes(apps, schema_editor):
    PrixOrParam = apps.get_model('parametres', 'PrixOrParam')
    try:
        PrixOrComptes = apps.get_model('comptes', 'PrixOr')
    except LookupError:
        # Si le modèle comptes.PrixOr n'existe pas (déjà supprimé), rien à faire
        return

    for p in PrixOrComptes.objects.all().order_by('date_saisie'):
        PrixOrParam.objects.create(prix_gramme=p.prix_gramme, date_saisie=p.date_saisie)


def noop_reverse(apps, schema_editor):
    # Aucun rollback nécessaire
    return


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0002_about_parametres_delete_aboutinfo_delete_formatparam_and_more'),
        ('comptes', '0002_alter_compteargent_options_alter_compteor_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrixOrParam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prix_gramme', models.DecimalField(decimal_places=0, max_digits=12, verbose_name="Prix du gramme d'or (GNF)")),
                ('date_saisie', models.DateTimeField(auto_now_add=True, verbose_name='Date de saisie')),
            ],
            options={
                'verbose_name': "Paramètre - Prix de l'or",
                'verbose_name_plural': "Paramètres - Prix de l'or",
                'get_latest_by': 'date_saisie',
            },
        ),
        migrations.RunPython(copy_prix_from_comptes, noop_reverse),
    ]
