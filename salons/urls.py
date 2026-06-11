from django.urls import path
from .views import salon_list,get_services, create_salon,salon_dashboard,add_service,edit_service,delete_service,edit_salon,available_salons

app_name = 'salons'

urlpatterns = [
    path('', salon_list, name='salon_list'),
    path('create/', create_salon, name='create_salon'),
    path('dashboard/<int:salon_id>/', salon_dashboard, name='salon_dashboard'),
    path('service/add/', add_service, name='add_service'),
path('service/<int:service_id>/edit/', edit_service, name='edit_service'),
path('service/<int:service_id>/delete/', delete_service, name='delete_service'),
path('get-services/', get_services, name='get_services'),

path('edit/', edit_salon, name='edit_salon'),
path("available/", available_salons, name="available_salons"),





    
]
