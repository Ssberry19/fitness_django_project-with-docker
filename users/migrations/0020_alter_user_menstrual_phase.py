# Generated by Django 4.2.1 on 2025-06-09 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_rename_cycle_record_user_menstrual_phase_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='menstrual_phase',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
