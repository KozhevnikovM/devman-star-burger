# Generated by Django 3.0.7 on 2021-03-31 11:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='created_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Заказ создан'),
        ),
    ]