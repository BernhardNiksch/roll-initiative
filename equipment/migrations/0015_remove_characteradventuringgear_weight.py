# Generated by Django 3.1.6 on 2021-05-23 16:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('equipment', '0014_added_character_gear_table_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='characteradventuringgear',
            name='weight',
        ),
    ]
