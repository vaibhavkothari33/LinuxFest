from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard home
    path('', views.dashboard_home, name='index'),

    # Event management
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:event_id>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:event_id>/registrations/', views.event_registrations, name='event_registrations'),
    path('events/<int:event_id>/form-builder/', views.form_builder, name='form_builder'),
    path('events/<int:event_id>/form-builder/reorder/', views.reorder_fields, name='reorder_fields'),
    path('events/<int:event_id>/export/', views.export_registrations, name='export_registrations'),
    
    # Form field management
    path('fields/create/<int:event_id>/', views.form_field_create, name='field_create'),
    path('fields/<int:field_id>/edit/', views.form_field_edit, name='field_edit'),
    path('fields/<int:field_id>/delete/', views.form_field_delete, name='field_delete'),
    
    # Registration management
    path('registrations/', views.registration_list, name='registration_list'),
    path('registrations/<int:registration_id>/', views.registration_detail, name='registration_detail'),
    path('registrations/<int:registration_id>/approve/', views.approve_registration, name='approve_registration'),
    path('registrations/<int:registration_id>/reject/', views.reject_registration, name='reject_registration'),
    path('registrations/<int:registration_id>/send_approval_email/', views.send_approval_email, name='send_approval_email'),
    path('registrations/<int:registration_id>/send_rejection_email/', views.send_rejection_email, name='send_rejection_email'),
]