# Generated by Django 3.1.6 on 2021-03-23 16:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monster', '0002_monster_temporary_hp'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monster',
            options={'ordering': ('first_name', 'last_name')},
        ),
    ]
