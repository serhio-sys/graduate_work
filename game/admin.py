from django.contrib import admin
from .models import (
    Armor,
    Weapon,
    Enemy,
    Effect 
)

admin.site.register(Armor)
admin.site.register(Weapon)
admin.site.register(Enemy)
admin.site.register(Effect)
