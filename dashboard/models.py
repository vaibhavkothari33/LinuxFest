from django.db import models
from django.contrib.auth.models import User
from events.models import Event

class CheckInVolunteer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    events = models.ManyToManyField(Event, related_name='check_in_volunteers')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    class Meta:
        verbose_name = 'Check-in Volunteer'
        verbose_name_plural = 'Check-in Volunteers'

class EventNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('registration', 'New Registration'),
        ('cancellation', 'Registration Cancellation'),
        ('reminder', 'Event Reminder'),
        ('update', 'Event Update'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    template = models.TextField(help_text='Use {{variables}} for dynamic content')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event.name} - {self.get_notification_type_display()}"

    class Meta:
        ordering = ['-created_at']

class DashboardSetting(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = 'Dashboard Setting'
        verbose_name_plural = 'Dashboard Settings'
