from drf_spectacular.utils import extend_schema
from rest_framework import filters
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    get_object_or_404,
    ListAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from common.pagination import Pagination
from .models import CharacterClass, CharacterRace, Character
from .serializers import (
    CharacterAddSerializer,
    CharacterAdjustHealthSerializer,
    CharacterClassListEntrySerializer,
    CharacterClassSerializer,
    CharacterDetailSerializer,
    CharacterEquipmentSerializer,
    CharacterHealthSerializer,
    CharacterListEntrySerializer,
    CharacterRaceSerializer,
)
from common.views import ManagedListView


class CharacterClassListView(ListAPIView):
    """
    Paginated character class list view with search, and sorting capability.
    """

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("name",)
    ordering_fields = ("name", "hit_die")
    ordering = ("name", "id")
    pagination_class = Pagination
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


class CharacterRaceListView(ListAPIView):
    """
    Paginated character class list view with filter, search, and sorting capability.
    """

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("name",)
    ordering_fields = (
        "name",
        "speed",
        "strength_increase",
        "dexterity_increase",
        "constitution_increase",
        "intelligence_increase",
        "wisdom_increase",
        "charisma_increase",
    )
    ordering = ("name", "id")
    pagination_class = Pagination
    queryset = CharacterRace.objects.all()
    serializer_class = CharacterRaceSerializer


class CharacterRaceView(RetrieveAPIView):
    """
    Get a character race's details.
    """

    queryset = CharacterRace.objects.all()
    serializer_class = CharacterRaceSerializer


class CharacterListView(ListAPIView):
    """
    Paginated character class list view with filter, search, and sorting capability.
    """

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = (
        "first_name", "last_name", "title", "age", "level", "race__name", "character_class__name"
    )
    ordering = ["first_name", "last_name", "id"]
    pagination_class = Pagination
    queryset = Character.objects.all().prefetch_related("race", "character_class")
    search_fields = (
        "first_name", "last_name", "title", "race__name", "character_class__name",
    )
    serializer_class = CharacterListEntrySerializer


class CharacterAddView(CreateAPIView):
    """Add a new character."""

    queryset = Character.objects.all()
    serializer_class = CharacterAddSerializer


class CharacterView(RetrieveDestroyAPIView):
    """Manage a character's details."""

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


class CharacterHealthView(RetrieveUpdateAPIView):
    """
    Get, update, or adjust a character's max, current, and temporary health.

    PUT and PATCH updates the HP with the requested valued.
    POST adjusts HP by the requested value.
    """

    queryset = Character.objects.all()
    serializer_class = CharacterHealthSerializer

    @extend_schema(request=CharacterAdjustHealthSerializer)
    def post(self, request: Request, pk):
        """Adjust the character's current, maximum, and temporary HP by the requested values."""

        serializer = CharacterAdjustHealthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data
        character = self.get_object()

        update_fields = []
        heal_amount = request_data["current_hp"]
        if heal_amount:
            character.heal(heal_amount)
            update_fields.append("current_hp")
        max_hp_adjustment = request_data["max_hp"]
        add_constitution = request_data["add_constitution_to_max_hp"]
        if max_hp_adjustment or add_constitution:
            character.increase_max_hp(max_hp_adjustment, add_constitution=add_constitution)
            update_fields.append("max_hp")
        temporary_hp_adjustment = request_data["temporary_hp"]
        if temporary_hp_adjustment:
            character.adjust_temporary_hp(temporary_hp_adjustment)
            update_fields.append("temporary_hp")

        if update_fields:
            character.save(update_fields=update_fields)
        serializer = self.get_serializer(character)
        return Response(serializer.data)
