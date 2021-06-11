from django.db import connection
from django.db.models import Prefetch
from rest_framework.generics import RetrieveAPIView, get_object_or_404, GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from common.views import ManagedListView
from .models import Tool, Armor, Weapon, AdventuringGear, EquipmentPack, EquipmentPackGear
from .serializers import (
    AdventuringGearSerializer,
    ArmorSerializer,
    EquipmentPackDetailSerializer,
    EquipmentPackSerializer,
    ToolSerializer,
    WeaponSerializer,
)


class ArmorListView(ManagedListView):
    """
    Paginated Armor list view with filter, search, and sorting capability.
    """

    search_fields = ("name", "armor_type")
    sort_fields = (
        "name",
        "armor_type",
        "weight",
        "gold",
        "armor_class",
        "armor_class_increase",
        "strength_requirement",
    )
    ordering = ["armor_type", "name", "id"]
    queryset = Armor.objects.all()
    serializer_class = ArmorSerializer

    def post(self, request: Request):
        armor_type_options = [{"id": i, "name": n} for i, n in Armor.ARMOR_TYPE_CHOICES]
        # stealth_disadv_choices = [True, False]
        self.filter_options = {
            "armor_type": armor_type_options,
            # "stealth_disadvantage": stealth_disadv_choices,
        }
        return super().post(request)


class ArmorView(RetrieveAPIView):
    """
    Get a piece of Armor's details.
    """

    queryset = Armor.objects.all()
    serializer_class = ArmorSerializer


class AdventuringGearListView(ManagedListView):
    """
    Paginated AdventuringGear list view with filter, search, and sorting capability.
    """

    search_fields = ("name",)
    sort_fields = ("name", "weight", "quantity", "length")
    ordering = ["name", "id"]
    queryset = AdventuringGear.objects.all()
    serializer_class = AdventuringGearSerializer


class AdventuringGearView(RetrieveAPIView):
    """
    Get a piece of AdventuringGear's details.
    """

    queryset = AdventuringGear.objects.all()
    serializer_class = AdventuringGearSerializer


class EquipmentPackListView(ManagedListView):
    """
    Paginated EquipmentPack list view with filter, search, and sorting capability.
    """

    search_fields = ("name",)
    sort_fields = ("name", "gold")
    ordering = ["name", "id"]
    queryset = EquipmentPack.objects.all()
    serializer_class = EquipmentPackSerializer


class EquipmentPackView(GenericAPIView):
    """
    Get EquipmentPack's details and list included AdventuringGear.
    """

    queryset = EquipmentPack.objects.prefetch_related(
        Prefetch(
            "gear", queryset=EquipmentPackGear.objects.select_related("adventuring_gear")
        )
    )
    serializer_class = EquipmentPackDetailSerializer

    def get(self, request: Request, pk):
        # RetrieveAPIView adds additional filters that makes prefetch_related() useless.
        # Getting object this way uses queryset cache for prefetched adventuring_gear.
        instance = get_object_or_404(self.queryset, pk=pk)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class WeaponListView(ManagedListView):
    """
    Paginated Weapon list view with filter, search, and sorting capability.
    """

    search_fields = ("name", "weapon_type")
    sort_fields = (
        "name",
        "weapon_type",
        "weight",
        "copper",
        "silver",
        "electrum",
        "gold",
        "platinum",
        "normal_range",
        "maximum_range",
    )
    ordering = ["weapon_type", "name", "id"]
    queryset = Weapon.objects.all()
    serializer_class = WeaponSerializer

    def post(self, request: Request):
        weapon_type_options = [{"id": i, "name": n} for i, n in Weapon.WEAPON_TYPE_CHOICES]
        self.filter_options = {"weapon_type": weapon_type_options}
        return super().post(request)


class WeaponView(RetrieveAPIView):
    """
    Get a piece of Weapon's details.
    """

    queryset = Weapon.objects.all()
    serializer_class = WeaponSerializer


class ToolListView(ManagedListView):
    """
    Paginated Tool list view with filter, search, and sorting capability.
    """

    search_fields = ("name", "description")
    sort_fields = ("name", "weight", "copper", "silver", "electrum", "gold", "platinum")
    ordering = ["name", "id"]
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer

    def post(self, request: Request):
        category_options = [{"id": i, "name": n} for i, n in Tool.TOOL_CATEGORY_CHOICES]
        self.filter_options = {"category": category_options}
        return super().post(request)


class ToolView(RetrieveAPIView):
    """
    Get a Tool's details.
    """

    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
