from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from registrations.models import Registration
from dashboard.models import CheckInVolunteer
from django.utils import timezone
import json

def is_check_in_staff(user):
    """Check if user is staff or check-in volunteer"""
    return user.is_staff or hasattr(user, 'check_in_volunteer')

@user_passes_test(is_check_in_staff)
def scanner(request):
    """QR Code scanner interface"""
    return render(request, 'checkin/scanner.html')

@user_passes_test(is_check_in_staff)
def lookup_registration(request):
    """Look up registration details from QR code"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        uuid = data.get('uuid')
        
        if not uuid:
            return JsonResponse({'error': 'UUID is required'}, status=400)
        
        registration = get_object_or_404(Registration, uuid=uuid)
        
        # Check if already checked in
        if registration.check_in_time:
            return JsonResponse({
                'status': 'error',
                'message': 'Already checked in',
                'check_in_time': registration.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                'registration': {
                    'id': registration.id,
                    'name': registration.name,
                    'email': registration.email,
                    'event': registration.event.name,
                    'status': registration.status,
                }
            })
        
        # Check if registration is approved
        if registration.status != 'approved':
            return JsonResponse({
                'status': 'error',
                'message': f'Registration status is {registration.status}',
                'registration': {
                    'id': registration.id,
                    'name': registration.name,
                    'email': registration.email,
                    'event': registration.event.name,
                    'status': registration.status,
                }
            })
        
        return JsonResponse({
            'status': 'success',
            'message': 'Registration found',
            'registration': {
                'id': registration.id,
                'name': registration.name,
                'email': registration.email,
                'event': registration.event.name,
                'status': registration.status,
            }
        })
        
    except Registration.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid registration'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@user_passes_test(is_check_in_staff)
def process_checkin(request, registration_id):
    """Process the actual check-in after confirmation"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        registration = get_object_or_404(Registration, id=registration_id)
        
        # Double-check if already checked in
        if registration.check_in_time:
            return JsonResponse({
                'status': 'error',
                'message': 'Already checked in',
                'check_in_time': registration.check_in_time.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Double-check if registration is approved
        if registration.status != 'approved':
            return JsonResponse({
                'status': 'error',
                'message': f'Registration status is {registration.status}'
            })
        
        # Process check-in
        registration.check_in_time = timezone.now()
        registration.checked_in_by = request.user
        registration.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Check-in successful',
            'check_in_time': registration.check_in_time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Registration.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid registration'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)