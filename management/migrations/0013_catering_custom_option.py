# Generated by Django 5.1.5 on 2025-03-07 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0012_remove_catering_advance_amount_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="catering",
            name="custom_option",
            field=models.CharField(
                blank=True, help_text="Custom idea if any", max_length=255
            ),
        ),
    ]
