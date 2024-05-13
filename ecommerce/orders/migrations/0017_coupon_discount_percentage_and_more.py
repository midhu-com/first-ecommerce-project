# Generated by Django 5.0.2 on 2024-05-13 06:11

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0004_alter_category_slug'),
        ('orders', '0016_alter_orderproduct_order'),
        ('store', '0004_reviewrating'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='discount_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name='coupon',
            name='maximum_discount_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='coupon',
            name='minimum_purchase_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.CreateModel(
            name='CategoryOffers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Default Offer Name', max_length=100)),
                ('discount_percentage', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MaxValueValidator(50)])),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('category', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='offer', to='category.category')),
            ],
        ),
        migrations.CreateModel(
            name='ProductOffers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Default Offer Name', max_length=100)),
                ('discount_percentage', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MaxValueValidator(50)])),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='offer', to='store.product')),
            ],
        ),
    ]
