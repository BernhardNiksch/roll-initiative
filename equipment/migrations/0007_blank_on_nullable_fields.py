# Generated by Django 3.1.6 on 2021-04-23 20:08

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0006_money_blank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adventuringgear',
            name='length',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='adventuringgear',
            name='quantity',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='armor',
            name='armor_class',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(20)]),
        ),
        migrations.AlterField(
            model_name='characteradventuringgear',
            name='length',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='characteradventuringgear',
            name='quantity',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
