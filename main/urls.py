from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('redirect_to_login/', views.redirect_to_login, name='redirect_to_login'),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.main, name="main"),
    path("load_balance/", views.load_balance, name="load_balance"),
    path("profile_edit/", views.profile_edit, name="profile_edit"),
    path("pay/<int:booking_id>/", views.pay_booking, name="pay_booking"),
]
