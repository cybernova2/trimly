from django import forms
from .models import Salon, ServiceCategory, SalonService

class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = [
            'name',
            'address',
            'phone',
            'opening_time',
            'closing_time',
        ]
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
        }
class ServiceForm(forms.ModelForm):

    service = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.all(),
        empty_label="Select Service"
    )

    class Meta:
        model = SalonService
        fields = [
            'service',
            'duration_minutes',
            'price'
        ]

        

