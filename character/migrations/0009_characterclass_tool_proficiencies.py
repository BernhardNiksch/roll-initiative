# Generated by Django 3.1.6 on 2021-04-12 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0004_money_mixin'),
        ('character', '0008_money_mixin'),
    ]

    operations = [
        migrations.AddField(
            model_name='characterclass',
            name='tool_proficiencies',
            field=models.ManyToManyField(blank=True, to='equipment.Tool'),
        ),
    ]
