from django.contrib import admin
from .models import CheckInVolunteer, EventNotification, DashboardSetting

@admin.register(CheckInVolunteer)
class CheckInVolunteerAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'

@admin.register(EventNotification)
class EventNotificationAdmin(admin.ModelAdmin):
    list_display = ('event', 'notification_type', 'subject', 'is_active', 'created_at')
    list_filter = ('notification_type', 'is_active', 'event')
    search_fields = ('subject', 'message', 'template')
    date_hierarchy = 'created_at'

@admin.register(DashboardSetting)
class DashboardSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'created_at', 'updated_at')
    search_fields = ('key', 'description')
    readonly_fields = ('created_at', 'updated_at')
