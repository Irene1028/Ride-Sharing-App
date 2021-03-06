# Generated by Django 3.0.3 on 2020-02-08 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_auto_20200207_2220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='vehicle_capacity',
            field=models.PositiveIntegerField(blank=True, default=1, null=True),
        ),
        migrations.AlterField(
            model_name='vehicleinfo',
            name='num_of_passengers',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
