from django.urls import path
from . import views

app_name = 'karfa'

urlpatterns = [
    path('', views.karfa_list, name='karfa_list'),
    path('creer/', views.karfa_create, name='karfa_create'),
    path('<uuid:pk>/', views.karfa_detail, name='karfa_detail'),
    path('<uuid:pk>/restituer/', views.karfa_restituer, name='karfa_restituer'),
]