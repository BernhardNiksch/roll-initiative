# Generated by Django 3.1.6 on 2021-04-23 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0009_characterclass_tool_proficiencies'),
    ]

    operations = [
        migrations.AlterField(
            model_name='character',
            name='copper',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='character',
            name='electrum',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='character',
            name='gold',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='character',
            name='platinum',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='character',
            name='silver',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
