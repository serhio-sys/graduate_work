from django.shortcuts import redirect
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.template.response import TemplateResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from .services import get_select_classview, get_with_user_context, post_select_classview, get_inventory_classview, \
    post_church, post_equip_armor, post_equip_weapon, get_buy_armor, get_buy_weapon
from .models import Weapon, Armor
from .forms import UserIncreaseStatsForm
from django.conf import settings

import json


@login_required
def back_to_starter_page(request: HttpRequest, name: str):
    if name in ["inventory", "abilities"]:
        return redirect("home")
    if request.method == "GET":
        request.user.current_position = name
        request.user.save(update_fields=['current_position'])
        return redirect("home")
    return JsonResponse("Error")


@login_required
def get_start_game_page(request: HttpRequest):
    if request.user.current_position is None:
        return redirect("main_loc")
    try:
        return redirect(request.user.current_position)
    except NoReverseMatch:
        return redirect("main_loc")


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
            request.user.save(update_fields=['current_position'])
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
        response.context_data.update({"error": request.GET.get("error", None)})
        return response.render()

    def post(self, request: HttpRequest):
        return post_church(request=request)


class ShopLocation(LoginRequiredMixin, View):
    template_name = "game/shop.html"

    def get(self, request: HttpRequest):
        weapons = Weapon.objects.filter(user__isnull=True)
        armors = Armor.objects.filter(user__isnull=True)
        response = get_with_user_context(request=request, template_name=self.template_name)
        response.context_data.update({"weapons": weapons, "armors": armors})
        return response.render()


class SelectClassView(LoginRequiredMixin, View):
    template_name = "game/select_class.html"

    def get(self, request: HttpRequest):
        return get_select_classview(request=request, template_name=self.template_name)

    def post(self, request: HttpRequest):
        return post_select_classview(request=request)


class AbilitiesView(LoginRequiredMixin, View):
    template_name = "game/abilities.html"

    def get(self, request: HttpRequest):
        name = request.GET.get("name", "main_loc")
        if name != 'inventory':
            request.user.current_position = name
            request.user.save(update_fields=['current_position'])
        response = get_with_user_context(request=request, template_name=self.template_name)
        response.context_data.update({"form": UserIncreaseStatsForm(instance=request.user)})
        return response.render()

    def post(self, request: HttpRequest):
        form = UserIncreaseStatsForm(request.POST)
        response = get_with_user_context(request=request, template_name=self.template_name)
        if form.is_valid():
            difference_ag = form.cleaned_data['agility'] - request.user.agility
            difference_str = form.cleaned_data['strength'] - request.user.strength
            if (difference_ag + difference_str) <= request.user.upgrade_points:
                request.user.agility = form.cleaned_data['agility']
                request.user.strength = form.cleaned_data['strength']
                request.user.upgrade_points = form.cleaned_data['upgrade_points']
                request.user.save(update_fields=['upgrade_points', 'strength', 'agility'])
            response = get_with_user_context(request=request, template_name=self.template_name)
            response.context_data.update({"form": UserIncreaseStatsForm(instance=request.user)})
            return response.render()
        else:
            response.context_data.update({"form": form})
            return response.render()


class DungeonEnterenceView(LoginRequiredMixin, View):
    template_name = "game/dungeon/dungeon.html"
    map_data = []

    def get_start_points(self) -> list[int]:
        for i in range(len(self.map_data)):
            for j in range(len(self.map_data[i])):
                if self.map_data[i][j] == 2:
                    return [i, j]
        raise Exception("Not found point 2 in map")

    def get(self, request: HttpRequest):
        return get_with_user_context(request=request, template_name=self.template_name).render()


class DungeonView(LoginRequiredMixin, View):
    template_name = "game/dungeon/dungeon_inside.html"
    map_data = []
    x, y = 0, 0

    def get_start_points(self) -> list[int]:
        for i in range(len(self.map_data)):
            for j in range(len(self.map_data[i])):
                if self.map_data[i][j] == 2:
                    return [i, j]
        raise Exception("Not found point 2 in map")

    def get_point_reverse(self, x: int, y: int) -> str:
        if x < 0 or y < 0:
            return None
        if self.map_data[x][y] == 1 or self.map_data[x][y] == 2:
            return reverse("dungeon") + f"?x={x}&y={y}"
        if self.map_data[x][y] == 3:
            return reverse("dungeon_tresure") + f"?x={x}&y={y}"
        if self.map_data[x][y] == 4:
            return reverse("dungeon_enemy") + f"?x={x}&y={y}"
        if self.map_data[x][y] == 5:
            return reverse("dungeon_boss") + f"?x={x}&y={y}"
        return None

    def initial_points(self, request: HttpRequest) -> bool:
        leave = False
        with open(settings.BASE_DIR + request.user.dungeon.map.url, 'r') as f:
            self.map_data = json.load(f)
        self.x, self.y = int(request.GET.get("x", request.session.get("x", 0))), int(
            request.GET.get("y", request.session.get("y", 0)))
        if self.map_data[self.x][self.y] == 0:
            points = self.get_start_points()
            self.x, self.y = points[0], points[1]
        if self.map_data[self.x][self.y] == 2:
            leave = True
        self.map_data[self.x][self.y] = 6
        return leave

    def get_based_response(self, request: HttpRequest) -> TemplateResponse:
        can_leave = self.initial_points(request=request)
        response = get_with_user_context(request=request, template_name=self.template_name)
        moves = {"a": self.get_point_reverse(self.x + 1, self.y), "l": self.get_point_reverse(self.x, self.y + 1),
                 "r": self.get_point_reverse(self.x, self.y - 1), "b": self.get_point_reverse(self.x - 1, self.y)}
        response.context_data.update(moves)
        response.context_data['map'] = self.map_data
        response.context_data['can_leave'] = can_leave
        request.session["x"], request.session["y"] = self.x, self.y
        return response

    def get(self, request: HttpRequest):
        response = self.get_based_response(request=request)
        return response.render()


class DungeonEnemyView(DungeonView):
    template_name = "game/dungeon/dungeon_enemy.html"

    def get(self, request: HttpRequest):
        response = self.get_based_response(request=request)
        response.template_name = self.template_name
        return response.render()

    def post(self, request: HttpRequest):
        pass
