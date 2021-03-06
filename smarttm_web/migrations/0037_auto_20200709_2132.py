# Generated by Django 2.2.13 on 2020-07-09 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smarttm_web', '0036_requests'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requests',
            name='assigned',
        ),
        migrations.AddField(
            model_name='requests',
            name='status',
            field=models.CharField(choices=[('Assigned', 'Assignment Completed'), ('Cancelled', 'Cancelled'), ('Unassigned', 'Pending Assignment')], default='Unassigned', max_length=20),
            preserve_default=False,
        ),
    ]
