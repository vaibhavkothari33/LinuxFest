from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0003_add_registration_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registration',
            name='qr_code',
        ),
    ]