from django.shortcuts import render, redirect
from salons.models import Salon

def home(request):
    salon = None

    if request.user.is_authenticated and request.user.profile.user_type == 'shopkeeper':
        salon = Salon.objects.filter(owner=request.user).first()

        # OPTIONAL: auto-redirect if salon exists
        if salon:
            return redirect('salon_dashboard', salon.id)
        return redirect('salons:create_salon')

    return render(request, 'home.html', {
        'salon': salon
    })
