from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.exceptions import ValidationError


class LoadBalanceForm(forms.Form):
    card_number = forms.CharField(max_length=16)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(label="Ad", max_length=30, required=False)
    last_name = forms.CharField(label="Soyad", max_length=30, required=False)
    car_plate = forms.CharField(label="Araç Plakası", max_length=20, required=False)

    class Meta:
        model = UserProfile
        fields = ["balance"]  # Bakiye düzenlemesi için bu alan bırakılıyor

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # User objesini alıyoruz
        super().__init__(*args, **kwargs)
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["car_plate"].initial = user.userprofile.car_plate


class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(label="Ad", max_length=30)
    last_name = forms.CharField(label="Soyad", max_length=30)
    car_plate = forms.CharField(label="Araç Plakası", max_length=20)

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

    def clean_car_plate(self):
        car_plate = self.cleaned_data.get("car_plate")
        if UserProfile.objects.filter(car_plate=car_plate).exists():
            raise ValidationError(
                "Bu araç plakası zaten kayıtlı. Lütfen farklı bir plaka girin."
            )
        return car_plate
