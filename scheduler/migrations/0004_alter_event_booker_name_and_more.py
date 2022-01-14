# Generated by Django 4.0.1 on 2022-01-14 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0003_event_booker_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='booker_name',
            field=models.CharField(editable=False, max_length=64),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(condition=models.Q(('location_type', 1)), fields=('phone_number',), name='unique_number_for_phone_call'),
        ),
    ]
