# Generated by Django 3.x on 2025-03-16

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0006_merge_20250304_0803'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailCommunication',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('email_type', models.CharField(choices=[('registration_approved', 'Registration Approved'), ('registration_rejected', 'Registration Rejected'), ('event_update', 'Event Update')], max_length=50)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_communications', to='auth.user')),
            ],
            options={
                'unique_together': {('user', 'email_type')},
            },
        ),
    ]