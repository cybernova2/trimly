from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(
        choices=(('customer', 'Customer'), ('shopkeeper', 'Shopkeeper'))
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            user.profile.user_type = self.cleaned_data['user_type']
            user.profile.save()

        return user
