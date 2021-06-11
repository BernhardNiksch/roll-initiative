from django.contrib import admin

from .models import CharacterClassFeature, CharacterFeat, Feat


admin.site.register([Feat, CharacterClassFeature, CharacterFeat])
