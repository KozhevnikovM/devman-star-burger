# Generated by Django 3.0.7 on 2021-03-17 11:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_order_products'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='products',
        ),
    ]
