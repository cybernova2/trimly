from django.contrib import admin
from .models import Salon, ServiceCategory,SalonService

admin.site.register(Salon)
admin.site.register(ServiceCategory)
admin.site.register(SalonService)
