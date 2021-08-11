from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from schema_graph.views import Schema

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/character/', include('character.urls'), name="character"),
    path('api/equipment/', include('equipment.urls'), name="equipment"),
    path('api/monster/', include('monster.urls'), name="monster"),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema-graph/', Schema.as_view(), name='schema_graph'),
    path('schema-plate/', include('django_spaghetti.urls'), name='schema_plate'),
    path('swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger_ui'),
]
