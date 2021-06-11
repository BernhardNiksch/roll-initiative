from django.urls import path

from .views import MonsterTypeListView, MonsterTypeView, MonsterListView, MonsterView


urlpatterns = [
    path('type/list/', MonsterTypeListView.as_view(), name="monster_type_list"),
    path('type/<str:pk>/', MonsterTypeView.as_view(), name="monster_type_detail"),
    path('list/', MonsterListView.as_view(), name="monster_list"),
    path('<str:pk>/', MonsterView.as_view(), name="monster_detail"),
]
