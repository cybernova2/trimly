from django.urls import path
from .views import (
    book_slot,
    confirmation,
    customer_dashboard,
    cancel_booking,
    update_booking_status,
    load_time_slots,get_time_slots,reschedule_booking
)

app_name = 'bookings' 

urlpatterns = [
    path('book/', book_slot, name='book_slot'),
        path('confirmation/<int:booking_id>/', confirmation, name='confirmation'),
     path('update/<int:booking_id>/<str:status>/', update_booking_status, name='update_status'),
    path('dashboard/', customer_dashboard, name='customer_dashboard'),
    path('cancel/<int:booking_id>/', cancel_booking, name='cancel_booking'),
    path('load-slots/', load_time_slots, name='load_slots'),
    path('get-slots/', get_time_slots, name='get_slots'),
    path('my-bookings/', customer_dashboard, name='customer_dashboard'),
    path('reschedule/<int:booking_id>/',reschedule_booking,name='reschedule_booking'),


]
