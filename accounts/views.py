from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth.views import LoginView
from salons.models import Salon
from django.urls import reverse
from django.contrib.auth import logout


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

class RoleBasedLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user

        if user.profile.user_type == 'shopkeeper':
            salon = Salon.objects.filter(owner=user).first()

            if salon:
                return reverse(
                    'salons:salon_dashboard',
                    kwargs={'salon_id': salon.id}
                )

            return reverse('salons:create_salon')

        # customer
        return '/'
    


def logout_view(request):
    logout(request)
    return redirect('/')

