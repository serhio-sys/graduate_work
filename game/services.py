import datetime
import json
import random
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.forms import model_to_dict
from .models import Weapon, Armor, Effect


def get_with_user_context(request: HttpRequest, template_name: str) -> TemplateResponse:
    user = get_user_model().objects.select_related('weapon2_equiped', 'weapon_equiped', 'dungeon')\
        .get(pk=request.user.pk)
    return TemplateResponse(request=request, template=template_name, context={'user': user})


def post_church(request: HttpRequest) -> HttpResponse:
    if request.user.balance < 10:
        return render(request=request, template_name="game/church_success.html",
                      context={"head": _("Недостатньо коштів на вашому рахунку")})
    if Effect.objects.filter(user=request.user, is_church_ef=True).exists():
        return redirect(reverse("church_loc") + "?error=Ви вже робили пожертвування.")
    effects = Effect.objects.filter(user__isnull=True, is_church_ef=True)
    effect = effects[random.randint(0, len(effects) - 1)]
    kwargs = model_to_dict(effect, exclude=['id'])
    user_effect = Effect(**kwargs)
    user_effect.user = request.user
    user_effect.deleted_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
    request.user.balance -= 10
    request.user.save()
    user_effect.save()
    return render(request=request, template_name="game/church_success.html",
                  context={"head": _("Бог схильний до вас. (слова священника)"),
                           "msg": _("Ви отримали благословення бога.")})


def post_equip_armor(request: HttpRequest) -> JsonResponse:
    data = json.loads(request.body)
    if data.get('dequip'):
        request.user.armor_equiped = None
        request.user.save()
        return JsonResponse("success", safe=False, status=200)
    try:
        armor = Armor.objects.get(pk=data.get('pk'))
    except Armor.DoesNotExist:
        return JsonResponse({"error": Armor.DoesNotExist})
    if request.user.weapon2_equiped:
        request.user.weapon2_equiped = None
    request.user.armor_equiped = armor
    request.user.save()
    return JsonResponse("success", safe=False, status=200)


def post_equip_weapon(request: HttpRequest) -> JsonResponse:
    data = json.loads(request.body)
    if data.get('dequip') is not None:
        if int(data.get('dequip')) == 1:
            request.user.weapon_equiped = None
            request.user.save()
            return JsonResponse("success", safe=False, status=200)
        if int(data.get('dequip')) == 2:
            request.user.weapon2_equiped = None
            request.user.save()
            return JsonResponse("success", safe=False, status=200)
    else:
        try:
            weapon = Weapon.objects.get(pk=data.get('pk'))
        except Weapon.DoesNotExist:
            return JsonResponse({"error": Weapon.DoesNotExist})
        if request.user.weapon_equiped:
            if request.user.armor_equiped:
                request.user.armor_equiped = None
            request.user.weapon2_equiped = weapon
        else:
            request.user.weapon_equiped = weapon
        request.user.save()
    return JsonResponse("success", safe=False, status=200)


def get_buy_armor(request: HttpRequest, pk: int) -> HttpResponse:
    user = request.user
    item = Armor.objects.get(pk=pk, user__isnull=True)
    kwargs = model_to_dict(item, exclude=['id'])
    if user.balance < item.balance:
        return render(request, 'game/shop_err.html', 
                      context={"msg": _("Не вистачає коштів")})
    user_armors = list(user.armor_set.values_list('name', flat=True).distinct())
    if item.name in user_armors:
        return render(request, 
                      'game/shop_err.html',
                      context={"msg": _("Цей предмет вже є у вас в інвентарі.")})
    if item.lvl <= request.user.lvl and item.dun_lvl <= request.user.dungeon.lvl:
        user.balance -= item.balance
        new_armor = Armor(**kwargs)
        new_armor.user = user
        new_armor.save()
        user.save()
    return render(request, template_name="game/shop_success.html")


def get_buy_weapon(request: HttpRequest, pk: int) -> HttpResponse:
    user = request.user
    item = Weapon.objects.get(pk=pk, user__isnull=True)
    kwargs = model_to_dict(item, exclude=['id'])
    if user.balance < item.balance:
        return render(request, 'game/shop_err.html', 
                      context={"msg": _("Не вистачає коштів")})
    user_weapons = list(user.weapon_set.values_list('name', flat=True).distinct())
    if item.name in user_weapons:
        return render(request, 'game/shop_err.html', 
                      context={"msg": _("Цей предмет вже є у вас в інвентарі.")})
    if item.lvl <= request.user.lvl and item.dun_lvl <= request.user.dungeon.lvl:
        user.balance -= item.balance
        new_weapon = Weapon(**kwargs)
        new_weapon.user = user
        new_weapon.save()
        user.save()
    return render(request, template_name="game/shop_success.html")


