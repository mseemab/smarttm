# Generated by Django 2.2 on 2019-05-05 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smarttm_web', '0018_participation_club'),
    ]

    operations = [
        migrations.CreateModel(
            name='Summary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tt_count', models.IntegerField(default=0)),
                ('speeches_count', models.IntegerField(default=0)),
                ('basic_role_count', models.IntegerField(default=0)),
                ('adv_role_count', models.IntegerField(default=0)),
                ('evaluation_count', models.IntegerField(default=0)),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='smarttm_web.Member')),
            ],
        ),
    ]