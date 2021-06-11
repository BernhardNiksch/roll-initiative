from django.urls import path

from .views import (
    AdventuringGearListView,
    AdventuringGearView,
    ArmorListView,
    ArmorView,
    EquipmentPackListView,
    EquipmentPackView,
    ToolListView,
    ToolView,
    WeaponListView,
    WeaponView,
)

urlpatterns = [
    path('adventuring-gear/list/', AdventuringGearListView.as_view(), name="adventuring_gear_list"),
    path(
        'adventuring-gear/<str:pk>/', AdventuringGearView.as_view(), name="adventuring_gear_detail"
    ),
    path('equipment-pack/list/', EquipmentPackListView.as_view(), name="equipment_pack_list"),
    path('equipment-pack/<str:pk>/', EquipmentPackView.as_view(), name="equipment_pack_detail"),
    path('armor/list/', ArmorListView.as_view(), name="armor_list"),
    path('armor/<str:pk>/', ArmorView.as_view(), name="armor_detail"),
    path('tool/list/', ToolListView.as_view(), name="tool_list"),
    path('tool/<str:pk>/', ToolView.as_view(), name="tool_detail"),
    path('weapon/list/', WeaponListView.as_view(), name="weapon_list"),
    path('weapon/<str:pk>/', WeaponView.as_view(), name="weapon_detail"),
]
