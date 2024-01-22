from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from .services import get_select_classview, get_with_user_context, post_select_classview, get_inventory_classview, post_church, post_equip_armor, post_equip_weapon, get_buy_armor, get_buy_weapon
from .models import Weapon, Armor
        

@login_required
def back_to_starter_page(request: HttpRequest, name: str):
    if name == "inventory":
        return redirect("home")
    if request.method == "GET":
        request.user.current_position = name
        request.user.save()
        return redirect("home")
    return JsonResponse("Error")

@login_required
def get_start_game_page(request: HttpRequest):
   if request.user.current_position is None:
       return redirect("main_loc")
   return redirect(request.user.current_position)

@login_required
@require_POST
def equip_armor(request: HttpRequest):
    return post_equip_armor(request=request)

@login_required
@require_POST
def equip_weapon(request: HttpRequest):
    return post_equip_weapon(request=request)

@login_required
def buy_armor(request: HttpRequest, pk: int):
    return get_buy_armor(request=request, pk=pk)

@login_required
def buy_weapon(request: HttpRequest, pk: int):
    return get_buy_weapon(request=request, pk=pk)

class InventoryView(LoginRequiredMixin, View):
    template_name = "game/inventory.html"

    def get(self, request: HttpRequest, name: str):
        if request.resolver_match.url_name != name:
            request.user.current_position = name
            request.user.save()
        return get_inventory_classview(request=request, template_name=self.template_name)

class MainLocationView(LoginRequiredMixin, View):
    template_name = "game/main.html"

    def get(self, request: HttpRequest):
        return get_with_user_context(request=request, template_name=self.template_name).render()
        
class CityLocation(LoginRequiredMixin, View):
    template_name = "game/city_center.html"

    def get(self, request: HttpRequest):
        return get_with_user_context(request=request, template_name=self.template_name).render()
    
class OutskirtsLocation(LoginRequiredMixin, View):
    template_name = "game/outskirts.html"
    
    def get(self, request: HttpRequest):
        return get_with_user_context(request=request, template_name=self.template_name).render()

class ChurchLocation(LoginRequiredMixin, View):
    template_name = "game/church.html"

    def get(self, request: HttpRequest):
        response = get_with_user_context(request=request, template_name=self.template_name)
        response.context_data.update({"error":request.GET.get("error",None)})
        return response.render()
    
    def post(self, request: HttpRequest):
        return post_church(request=request)

class ShopLocation(LoginRequiredMixin, View):
    template_name = "game/shop.html"

    def get(self, request:HttpRequest):
        weapons = Weapon.objects.filter(user__isnull=True)
        armors = Armor.objects.filter(user__isnull=True)
        response = get_with_user_context(request=request, template_name=self.template_name)
        response.context_data.update({"weapons":weapons,"armors":armors})
        return response.render()

class SelectClassView(LoginRequiredMixin, View):
    template_name = "game/select_class.html"

    def get(self, request: HttpRequest):
        return get_select_classview(request=request, template_name=self.template_name)
    
    def post(self, request: HttpRequest):
        return post_select_classview(request=request)
    

