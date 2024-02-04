# Generated by Django 4.2.2 on 2023-07-01 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0008_remove_customer_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='loan',
            name='monthly_payment',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='loan',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='loan',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('approved', 'approved'), ('rejected', 'rejected'), ('closed', 'closed')], max_length=50),
        ),
    ]
