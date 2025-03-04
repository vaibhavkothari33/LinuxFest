from django.shortcuts import render, get_object_or_404
from .models import Registration

def registration_confirmation(request, registration_id):
    registration = get_object_or_404(Registration, pk=registration_id)
    return render(request, 'registrations/confirmation.html', {'registration': registration})
