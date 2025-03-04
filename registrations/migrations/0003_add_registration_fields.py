from django.db import migrations, models
import uuid


def migrate_name_email(apps, schema_editor):
    Registration = apps.get_model('registrations', 'Registration')
    FormResponse = apps.get_model('registrations', 'FormResponse')
    
    for registration in Registration.objects.all():
        # Get name and email from form responses
        name = None
        email = None
        for response in FormResponse.objects.filter(registration=registration):
            if response.field.label.lower() == "full name":
                name = response.value
            elif response.field.label.lower() == "email":
                email = response.value
        
        # Update registration with found values
        if name or email:
            registration.name = name or "Unknown"
            registration.email = email or "unknown@example.com"
            registration.save()


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0002_alter_registration_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='name',
            field=models.CharField(default='Unknown', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='email',
            field=models.EmailField(default='unknown@example.com', max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='registration',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.RunPython(migrate_name_email, migrations.RunPython.noop),
    ]