from django.urls import path

from .views import (
    CharacterAddView,
    CharacterClassListView,
    CharacterClassView,
    CharacterEquipmentView,
    CharacterListView,
    CharacterRaceListView,
    CharacterRaceView,
    CharacterView,
)


urlpatterns = [
    path('class/list/', CharacterClassListView.as_view(), name="character_class_list"),
    path('class/<str:pk>/', CharacterClassView.as_view(), name="character_class_detail"),
    path('race/list/', CharacterRaceListView.as_view(), name="character_race_list"),
    path('race/<str:pk>/', CharacterRaceView.as_view(), name="character_race_detail"),
    path('list/', CharacterListView.as_view(), name="character_list"),
    path('', CharacterAddView.as_view(), name="character"),
    path('<str:pk>/', CharacterView.as_view(), name="character_detail"),
    path('<str:pk>/equipment/', CharacterEquipmentView.as_view(), name="character_equipment"),
]
