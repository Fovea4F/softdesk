# Generated by Django 5.0.1 on 2024-03-29 08:18

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("softdesk", "0022_comment_in_charge_customuser_created_date_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comment",
            name="in_charge",
        ),
    ]
