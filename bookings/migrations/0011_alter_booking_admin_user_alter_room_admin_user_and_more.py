# Generated by Django 4.0.6 on 2023-05-15 14:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bookings', '0010_alter_room_admin_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='admin_user',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, related_name='bookings_admin', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='room',
            name='admin_user',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, related_name='room_admin', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='room',
            name='image',
            field=models.ImageField(blank=True, upload_to='rooms/'),
        ),
    ]
