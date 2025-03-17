from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Registration, EmailCommunication
from django.contrib.auth.models import User

def decline_success(request, registration_uuid):
    """
    Display the success page after declining an RSVP.
    """
    registration = get_object_or_404(Registration, uuid=registration_uuid)
    return render(request, 'registrations/decline_success.html', {
        'registration': registration,
        'event': registration.event,
    })

def rsvp_decline(request, registration_uuid):
    """
    Handle RSVP decline for a registration with confirmation.
    """
    registration = get_object_or_404(Registration, uuid=registration_uuid)

    if request.method == 'POST':
        if registration.status != 'approved':
            return JsonResponse({'error': 'Only approved registrations can RSVP.'}, status=400)
        
        # Update the status to 'declined'
        registration.status = 'declined'
        registration.save()
        
        messages.success(request, 'Your RSVP has been updated. We are sorry to hear you won’t be attending.')
        return redirect('registrations:decline_success', registration_uuid=registration.uuid)

    return render(request, 'registrations/decline.html', {
        'registration': registration,
        'event': registration.event,
    })

def confirmation(request, registration_id):
    """
    Display the confirmation page for a registration and check email status.
    """
    registration = get_object_or_404(Registration, id=registration_id)
    return render(request, 'registrations/confirmation.html', {
        'registration': registration,
        'event': registration.event,
    })
