from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render  

def test(request):  
    return render(request, 'test.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test/', test),  
    path('', include('modules.karfa.urls')),
]