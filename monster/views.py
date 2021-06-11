from rest_framework.generics import RetrieveAPIView

from .models import MonsterType, Monster
from .serializers import MonsterTypeSerializer, MonsterListEntrySerializer, MonsterSerializer
from common.views import ManagedListView


class MonsterTypeListView(ManagedListView):
    """
    Paginated monster type list view with filter, search, and sorting capability.
    """

    search_fields = ("name",)
    sort_fields = ("name", "armor_class")
    ordering = ["name", "id"]
    queryset = MonsterType.objects.all()
    serializer_class = MonsterTypeSerializer


class MonsterTypeView(RetrieveAPIView):
    """
    Get a monster type's details.
    """

    queryset = MonsterType.objects.all()
    serializer_class = MonsterTypeSerializer


class MonsterListView(ManagedListView):
    """
    Paginated monster type list view with filter, search, and sorting capability.
    """

    search_fields = ("first_name", "last_name", "armor_class", "max_hp", "monster_type__name")
    sort_fields = ("first_name", "last_name", "armor_class", "max_hp", "monster_type")
    field_map = {"monster_type": "monster_type__name"}
    ordering = ["first_name", "last_name", "id"]
    queryset = Monster.objects.all().prefetch_related("monster_type")
    serializer_class = MonsterListEntrySerializer


class MonsterView(RetrieveAPIView):
    """
    Manage monsters.

    Just a GET for now.
    """

    queryset = Monster.objects.all().select_related("monster_type")
    serializer_class = MonsterSerializer
