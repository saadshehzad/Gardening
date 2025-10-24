from django.contrib import admin

from .models import *

admin.site.register(Category)
admin.site.register(Plant)
admin.site.register(PlantRegion)
admin.site.register(SeasonalPlant)
admin.site.register(Season)
admin.site.register(LLM)

