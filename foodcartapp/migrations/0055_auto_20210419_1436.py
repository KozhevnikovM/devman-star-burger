# Generated by Django 3.0.7 on 2021-04-19 11:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0054_auto_20210419_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderposition',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_positions', to='foodcartapp.Order', verbose_name='Заказ'),
        ),
        migrations.AlterField(
            model_name='orderposition',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_possitions', to='foodcartapp.Product', verbose_name='Товар'),
        ),
    ]
