# Generated by Django 3.1.6 on 2021-06-07 19:54

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('features', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='characterfeat',
            name='properties',
        ),
        migrations.AddField(
            model_name='characterfeat',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, serialize=False),
        ),
        migrations.RemoveField(
            model_name='characterfeat',
            name='id',
        ),
        migrations.AlterField(
            model_name='characterfeat',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
        migrations.RenameField(
            model_name='characterfeat',
            old_name='uuid',
            new_name='id',
        )
    ]
