# Generated by Django 4.2.2 on 2023-06-24 04:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0004_customer_username'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='account_id',
            new_name='account_number',
        ),
    ]
