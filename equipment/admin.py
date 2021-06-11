from django.contrib import admin

from .models import (
    AdventuringGear,
    Armor,
    CharacterAdventuringGear,
    CharacterArmor,
    CharacterWeapon,
    EquipmentPack,
    EquipmentPackGear,
    Tool,
    Weapon,
)


admin.site.register(
    [
        Armor,
        CharacterArmor,
        Weapon,
        CharacterWeapon,
        AdventuringGear,
        CharacterAdventuringGear,
        EquipmentPack,
        EquipmentPackGear,
        Tool,
    ]
)
