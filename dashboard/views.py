from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from events.models import Event, FormField
from registrations.models import Registration
from .models import CheckInVolunteer, EventNotification, DashboardSetting
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import json
import qrcode
import base64
from io import BytesIO

def is_staff_check(user):
    return user.is_staff

@user_passes_test(is_staff_check)
def dashboard_home(request):
    events = Event.objects.all().order_by('-date')[:5]
    registrations = Registration.objects.select_related('event').order_by('-registration_date')[:10]
    pending_registrations = Registration.objects.filter(status='pending').count()
    active_volunteers = CheckInVolunteer.objects.filter(is_active=True).count()

    return render(request, 'dashboard/index.html', {
        'events': events,
        'registrations': registrations,
        'pending_registrations': pending_registrations,
        'active_volunteers': active_volunteers,
    })

@user_passes_test(is_staff_check)
def event_list(request):
    events = Event.objects.all().order_by('-date')
    return render(request, 'dashboard/events/list.html', {'events': events})

@user_passes_test(is_staff_check)
def event_registrations(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    registrations = Registration.objects.filter(event=event).order_by('-registration_date')
    stats = {
        'total': registrations.count(),
        'pending': registrations.filter(status='pending').count(),
        'approved': registrations.filter(status='approved').count(),
        'rejected': registrations.filter(status='rejected').count(),
    }
    return render(request, 'dashboard/events/registrations.html', {
        'event': event,
        'registrations': registrations,
        'stats': stats,
    })

@user_passes_test(is_staff_check)
def event_create(request):
    if request.method == 'POST':
        try:
            event = Event.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                date=request.POST.get('date'),
                time=request.POST.get('time'),
                location=request.POST.get('location'),
                max_attendees=request.POST.get('max_attendees'),
                registration_open=request.POST.get('registration_open') == 'on'
            )
            messages.success(request, 'Event created successfully')
            return redirect('dashboard:event_list')
        except Exception as e:
            messages.error(request, f'Error creating event: {str(e)}')
    return render(request, 'dashboard/events/create.html')

@user_passes_test(is_staff_check)
def event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        try:
            event.name = request.POST.get('name')
            event.description = request.POST.get('description')
            event.date = request.POST.get('date')
            event.time = request.POST.get('time')
            event.location = request.POST.get('location')
            event.max_attendees = request.POST.get('max_attendees')
            event.registration_open = request.POST.get('registration_open') == 'on'
            event.save()
            messages.success(request, 'Event updated successfully')
            return redirect('dashboard:event_list')
        except Exception as e:
            messages.error(request, f'Error updating event: {str(e)}')
    return render(request, 'dashboard/events/edit.html', {'event': event})

@user_passes_test(is_staff_check)
def registration_list(request):
    registrations = Registration.objects.all().select_related('event').order_by('-registration_date')
    return render(request, 'dashboard/registrations/list.html', {
        'registrations': registrations
    })

@user_passes_test(is_staff_check)
def registration_detail(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)
    responses = registration.form_responses.select_related('field')
    return render(request, 'dashboard/registrations/detail.html', {
        'registration': registration,
        'responses': responses,
    })

@user_passes_test(is_staff_check)
def approve_registration(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)
    if request.method == 'POST':
        registration.status = 'approved'
        registration.save()
        messages.success(request, 'Registration approved successfully')
        return redirect('dashboard:registration_detail', registration_id=registration.id)

@user_passes_test(is_staff_check)
def reject_registration(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)
    if request.method == 'POST':
        registration.status = 'rejected'
        registration.save()
        messages.success(request, 'Registration rejected successfully')
        return redirect('dashboard:registration_detail', registration_id=registration.id)

@user_passes_test(is_staff_check)
def send_approval_email(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id, status='approved')
    
    # Generate QR code with UUID
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(registration.uuid))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert QR code to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    context = {
        'registration': registration,
        'event': registration.event,
        'qr_code_base64': qr_code_base64
    }
    
    email_body = render_to_string('emails/registration_approved.html', context)
    
    send_mail(
        subject=f"Your Registration for {registration.event.name} is Approved!",
        message=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[registration.email],
        html_message=email_body
    )
    
    messages.success(request, f"Approval email with QR code sent to {registration.email}")
    return redirect('dashboard:registration_detail', registration_id=registration.id)

@user_passes_test(is_staff_check)
def send_rejection_email(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id, status='rejected')
    
    context = {
        'registration': registration,
        'event': registration.event,
    }
    
    email_body = render_to_string('emails/registration_rejected.html', context)
    
    send_mail(
        subject=f"Registration Update for {registration.event.name}",
        message=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[registration.email],
        html_message=email_body
    )
    
    messages.success(request, f"Rejection email sent to {registration.email}")
    return redirect('dashboard:registration_detail', registration_id=registration.id)
