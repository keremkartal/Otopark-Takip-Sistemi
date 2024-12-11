import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, Booking 
from django.contrib.auth import get_user_model
from django.forms import Form
from .forms import LoadBalanceForm
from decimal import Decimal 
from django.test import Client
from unittest.mock import patch, MagicMock
from datetime import datetime

@pytest.mark.django_db
def test_redirect_to_login_authenticated(client):

    user = User.objects.create_user(username="testuser", password="testpass")
    client.login(username="testuser", password="testpass") 
    response = client.get(reverse("redirect_to_login"))
    assert response.status_code == 302
    assert response.url == reverse("main")

@pytest.mark.django_db
def test_redirect_to_login_unauthenticated(client):
    response = client.get(reverse("redirect_to_login"))
    assert response.status_code == 302
    assert response.url == reverse("login")


@pytest.mark.django_db
def test_load_balance_get(client):
    user = User.objects.create_user(username="testuser", password="testpass")
    client.login(username="testuser", password="testpass")

    # GET isteği gönder
    response = client.get(reverse('load_balance'))

    # Doğru template'in kullanıldığını doğrula
    assert response.status_code == 200
    assert "form" in response.context





@pytest.mark.django_db
def test_load_balance_post_invalid(client):
    
    user = User.objects.create_user(username="testuser", password="testpass")
    client.login(username="testuser", password="testpass")

    # POST isteği gönder (geçersiz form verisi)
    data = {"amount": "invalid"}  
    response = client.post(reverse('load_balance'), data)

    # Formun tekrar render edilmesi
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors


@pytest.mark.django_db
def test_pay_booking_valid(client):
   
    user = User.objects.create_user(username="testuser", password="testpass")
    client.login(username="testuser", password="testpass")

    
    profile = UserProfile.objects.create(user=user, balance=Decimal('200.00'))

    
    booking = Booking.objects.create(
        user=user, 
        amount=Decimal('100.00'), 
        paid=False,
        start_time="10:00:00",  
        end_time="12:00:00"     
    )

    # POST isteği gönder
    response = client.get(reverse('pay_booking', kwargs={'booking_id': booking.id}))

    # Kullanıcının bakiyesinin doğru şekilde güncellendiğini doğrula
    profile.refresh_from_db()
    assert profile.balance == Decimal('100.00')

    # Rezervasyonun ödendi olarak işaretlendiğini doğrula
    booking.refresh_from_db()
    assert booking.paid is True

    # Ana sayfaya yönlendirildiğini kontrol et
    assert response.status_code == 302
    assert response.url == reverse('main')


@pytest.mark.django_db
def test_pay_booking_invalid_balance(client):
    
    user = User.objects.create_user(username="testuser", password="testpass")
    client.login(username="testuser", password="testpass")

    # Kullanıcı profili oluştur (yetersiz bakiye)
    profile = UserProfile.objects.create(user=user, balance=Decimal('50.00'))

    
    booking = Booking.objects.create(
        user=user, 
        amount=Decimal('100.00'), 
        paid=False,
        start_time="10:00:00",  # Buraya bir zaman değeri ekleyin
        end_time="12:00:00"     # Buraya bir zaman değeri ekleyin
    )

    # POST isteği gönder
    response = client.get(reverse('pay_booking', kwargs={'booking_id': booking.id}))

    # Kullanıcının bakiyesi değişmediğini doğrula
    profile.refresh_from_db()
    assert profile.balance == Decimal('50.00')

    # Rezervasyonun ödendi olarak işaretlenmediğini doğrula
    booking.refresh_from_db()
    assert booking.paid is False

    # Ana sayfaya yönlendirildiğini kontrol et
    assert response.status_code == 302
    assert response.url == reverse('main')


@pytest.mark.django_db
def test_pay_booking_invalid_booking(client):
    
    user = User.objects.create_user(username="testuser", password="testpass")
    client.login(username="testuser", password="testpass")

    
    profile = UserProfile.objects.create(user=user, balance=Decimal('200.00'))

    # Geçersiz rezervasyon ID'si
    invalid_booking_id = 9999  # Geçersiz ID

    # POST isteği gönder
    response = client.get(reverse('pay_booking', kwargs={'booking_id': invalid_booking_id}))

    # 404 hata sayfasının gösterilmesi gerektiğini doğrula
    assert response.status_code == 404



from .views import get_user_balance

@pytest.mark.django_db
def test_get_user_balance():
   
    user = User.objects.create_user(username="testuser", password="testpass")
    
   
    profile = UserProfile.objects.create(user=user, balance=Decimal('100.00'))

    
    balance = get_user_balance(user)

    # Bakiyenin doğru olduğunu doğrula
    assert balance == Decimal('100.00')

@pytest.mark.django_db
def test_get_user_balance_no_profile():
    
    user = User.objects.create_user(username="testuser", password="testpass")

    
    balance = get_user_balance(user)

   
    assert balance == 0


@pytest.mark.django_db
def test_profile_edit():
    
    user = User.objects.create_user(username="testuser", password="testpass")
    profile = UserProfile.objects.create(user=user, balance=Decimal('100.00'), car_plate="34XYZ34")

    # Kullanıcıyı oturum açtır
    client = Client()
    client.login(username="testuser", password="testpass")

    
    new_first_name = "NewFirstName"
    new_last_name = "NewLastName"
    new_car_plate = "45ABC45"

    # Profile edit sayfasına POST isteği gönder
    response = client.post(reverse("profile_edit"), {
        "first_name": new_first_name,
        "last_name": new_last_name,
        "car_plate": new_car_plate,
        "balance": Decimal('100.00')  
    })

    # Kullanıcı bilgilerini ve profil bilgilerini güncellenip güncellenmediğini kontrol et
    user.refresh_from_db()
    profile.refresh_from_db()

    # Form başarılı şekilde gönderildiyse yönlendirme yapılmalı
    assert response.status_code == 302  
    assert user.first_name == new_first_name
    assert user.last_name == new_last_name
    assert profile.car_plate == new_car_plate

@pytest.mark.django_db
def test_profile_edit_invalid_form():
 
    user = User.objects.create_user(username="testuser", password="testpass")
    profile = UserProfile.objects.create(user=user, balance=Decimal('100.00'), car_plate="34XYZ34")

    # Kullanıcıyı oturum açtır
    client = Client()
    client.login(username="testuser", password="testpass")

    # Hatalı form verisi (örneğin, geçersiz araç plakası)
    invalid_car_plate = "INVALID_PLATE_TOO_LONG"

    # Profile edit sayfasına POST isteği gönder
    response = client.post(reverse("profile_edit"), {
        "first_name": "NewFirstName",
        "last_name": "NewLastName",
        "car_plate": invalid_car_plate,
        "balance": Decimal('100.00')
    })

    # Form geçerli değil, formun tekrar render edilmesi gerekir
    assert response.status_code == 200
    assert "profile_form" in response.context
    assert response.context["profile_form"].errors

