# Generated by Django 3.0.7 on 2021-03-31 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_auto_20210331_1426'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('C', 'Наличными при доставке'), ('O', 'Картой онлайн')], default='C', max_length=2, verbose_name='Способ оплаты'),
        ),
    ]