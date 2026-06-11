from django import forms
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Booking
from .utils import generate_time_slots
from salons.models import Salon, SalonService


class BookingForm(forms.ModelForm):
    # time = forms.ChoiceField(choices=[], required=True)
    time = forms.TimeField(
    input_formats=['%H:%M'],
    required=True
)

    class Meta:
        model = Booking
        fields = ['salon', 'service', 'date', 'time']
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'min': timezone.localdate().isoformat(),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['time'].choices = []

        if (
            'salon' in self.data and
            'service' in self.data and
            'date' in self.data
        ):
            try:
                salon = Salon.objects.get(id=self.data.get('salon'))
                service = SalonService.objects.get(id=self.data.get('service'))
                date = datetime.strptime(self.data.get('date'), "%Y-%m-%d").date()

                slots = generate_time_slots(
                    salon.opening_time,
                    salon.closing_time,
                    service.duration_minutes
                )

                booked = Booking.objects.filter(
                    salon=salon,
                    date=date,
                    status__in=['pending', 'confirmed']
                )

                available_slots = []

                for slot in slots:
                    slot_start = datetime.combine(date, slot)
                    slot_end = slot_start + timedelta(
                        minutes=service.duration_minutes
                    )

                    conflict = False
                    for b in booked:
                        b_start = datetime.combine(date, b.time)
                        b_end = b_start + timedelta(
                            minutes=b.service.duration_minutes
                        )

                        if slot_start < b_end and slot_end > b_start:
                            conflict = True
                            break

                    if not conflict:
                        available_slots.append(slot)

                self.fields['time'].choices = [
                    (t.strftime('%H:%M'), t.strftime('%I:%M %p'))
                    for t in available_slots
                ]

            except Exception:
                self.fields['time'].choices = []


    def clean(self):
        cleaned_data = super().clean()
        salon = cleaned_data.get('salon')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if salon and date and time:
            booking_datetime = timezone.make_aware(
                datetime.combine(date, time),
                timezone.get_current_timezone()
            )

            if booking_datetime <= timezone.localtime() + timedelta(hours=1):
                raise forms.ValidationError(
                    "Bookings must be at least 1 hours in advance."
                )

            if Booking.objects.filter(
                salon=salon,
                date=date,
                time=time,
                status__in=['pending', 'confirmed']
            ).exists():
                raise forms.ValidationError(
                    "This time slot is already booked."
                )

        return cleaned_data


class RescheduleBookingForm(forms.ModelForm):
    # time = forms.ChoiceField(choices=[])
    time = forms.TimeField(
    input_formats=['%H:%M'],
    required=True
)


    class Meta:
        model = Booking
        fields = ['date', 'time']
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'min': timezone.localdate().isoformat(),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        booking = kwargs.pop('booking')
        super().__init__(*args, **kwargs)

        self.fields['time'].choices = []

        date = self.initial.get('date')
        salon = booking.salon

        if date:
            slots = generate_time_slots(
                salon.opening_time,
                salon.closing_time,
                booking.service.duration_minutes
            )


            booked_times = Booking.objects.filter(
                salon=salon,
                date=date,
                status__in=['pending', 'confirmed']
            ).exclude(
                id=booking.id   
            ).values_list('time', flat=True)

            available_slots = [
                slot for slot in slots if slot not in booked_times
            ]

            self.fields['time'].choices = [
                (t.strftime('%H:%M'), t.strftime('%I:%M %p'))
                for t in available_slots
            ]

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if date and time:
            booking_datetime = timezone.make_aware(
                datetime.combine(date, time),
                timezone.get_current_timezone()
            )

            if booking_datetime <= timezone.localtime() + timedelta(hours=1):
                raise forms.ValidationError(
                    "Rescheduling must be at least 1 hours in advance."
                )

        return cleaned_data


