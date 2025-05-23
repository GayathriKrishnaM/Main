# Generated by Django 5.1.5 on 2025-03-09 23:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0017_tablereservation_date_time"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="menu",
            name="inventory",
        ),
        migrations.AlterField(
            model_name="inventory",
            name="menu",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="inventories",
                to="management.menu",
            ),
        ),
    ]
