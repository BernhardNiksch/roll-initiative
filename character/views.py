from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    get_object_or_404,
    RetrieveAPIView,
)
from rest_framework.request import Request
from rest_framework.response import Response

from .models import CharacterClass, CharacterRace, Character
from .serializers import (
    CharacterAddSerializer,
    CharacterClassListEntrySerializer,
    CharacterClassSerializer,
    CharacterEquipmentSerializer,
    CharacterListEntrySerializer,
    CharacterRaceSerializer,
    CharacterDetailSerializer,
)
from common.views import ManagedListView


class CharacterClassListView(ManagedListView):
    """
    Paginated character class list view with filter, search, and sorting capability.
    """

    search_fields = ("name",)
    sort_fields = ("name", "hit_die")
    ordering = ["name", "id"]
    queryset = CharacterClass.objects.all()
    serializer_class = CharacterClassListEntrySerializer


class CharacterClassView(RetrieveAPIView):
    """
    Get a character class' details.
    """

    queryset = CharacterClass.objects.all().prefetch_related(
        "armor_proficiencies", "tool_proficiencies", "weapon_proficiencies",
    )  # TODO reduce queries on feat
    serializer_class = CharacterClassSerializer


class CharacterRaceListView(ManagedListView):
    """
    Paginated character class list view with filter, search, and sorting capability.
    """

    search_fields = ("name",)
    sort_fields = (
        "name",
        "speed",
        "strength_increase",
        "dexterity_increase",
        "constitution_increase",
        "intelligence_increase",
        "wisdom_increase",
        "charisma_increase",
    )
    ordering = ["name", "id"]
    queryset = CharacterRace.objects.all()
    serializer_class = CharacterRaceSerializer


class CharacterRaceView(RetrieveAPIView):
    """
    Get a character race's details.
    """

    queryset = CharacterRace.objects.all()
    serializer_class = CharacterRaceSerializer


class CharacterListView(ManagedListView):
    """
    Paginated character class list view with filter, search, and sorting capability.
    """

    search_fields = (
        "first_name", "last_name", "title", "race__name", "character_class__name",
    )
    sort_fields = ("first_name", "last_name", "title", "age", "level", "race", "character_class")
    field_map = {
        "race": "race__name",
        "character_class": "character_class__name",
    }
    ordering = ["first_name", "last_name", "id"]
    queryset = Character.objects.all().prefetch_related("race", "character_class")
    serializer_class = CharacterListEntrySerializer


class CharacterAddView(CreateAPIView):
    """Add a new character."""

    queryset = Character.objects.all()
    serializer_class = CharacterAddSerializer


class CharacterView(RetrieveAPIView):
    """
    Manage Characters.

    For now just a GET.
    """

    queryset = Character.objects.all().select_related("race", "character_class", "campaign")
    serializer_class = CharacterDetailSerializer


class CharacterEquipmentView(GenericAPIView):
    """
    Manage equipment assigned to a character.
    """

    queryset = Character.objects.prefetch_related("tools")
    # TODO Get this prefetch working to reduce queries
    # For some reason Django isn't using the prefetched data.
    # queryset = Character.objects.prefetch_related(
    #     "tools",
    #     Prefetch(
    #         "adventuring_gear",
    #         queryset=CharacterAdventuringGear.objects.select_related("adventuring_gear")
    #     ),
    #     Prefetch("armor", queryset=CharacterArmor.objects.select_related("armor")),
    #     Prefetch("weapons", queryset=CharacterWeapon.objects.select_related("weapon")),
    # )
    serializer_class = CharacterEquipmentSerializer

    def get(self, request: Request, pk):
        """
        Get equipment assigned to a character and the sum of their weights.
        """

        instance = get_object_or_404(self.queryset, pk=pk)
        serializer = self.get_serializer(instance)
        response_data = serializer.data

        weight = 0
        for equipment, items in response_data.items():
            # assuming the serializer includes only lists of weighted items
            weight += sum(float(item["weight"]) for item in items)
        response_data["total_weight"] = f"{weight:.2f}"
        return Response(response_data)
