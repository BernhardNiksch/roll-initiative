# Generated by Django 3.1.6 on 2021-06-26 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monster', '0008_money_blank'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monster',
            name='copper',
        ),
        migrations.RemoveField(
            model_name='monster',
            name='electrum',
        ),
        migrations.RemoveField(
            model_name='monster',
            name='gold',
        ),
        migrations.RemoveField(
            model_name='monster',
            name='platinum',
        ),
        migrations.RemoveField(
            model_name='monster',
            name='silver',
        ),
    ]