def get_inventory_classview(request: HttpRequest, template_name: str):
    user = get_user_model().objects.select_related(
        'weapon2_equiped', 'weapon_equiped', 'armor_equiped'
    ).get(pk=request.user.pk)
    weapons = user.weapon_set.exclude(
        id__in=[user.weapon_equiped_id, user.weapon2_equiped_id]
    )
    armors = user.armor_set.exclude(id=user.armor_equiped_id)
    context = {'user': user, 'armors': armors, 'weapons': weapons}
    return render(request=request, template_name=template_name, context=context)


def get_select_classview(request: HttpRequest, template_name: str) -> HttpResponse:
    if request.user.role is not None:
        return redirect('main_loc')
    classes = [
        {
            "name": "agility",
            "img": request.build_absolute_uri('/static/img/classes/agility.png'),
            "visual_name": _("Ловкач"),
            "desc": _(
                "Головний атрибут: Спритність.\n Якщо супротивник дуже повільний і"
                "буде ловити гав, то є можливість зробити подвійну атаку.\n Особливість:" 
                "можливість ухилитися від атаки та контр атакувати.")
        },
        {
            "name": "strength",
            "img": request.build_absolute_uri('/static/img/classes/strength.png'),
            "visual_name": _("Силач"),
            "desc": _(
                "Головний атрибут: Сила.\n Чим більша сила, тим більше"
                "болю може зазнати супротивник.\n Особливість: наносити тяжкі поранення.")
        },
        {
            "name": "shooter",
            "img": request.build_absolute_uri('/static/img/classes/archer.png'),
            "visual_name": _("Стрілок"),
            "desc": _(
                "Головний атрибут: Спритність.\n Герой завжди тримається на відстані"
                 " й може зробити з супротивника решето.\n Особливість: дальній бій.")

        }
    ]
    return render(request=request, template_name=template_name, context={"classes": classes})


def post_select_classview(request: HttpRequest):
    if request.POST['role'] is not None:
        request.user.role = request.POST['role']
        request.user.save()
    else:
        return redirect('select_class')
    return redirect('main_loc')


class BasedDungeon:
    def __init__(self) -> None:
        self.map_data = []
        self.x, self.y = 0, 0

    def get_start_points(self) -> list[int]:
        for i in enumerate(self.map_data):
            for j in range(len(i[1])):
                if self.map_data[i[0]][j] == 2:
                    return [i[0], j]
        return [0, 2]

    def get_point_reverse(self, x: int, y: int) -> str:
        if x < 0 or y < 0:
            return None
        try:
            if self.map_data[x][y] == 1 or self.map_data[x][y] == 2:
                return reverse("dungeon") + f"?x={x}&y={y}"
            if self.map_data[x][y] == 3:
                return reverse("dungeon_tresure") + f"?x={x}&y={y}"
            if self.map_data[x][y] == 4:
                return reverse("dungeon_enemy") + f"?x={x}&y={y}"
            if self.map_data[x][y] == 5:
                return reverse("dungeon_boss") + f"?x={x}&y={y}"
        except IndexError:
            pass
        return None

    def initial_points(self, request: HttpRequest) -> bool:
        leave = False
        with open(settings.BASE_DIR + request.user.dungeon.map.url, 'r', encoding='utf-8') as f:
            self.map_data = json.load(f)
        self.x, self.y = int(request.GET.get("x", request.session.get("x", 0))),\
                         int(request.GET.get("y", request.session.get("y", 0)))
        if self.map_data[self.x][self.y] == 0:
            points = self.get_start_points()
            self.x, self.y = points[0], points[1]
        if self.map_data[self.x][self.y] == 2:
            leave = True
        self.map_data[self.x][self.y] = 6
        return leave

    def get_based_response(self, request: HttpRequest) -> TemplateResponse:
        can_leave = self.initial_points(request=request)
        response = get_with_user_context(request=request,
                                         template_name=self.template_name)
        moves = {"a": self.get_point_reverse(self.x + 1, self.y),
                 "l": self.get_point_reverse(self.x, self.y + 1),
                 "r": self.get_point_reverse(self.x, self.y - 1), 
                 "b": self.get_point_reverse(self.x - 1, self.y)}
        response.context_data.update(moves)
        response.context_data['map'] = self.map_data
        response.context_data['can_leave'] = can_leave
        request.session["x"], request.session["y"] = self.x, self.y
        return response
