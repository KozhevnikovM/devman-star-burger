# Generated by Django 3.0.7 on 2021-03-17 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(to='foodcartapp.Product'),
        ),
    ]
