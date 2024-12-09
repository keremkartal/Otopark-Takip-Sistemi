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
def test_main_view():
    
    user = User.objects.create_user(username="testuser", password="testpass")
    profile = UserProfile.objects.create(user=user, balance=Decimal('100.00'), car_plate="34XYZ34")

    # Kullanıcıyı oturum açtır
    client = Client()
    client.login(username="testuser", password="testpass")

    
    db_records = [
        ("34XYZ34", "2024-12-01 10:00:00", "2024-12-01 12:00:00", Decimal('20.00')),
        ("34XYZ34", "2024-12-02 14:00:00", None, Decimal('25.00'))
    ]
    
    # SQLite bağlantısı ve cursor mocklama
    with patch("sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = db_records
        
        # View'a GET isteği gönder
        response = client.get(reverse("main"))

    
    assert response.status_code == 200
    assert "balance" in response.context
    assert response.context["balance"] == Decimal('100.00')

    # Veritabanındaki rezervasyonları kontrol et
    bookings = Booking.objects.filter(user=user)
    assert bookings.count() == 2

    # İlk rezervasyonun doğru şekilde oluşturulup oluşturulmadığını kontrol et
    booking1 = bookings.first()
    assert booking1.car_plate == "34XYZ34"
    assert booking1.start_time == datetime(2024, 12, 1, 10, 0)
    assert booking1.end_time == datetime(2024, 12, 1, 12, 0)
    assert booking1.amount == Decimal('20.00')
    assert booking1.paid == False

    # İkinci rezervasyonun doğru şekilde oluşturulup oluşturulmadığını kontrol et
    booking2 = bookings.last()
    assert booking2.car_plate == "34XYZ34"
    assert booking2.start_time == datetime(2024, 12, 2, 14, 0)
    assert booking2.end_time is None  
    assert booking2.amount == Decimal('25.00')
    assert booking2.paid == False