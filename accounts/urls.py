from django.urls import path
from .views import register, RoleBasedLoginView
from .views import logout_view

app_name = 'accounts'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', RoleBasedLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
]
