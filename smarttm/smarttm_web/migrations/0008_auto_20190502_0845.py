# Generated by Django 2.2 on 2019-05-02 03:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smarttm_web', '0007_auto_20190502_0840'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_admin',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_staff',
        ),
    ]
