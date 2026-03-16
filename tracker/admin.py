from django.contrib import admin
from .models import PlantHealth, UserPlant

# Register your models here.
admin.site.register(UserPlant)
admin.site.register(PlantHealth)

# Adding my database objects in the built in admin panel for developement purposes