from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('modules.core.urls')),
    path('karfa/', include('modules.karfa.urls')),
    path('dettes/', include('modules.dettes.urls')),
    path('comptes/', include('modules.comptes.urls')),
    path('parametres/', include('modules.parametres.urls')),
]