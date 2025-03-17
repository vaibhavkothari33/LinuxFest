from django.urls import path
from . import views

app_name = 'registrations'

urlpatterns = [
    path('<uuid:registration_uuid>/rsvp/decline/', views.rsvp_decline, name='rsvp_decline'),
    path('<int:registration_id>/confirmation/', views.confirmation, name='confirmation'),
    path('<uuid:registration_uuid>/decline/success/', views.decline_success, name='decline_success'),
]