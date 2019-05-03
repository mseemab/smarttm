# Generated by Django 2.2 on 2019-05-03 07:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smarttm_web', '0014_auto_20190502_1726'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='status',
        ),
        migrations.AlterField(
            model_name='meeting',
            name='meeting_date',
            field=models.DateTimeField(verbose_name='Meeting Date'),
        ),
        migrations.AlterField(
            model_name='member',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
