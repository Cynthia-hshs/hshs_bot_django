from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("forgot-password/", views.forgot_password_view, name="forgot_password"),
    path("set-password/", views.set_password_view, name="set_password"),
    path("guest-login/", views.guest_login, name="guest_login"),
    path("guest-logout/", views.guest_logout, name="guest_logout"),
]
