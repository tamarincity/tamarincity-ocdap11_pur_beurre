# Generated by Django 4.0.3 on 2022-08-12 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customer_otp_customer_otp_validity_end_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='otp_validity_end_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
