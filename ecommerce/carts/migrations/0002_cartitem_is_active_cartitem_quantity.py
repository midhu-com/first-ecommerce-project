# Generated by Django 5.0.2 on 2024-03-25 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
