# Generated by Django 2.2 on 2019-05-02 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smarttm_web', '0013_member_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='meeting_date',
            field=models.DateField(verbose_name='Meeting Date'),
        ),
    ]
