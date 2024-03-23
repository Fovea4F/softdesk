# Generated by Django 5.0.1 on 2024-03-13 16:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("softdesk", "0016_issue_status_alter_issue_issue_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="issue",
            name="assigned_contributor",
            field=models.ForeignKey(
                default=2,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="issues_assigned",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="issue",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="issues_authored",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
