from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from bookings.models import Booking
from django.contrib.auth.decorators import login_required
from .models import Salon, ServiceCategory, SalonService
from .forms import SalonForm,ServiceForm
from django.http import JsonResponse
from bookings.views import redirect_if_shopkeeper
from bookings.utils import generate_time_slots
from datetime import datetime

@login_required
def create_salon(request):
    # If salon already exists → redirect
    if Salon.objects.filter(owner=request.user).exists():
        salon = Salon.objects.get(owner=request.user)
        return redirect('salon_dashboard', salon_id=salon.id)

    if request.method == 'POST':
        form = SalonForm(request.POST)
        if form.is_valid():
            salon = form.save(commit=False)
            salon.owner = request.user
            salon.save()
            return redirect('salon_dashboard', salon_id=salon.id)
    else:
        form = SalonForm()

    return render(request, 'salons/create_salon.html', {'form': form})

@login_required
def edit_salon(request):
    salon = get_object_or_404(Salon, owner=request.user)

    if request.method == 'POST':
        form = SalonForm(request.POST, instance=salon)
        if form.is_valid():
            form.save()
            return redirect('salon_dashboard', salon_id=salon.id)
    else:
        form = SalonForm(instance=salon)

    return render(request, 'salons/edit_salon.html', {'form': form})


@login_required
def add_service(request):
    salon = get_object_or_404(Salon, owner=request.user)

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.salon = salon
            service.save()
            return redirect('salon_dashboard', salon_id=salon.id)
    else:
        form = ServiceForm()

    return render(request, 'salons/add_service.html', {'form': form, 'salon': salon,
                                                       })

@login_required
def edit_service(request, service_id):
    service = get_object_or_404(
       SalonService,
        id=service_id,
        salon__owner=request.user
    )

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('salon_dashboard', salon_id=service.salon.id)
    else:
        form = ServiceForm(instance=service)

    return render(request, 'salons/edit_service.html', {
        'form': form,
        'service': service   
    })

@login_required
def delete_service(request, service_id):
    service = get_object_or_404(SalonService, id=service_id, salon__owner=request.user)
    salon_id = service.salon.id
    service.delete()
    return redirect('salon_dashboard', salon_id=salon_id)



@login_required
def salon_list(request):

    redirect_response = redirect_if_shopkeeper(request)
    if redirect_response:
        return redirect_response


    salons = Salon.objects.filter(is_active=True)
    services = ServiceCategory.objects.all().distinct()

    return render(request, 'salons/salon_list.html', {'salons': salons,  "services": services,'today': timezone.localdate(),

                                                      })

def get_services(request):
    salon_id = request.GET.get('salon')

    if not salon_id:
        return JsonResponse({'services': []})

    services = SalonService.objects.filter(salon_id=salon_id)

    data = [
        {
            'id': service.id,
            'name': service.service.name
        }
        for service in services
    ]

    return JsonResponse({'services': data})


@login_required
def salon_dashboard(request, salon_id):
    salon = get_object_or_404(Salon, id=salon_id)

    if salon.owner != request.user:
        return redirect('/')

    today = timezone.localdate()

    todays_bookings = Booking.objects.filter(
        salon=salon,
        date=today
    ).exclude(status='cancelled').order_by('time')

    upcoming_bookings = Booking.objects.filter(
        salon=salon,
        date__gt=today
    ).exclude(status='cancelled').order_by('date', 'time')

    services = SalonService.objects.filter(salon=salon)

    return render(request, 'salons/salon_dashboard.html', {
        'salon': salon,
        'todays_bookings': todays_bookings,
        'upcoming_bookings': upcoming_bookings,
        'services': services
    })


def available_salons(request):
    date_str = request.GET.get("date")
    service_id = request.GET.get("service")

    if not date_str or not service_id:
        return JsonResponse({"salons": []})

    try:
        date = datetime.strptime(
            date_str,
            "%Y-%m-%d"
        ).date()
    except ValueError:
        return JsonResponse({"salons": []})

    try:
        category = ServiceCategory.objects.get(
            id=service_id
        )
    except ServiceCategory.DoesNotExist:
        return JsonResponse({"salons": []})

    salon_services = SalonService.objects.filter(
        service=category
    )

    result = []

    for salon_service in salon_services:

        salon = salon_service.salon

        slots = generate_time_slots(
            salon.opening_time,
            salon.closing_time,
            salon_service.duration_minutes
        )

        booked = Booking.objects.filter(
            salon=salon,
            service=salon_service,
            date=date,
            status__in=["confirmed", "pending"]
        ).values_list(
            "time",
            flat=True
        )

        free_slots = [
            s for s in slots
            if s not in booked
        ]

        if free_slots:
            result.append({
                "id": salon.id,
                "name": salon.name,
                "address": salon.address,
                "salon_service_id": salon_service.id,
            })

    return JsonResponse({"salons": result})