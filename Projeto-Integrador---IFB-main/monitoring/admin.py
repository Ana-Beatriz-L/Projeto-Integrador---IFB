from django.contrib import admin

from .models import Observation, Station

admin.site.register(Station)
admin.site.register(Observation)
