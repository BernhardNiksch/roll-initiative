# Generated by Django 3.1.6 on 2021-04-01 19:20

import common.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0005_auto_20210401_2120'),
        ('equipment', '0002_weapon_damage'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdventuringGear',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=4)),
                ('description', models.TextField()),
                ('length', models.PositiveSmallIntegerField(null=True)),
                ('quantity', models.PositiveSmallIntegerField(null=True)),
            ],
            options={
                'db_table': 'adventuring_gear',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='AdventuringGearPack',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('quantity', models.PositiveSmallIntegerField(default=1)),
                ('adventuring_gear', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='equipment.adventuringgear')),
            ],
            options={
                'db_table': 'adventuring_gear_pack',
            },
        ),
        migrations.CreateModel(
            name='Tool',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=4)),
                ('description', models.TextField()),
            ],
            options={
                'db_table': 'tool',
                'ordering': ('name',),
            },
        ),
        migrations.RenameField(
            model_name='armor',
            old_name='cost',
            new_name='gold',
        ),
        migrations.AlterField(
            model_name='armor',
            name='stealth_disadvantage',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='armor',
            name='weight',
            field=models.DecimalField(decimal_places=2, max_digits=4),
        ),
        migrations.CreateModel(
            name='EquipmentPack',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('gold', models.PositiveSmallIntegerField()),
                ('gear', models.ManyToManyField(related_name='_equipmentpack_gear_+', through='equipment.AdventuringGearPack', to='equipment.AdventuringGear')),
            ],
            options={
                'db_table': 'equipment_pack',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='CharacterWeapon',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('equipped', models.BooleanField()),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.character')),
                ('weapon', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='equipment.weapon')),
            ],
            options={
                'db_table': 'character_weapon',
            },
        ),
        migrations.CreateModel(
            name='CharacterArmor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('equipped', models.BooleanField()),
                ('armor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='equipment.armor')),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.character')),
            ],
            options={
                'db_table': 'character_armor',
            },
        ),
        migrations.CreateModel(
            name='CharacterAdventuringGear',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('length', models.PositiveSmallIntegerField(null=True)),
                ('quantity', models.PositiveSmallIntegerField(null=True)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=5)),
                ('adventuring_gear', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='equipment.adventuringgear')),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.character')),
            ],
        ),
        migrations.AddField(
            model_name='adventuringgearpack',
            name='equipment_pack',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='equipment.equipmentpack'),
        ),
    ]
