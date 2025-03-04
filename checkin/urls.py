from django.urls import path
from . import views

app_name = 'checkin'

urlpatterns = [
    path('', views.scanner, name='scanner'),
    path('lookup/', views.lookup_registration, name='lookup'),
    path('process/<int:registration_id>/', views.process_checkin, name='process'),
]