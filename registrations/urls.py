from django.urls import path
from . import views

app_name = 'registrations'

urlpatterns = [
    path('confirmation/<int:registration_id>/', views.registration_confirmation, name='confirmation'),
]