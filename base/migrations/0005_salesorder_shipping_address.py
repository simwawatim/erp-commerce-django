# Generated by Django 5.2.1 on 2025-07-04 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_customer_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesorder',
            name='shipping_address',
            field=models.TextField(blank=True, null=True),
        ),
    ]
