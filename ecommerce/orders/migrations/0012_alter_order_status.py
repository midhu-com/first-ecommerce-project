# Generated by Django 5.0.2 on 2024-05-09 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_order_discount_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Accepted', 'Accepted'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned'), ('Delivered', 'Delivered')], default='New', max_length=20),
        ),
    ]
