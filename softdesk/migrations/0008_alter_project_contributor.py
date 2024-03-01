# Generated by Django 5.0.1 on 2024-02-13 23:47

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("softdesk", "0007_alter_project_contributor"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="contributor",
            field=models.ManyToManyField(
                blank=True, related_name="contributors", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
