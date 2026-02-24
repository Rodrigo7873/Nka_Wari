from modules.core.services.prix_or_service import recuperer_prix_or as core_recuperer_prix_or


def recuperer_prix_or():
    """Wrapper backward-compatible qui délègue au service central."""
    return core_recuperer_prix_or()