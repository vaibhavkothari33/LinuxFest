from django.db import models
from django.contrib.auth.models import User
import json

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    max_attendees = models.PositiveIntegerField()
    registration_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_available_slots(self):
        return self.max_attendees - self.registration_set.count()

    class Meta:
        ordering = ['-date', '-time']

class FormField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('email', 'Email'),
        ('number', 'Number'),
        ('choice', 'Choice'),
        ('date', 'Date'),
        ('file', 'File'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='form_fields')
    label = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(default=False)
    placeholder = models.CharField(max_length=200, blank=True)
    choices = models.TextField(blank=True, help_text='JSON array of choices for choice fields (e.g., ["Red", "Green", "Blue"])')
    order = models.PositiveIntegerField(default=0)
    conditional_field = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dependent_fields'
    )
    conditional_value = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.event.name} - {self.label}"

    def get_choices(self):
        if not self.choices:
            return []
        try:
            return json.loads(self.choices)
        except json.JSONDecodeError:
            return []

    class Meta:
        ordering = ['order']
        unique_together = ['event', 'order']
