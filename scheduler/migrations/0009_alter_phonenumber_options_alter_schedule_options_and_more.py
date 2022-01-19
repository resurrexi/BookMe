# Generated by Django 4.0.1 on 2022-01-19 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0008_phonenumber_remove_schedule_schedule_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='phonenumber',
            options={'verbose_name': 'phone number', 'verbose_name_plural': 'phone number'},
        ),
        migrations.AlterModelOptions(
            name='schedule',
            options={'verbose_name': 'availability schedule', 'verbose_name_plural': 'availability schedule'},
        ),
        migrations.AlterField(
            model_name='event',
            name='booker_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name='event',
            name='booker_name',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AlterField(
            model_name='event',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='location_type',
            field=models.CharField(choices=[('PHONE', 'Phone Call'), ('GMEET', 'Google Meet')], default='PHONE', max_length=8),
        ),
    ]
