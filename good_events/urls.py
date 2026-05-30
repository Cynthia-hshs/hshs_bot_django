from django.urls import path

from . import views

app_name = "good_events"

urlpatterns = [
    path("", views.index, name="index"),
]
