from django.shortcuts import render, redirect,get_object_or_404
from .forms import BookingForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Booking
from datetime import datetime, timedelta
from django.http import JsonResponse
from .utils import generate_time_slots
from django.contrib.auth.decorators import login_required
from .forms import BookingForm,RescheduleBookingForm
from salons.models import Salon, SalonService
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def redirect_if_shopkeeper(request):
    if request.user.profile.user_type == 'shopkeeper':
       salon = Salon.objects.filter(owner=request.user).first()

       if salon:
          return redirect('salon_dashboard', salon_id=salon.id)
    return None


def load_time_slots(request):
    form = BookingForm(request.GET)
    return render(request, 'bookings/time_slots.html',  {'time_field': form['time']})


from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from salons.models import Salon, SalonService
from .models import Booking
from .utils import generate_time_slots


def get_time_slots(request):
    salon_id = request.GET.get('salon')
    service_id = request.GET.get('service')
    date_str = request.GET.get('date')

    #  Required params
    if not (salon_id and service_id and date_str):
        return JsonResponse({'slots': []})

    try:
        salon = Salon.objects.get(id=salon_id)
        service = SalonService.objects.get(id=service_id)
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except (Salon.DoesNotExist, SalonService.DoesNotExist, ValueError):
        return JsonResponse({'slots': []})

    #  Generate base slots using service duration
    slots = generate_time_slots(
        salon.opening_time,
        salon.closing_time,
        service.duration_minutes
    )

    #  Existing bookings
    bookings = Booking.objects.filter(
        salon=salon,
        date=date,
        status__in=['pending', 'confirmed']
    )

    available_slots = []
    now = timezone.now()

    for slot in slots:
        #  Make slot timezone-aware
        slot_start = timezone.make_aware(
            datetime.combine(date, slot),
            timezone.get_current_timezone()
        )
        slot_end = slot_start + timedelta(
            minutes=service.duration_minutes
        )

        conflict = False

        #  Overlap check
        for booking in bookings:
            b_start = timezone.make_aware(
                datetime.combine(date, booking.time),
                timezone.get_current_timezone()
            )
            b_end = b_start + timedelta(
                minutes=booking.service.duration_minutes
            )

            if slot_start < b_end and slot_end > b_start:
                conflict = True
                break

        # 1-hour advance rule
        if date == now.date() and slot_start <= now + timedelta(hours=1):
            conflict = True

        if not conflict:
            available_slots.append(slot.strftime('%H:%M'))

    return JsonResponse({'slots': available_slots})

@login_required
def book_slot(request):
    #  Block shopkeepers
    redirect_response = redirect_if_shopkeeper(request)
    if redirect_response:
        return redirect_response

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.salon = booking.service.salon
            booking.save()
            return redirect('bookings:confirmation', booking_id=booking.id)
    else:
         form = BookingForm(initial={
        'salon': request.GET.get('salon'),
        'service': request.GET.get('service'),
        'date': request.GET.get('date'),
    })

    return render(request, 'bookings/book_slot.html', {'form': form})

@login_required
def confirmation(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )
    return render(request, 'bookings/confirmation.html', {'booking': booking})



@login_required
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id)

    #  Customer rule
    if request.user.profile.user_type == 'customer':
        if booking.user != request.user:
            return HttpResponseForbidden()

    #  Shopkeeper rule
    elif request.user.profile.user_type == 'shopkeeper':
        if booking.salon.owner != request.user:
            return HttpResponseForbidden()

    booking.status = status
    booking.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def customer_dashboard(request):
    redirect_response = redirect_if_shopkeeper(request)
    if redirect_response:
        return redirect_response

    bookings = Booking.objects.filter(
        user=request.user,
        date__gte=timezone.localdate()
    ).order_by('date', 'time')

    return render(request, 'bookings/customer_dashboard.html', {
        'bookings': bookings
    })



@login_required
def cancel_booking(request, booking_id):
    if request.user.profile.user_type != 'customer':
        return HttpResponseForbidden()

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )
    booking.status = 'cancelled'
    booking.save()
    return redirect('bookings:customer_dashboard')



@login_required
def reschedule_booking(request, booking_id):
    booking = Booking.objects.filter(
        id=booking_id,
        user=request.user
    ).exclude(
        status='cancelled'
    ).first()

    if not booking:
        return redirect('bookings:customer_dashboard')

    if request.method == 'POST':
        form = RescheduleBookingForm(
            request.POST,
            instance=booking,
            booking=booking
        )
        if form.is_valid():
            form.save()
            return redirect('bookings:customer_dashboard')
    else:
        form = RescheduleBookingForm(
            instance=booking,
            booking=booking,
            initial={
                'date': booking.date,
                'time': booking.time.strftime('%H:%M')
            }
        )

    return render(request, 'bookings/reschedule_booking.html', {
        'form': form,
        'booking': booking
    })


