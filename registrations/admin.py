from django.contrib import admin

# Register your models here.
from .models import Registration, FormResponse, EmailCommunication

admin.site.register(Registration)
admin.site.register(FormResponse)
admin.site.register(EmailCommunication)