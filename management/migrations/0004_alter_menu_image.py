# Generated by Django 5.1.5 on 2025-02-13 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management", "0003_alter_eventplan_menu_items"),
    ]

    operations = [
        migrations.AlterField(
            model_name="menu",
            name="image",
            field=models.ImageField(
                default="menu_images/default.jpg", upload_to="media/menu_images/"
            ),
        ),
    ]
