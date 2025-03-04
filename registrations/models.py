from django.db import models
from django.conf import settings
from events.models import Event, FormField
import uuid

class Registration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Default fields
    name = models.CharField(max_length=255)
    email = models.EmailField()
    
    # UUID for QR codes
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Other fields
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Check-in fields
    check_in_time = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-registration_date']

    def __str__(self):
        return f"{self.name} - {self.event.name} ({self.status})"

    def save(self, *args, **kwargs):
        # Update name and email from form responses if not set
        if not self.name or not self.email:
            for response in self.form_responses.all():
                if response.field.label.lower() == "full name" and not self.name:
                    self.name = response.value
                elif response.field.label.lower() == "email" and not self.email:
                    self.email = response.value
        super().save(*args, **kwargs)

    @property
    def is_checked_in(self):
        return bool(self.check_in_time)

class FormResponse(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='form_responses')
    field = models.ForeignKey(FormField, on_delete=models.CASCADE)
    value = models.TextField(blank=True)
    file = models.FileField(upload_to='form_responses/', blank=True, null=True)

    def __str__(self):
        return f"Response for {self.field.label} in {self.registration}"
