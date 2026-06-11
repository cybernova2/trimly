"""
URL configuration for trimly_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.shortcuts import render
from salons.views import salon_dashboard
from trimly_core.views import home


# def home(request):
#     return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
  path('', home, name='home'),            
    path('salons/', include('salons.urls')),
    path('accounts/', include('accounts.urls')),

    path('bookings/', include('bookings.urls')),
    path('book/', include('bookings.urls')), 
        path('salon-dashboard/<int:salon_id>/', salon_dashboard, name='salon_dashboard'),
]
