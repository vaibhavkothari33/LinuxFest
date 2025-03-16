from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Registration

@require_POST
def rsvp_decline(request, registration_uuid):
    """
    Handle RSVP decline for a registration.
    """
    registration = get_object_or_404(Registration, uuid=registration_uuid)
    
    if registration.status != 'approved':
        return JsonResponse({'error': 'Only approved registrations can RSVP.'}, status=400)
    
    # Update the status to 'declined'
    registration.status = 'declined'
    registration.save()
    
    messages.success(request, 'Your RSVP has been updated. We are sorry to hear you won’t be attending.')
    return JsonResponse({'success': 'RSVP updated successfully.'})

def confirmation(request, registration_id):
    """
    Display the confirmation page for a registration.
    """
    registration = get_object_or_404(Registration, id=registration_id)
    return render(request, 'registrations/confirmation.html', {
        'registration': registration,
        'event': registration.event,
    })
