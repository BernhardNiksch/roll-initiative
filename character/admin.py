from django.contrib import admin

from .models import Character, CharacterClass, CharacterRace


admin.site.register([Character, CharacterClass, CharacterRace])
