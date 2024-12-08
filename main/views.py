from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoadBalanceForm, ProfileEditForm, UserRegistrationForm
from .models import Booking, UserProfile
from django.db.models import F
import sqlite3
from datetime import datetime

@login_required()

def redirect_to_login(request):
    if request.user.is_authenticated: 
        return redirect("main")
    return redirect("login")  


@login_required()
def main(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    bookings = Booking.objects.filter(user=request.user)
    # Kullanıcının bakiyesini almak için yeni fonksiyonu kullanıyoruz
    balance = get_user_balance(request.user)

    # db_path = "C:\\Users\\Salih Can\\Desktop\\parking.db"
    db_path = "C:\\Users\\İzzet\\Downloads\\plaka_projeKerem\\plaka_proje\\parking.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # parking.db'den plaka, giriş zamanı, çıkış zamanı ve ücret bilgilerini al
    cursor.execute("SELECT plate, entry_time, exit_time, fee FROM parking")
    records = cursor.fetchall()
    print("Kayıtlar:", records)

    conn.close()


    # Her bir kayıt için işlemleri yap
    for plate, entry_time, exit_time, fee in records:
        profiles = UserProfile.objects.filter(car_plate=plate)
        if profiles.exists():
            for profile in profiles:
                user = profile.user  # User modelinden kullanıcıyı al

                # Tarih ve zaman formatını düzelt
                start_time = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
                if exit_time:  # exit_time varsa işle
                    end_time = datetime.strptime(exit_time, "%Y-%m-%d %H:%M:%S")
                else:
                    end_time = None  


                # Booking tablosunda ilgili rezervasyonu kontrol et ve varsa geç.
                existing_booking = Booking.objects.filter(
                    user=user,
                    car_plate=plate,
                    start_time=start_time,
                    end_time=end_time,
                ).exists()

                if not existing_booking:

                    Booking.objects.create(
                        user=user,
                        car_plate=plate,
                        start_time=start_time,
                        end_time=end_time,
                        amount=fee,
                        paid=False,
                    )
                    print(f"Yeni rezervasyon oluşturuldu: {plate}")
                else:
                    print(f"Zaten mevcut olan rezervasyon: {plate}")
        else:
            print(f"Plaka {plate} için kullanıcı bulunamadı.")

    return render(request, "main.html", {"balance": balance, "bookings": bookings})


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            # UserProfile'a ek bilgiler ekleniyor
            car_plate = form.cleaned_data["car_plate"]
            UserProfile.objects.create(user=user, car_plate=car_plate)

            return redirect("login")
    else:
        form = UserRegistrationForm()
    return render(request, "register.html", {"user_form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("main") 
    return render(request, "login.html")


# views.py
from .models import UserProfile


def get_user_balance(user):
    """Kullanıcının bakiyesini döndüren yardımcı fonksiyon"""
    try:
        profile = UserProfile.objects.get(user=user)
        return profile.balance
    except UserProfile.DoesNotExist:
        return 0 


@login_required
def pay_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    profile = get_object_or_404(UserProfile, user=request.user)

    if profile.balance >= booking.amount:
        UserProfile.objects.filter(user=request.user).update(
            balance=F("balance") - booking.amount
        )

        # Güncel kullanıcı profili alınıyor
        profile.refresh_from_db()

        booking.paid = True
        booking.save()
        return redirect("main")
    else:
        # Yetersiz bakiye mesajı
        return redirect("main")


def logout_view(request):
    logout(request)  
    request.session.flush()  
    return redirect("login")


@login_required()
def load_balance(request):
    if request.method == "POST":
        form = LoadBalanceForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            UserProfile.objects.filter(user=request.user).update(
                balance=F("balance") + amount
            )

            
            profile = get_object_or_404(UserProfile, user=request.user)
            return redirect("main")
    else:
        form = LoadBalanceForm()
    return render(request, "load_balance.html", {"form": form})


@login_required()
def profile_edit(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        form = ProfileEditForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            # Kullanıcı bilgilerini güncelle
            request.user.first_name = form.cleaned_data["first_name"]
            request.user.last_name = form.cleaned_data["last_name"]
            request.user.save()

            # UserProfile bilgilerini güncelle
            profile.car_plate = form.cleaned_data["car_plate"]
            profile.save()

            return redirect("main")
    else:
        form = ProfileEditForm(instance=profile, user=request.user)
    return render(request, "profile_edit.html", {"profile_form": form})


"""
@login_required
def pay_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.balance >= booking.amount:
        profile.balance -= booking.amount
        profile.save()
        booking.paid = True
        booking.save()
    return redirect("main")
    
    """
