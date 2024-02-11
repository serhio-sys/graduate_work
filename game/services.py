import datetime
import json
import random
import datetime
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.forms import model_to_dict
from users.models import NewUser, return_all_damage_taken
from .models import Weapon, Armor, Effect, Enemy
from .logs import get_text_effect
from .forms import AttackForm


def get_with_user_context(request: HttpRequest, template_name: str) -> TemplateResponse:
    user = request.user
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
    if user.agility < item.req_agility or user.strength < item.req_strength:
        return render(request, 'game/shop_err.html', 
                      context={"msg": _("Недостатньо атрибутів для цього предмету")})
    user_armors = list(user.armor_set.values_list('name', flat=True).distinct())
    if item.name in user_armors:
        return render(request, 
                      'game/shop_err.html',
                      context={"msg": _("Цей предмет вже є у вас в інвентарі.")})
    if item.lvl <= request.user.lvl:
        user.balance -= item.balance
        new_armor = Armor(**kwargs)
        new_armor.user = user
        new_armor.save()
        user.save()
    return render(request, template_name="game/shop_success.html")


def get_buy_weapon(request: HttpRequest, pk: int) -> HttpResponse:
    user = request.user
    item = Weapon.objects.get(pk=pk, user__isnull=True)
    if user.balance < item.balance:
        return render(request, 'game/shop_err.html', 
                      context={"msg": _("Не вистачає коштів")})
    if user.agility < item.req_agility or user.strength < item.req_strength:
        return render(request, 'game/shop_err.html', 
                      context={"msg": _("Недостатньо атрибутів для цього предмету")})
    kwargs = model_to_dict(item, exclude=['id'])
    user_weapons = list(user.weapon_set.values_list('name', flat=True).distinct())
    if item.name in user_weapons:
        return render(request, 'game/shop_err.html', 
                      context={"msg": _("Цей предмет вже є у вас в інвентарі.")})
    if item.lvl <= request.user.lvl:
        user.balance -= item.balance
        new_weapon = Weapon(**kwargs)
        new_weapon.user = user
        new_weapon.save()
        user.save()
    return render(request, template_name="game/shop_success.html")


def get_inventory_classview(request: HttpRequest, template_name: str):
    user = request.user
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
        self.points = self.get_start_points()
        self.image_choises = [static("img/locations/dungeon/dun1_1.jpg"),
                              static("img/locations/dungeon/dun1_2.jpg"),
                              static("img/locations/dungeon/dun1_3.jpg"),
                              static("img/locations/dungeon/dun1_4.jpg")]

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

    def initial_points(self, request: HttpRequest, user: NewUser) -> bool:
        leave = False
        with open(settings.BASE_DIR + user.dungeon.map.url, 'r', encoding='utf-8') as f:
            self.map_data = json.load(f)
        self.x, self.y = int(request.GET.get("x", request.session.get("x", 0))),\
                         int(request.GET.get("y", request.session.get("y", 0)))
        if self.map_data[self.x][self.y] == 0:
            self.x, self.y = self.points[0], self.points[1]
        if self.map_data[self.x][self.y] == 2:
            leave = True
        self.map_data[self.x][self.y] = 6
        return leave

    def get_based_response(self, request: HttpRequest) -> TemplateResponse|HttpResponseRedirect:
        response = get_with_user_context(request=request,
                                        template_name=self.template_name)
        can_leave = self.initial_points(request=request, user=response.context_data['user'])
        try:
            if (self.x > request.session["x"]+1 or\
                self.x < request.session["x"]-1 or\
                self.y > request.session["y"]+1 or\
                self.y < request.session["y"]-1):
                return redirect(self.get_point_reverse(request.session["x"], request.session["y"]))
        except KeyError: 
            pass   
        moves = {"a": self.get_point_reverse(self.x + 1, self.y),
                "l": self.get_point_reverse(self.x, self.y + 1),
                "r": self.get_point_reverse(self.x, self.y - 1), 
                "b": self.get_point_reverse(self.x - 1, self.y)}
        response.context_data.update(moves)
        response.context_data['map'] = self.map_data
        response.context_data['can_leave'] = can_leave
        if self.points[0] == self.x and self.points[1] == self.y:
            response.context_data['img'] = self.image_choises[0]
        else:
            response.context_data['img'] = self.image_choises[random.randint(0,len(self.image_choises)-1)]
        request.session["x"], request.session["y"] = self.x, self.y
        return response

class BasedFight:
    
    def __init__(self) -> None:
        self.is_winner = None
        self.logs = []
        self.patterns = ['head','leg','body']

    
    def initial_enemy(self, user: NewUser):
        if user.enemy is None:
            enemies = Enemy.objects.filter(dungeon__lvl = user.dungeon.lvl, is_boss = False)
            user.enemy = Enemy.objects.create(
                **model_to_dict(enemies[random.randint(0,len(enemies)-1)], exclude=['id','dungeon'])
                )
            user.save(update_fields=['enemy'])


    def apply_effect(self, effect_name: str, whom: NewUser | Enemy, duration_min: int):
        effect = Effect.objects.get(name=effect_name, user__isnull=True, enemy__isnull=True)
        en_effect = Effect(**model_to_dict(effect, exclude=['id']))
        en_effect.deleted_time = datetime.datetime.now() + datetime.timedelta(minutes=duration_min)
        setattr(en_effect, 'user' if isinstance(whom, NewUser) else 'enemy', whom)
        if en_effect.user is not None or en_effect.enemy is not None:
            en_effect.save()

    def get_entity_effect(self, who: NewUser | Enemy, whom: NewUser | Enemy):
        is_whom_user = isinstance(whom, NewUser)

        if is_whom_user and whom.effect_set.all().count() > 3: # pylint: disable=R1705
            return
        elif not is_whom_user and whom.effect_enemy.all().count() > 3:
            return

        if who.role in ["agility", "shooter"] and random.randint(0, 100) < 5:
            self.apply_effect("Кровотеча", whom, 2)
            self.logs.append(get_text_effect(who.get_name(), whom.get_name(), "bliding"))
        elif who.role == "strength" and random.randint(0, 100) < 8:
            self.apply_effect("Перелом кістки", whom, 2)    
            self.logs.append(get_text_effect(who.get_name(), whom.get_name(), "bones"))

    def attack(self, request: HttpRequest, who: NewUser|Enemy, whom: NewUser|Enemy) -> int:
        form = AttackForm(request.POST)
        if form.is_valid():
            rnd = random.randint(0,len(self.patterns)-1)
            if isinstance(who, NewUser):
                attack = 0
                if form.cleaned_data['attack'] != self.patterns[rnd]:
                    attack = return_all_damage_taken(who) - whom.defence
                    if whom.health-attack>0:
                        whom.health -= attack
                    else:
                        whom.health = 0
                        self.is_winner = True
                    self.get_entity_effect(who, whom)
                    whom.save(update_fields=['health'])
            else:
                attack = 0
                if self.patterns[rnd] != form.cleaned_data['defence']:
                    attack = return_all_damage_taken(who) - whom.defence
                if whom.health-attack>0:
                    whom.health -= attack
                else:
                    whom.health = 0
                    self.is_winner = False
                self.get_entity_effect(who, whom)
                whom.save(update_fields=['health'])
        else:
            attack = return_all_damage_taken(who)
            if whom.health-attack>0:
                whom.health -= attack
            else:
                whom.health = 0
            whom.save(update_fields=['health'])
        return attack

    def generate_response(self, user: NewUser, log: list[str]):
        if self.is_winner is None:
            response = JsonResponse({
                "enemy_hp": user.enemy.health,
                "user_hp": user.health,
                "user_stats": user.get_summary_stats(),
                "enemy_stats": user.enemy.get_summary_stats(),
                "winner": self.is_winner,
                "log": log
            }, status=200)
        else:
            response = JsonResponse({
                "winner": self.is_winner,
                "redirect_url": reverse("fight_results"),
            }, status=200)
        return response

    def finish_attack(self, request: HttpRequest, user: NewUser, logs: list[str]):
        if self.is_winner is True:
            request.session['winner'] = True
            user.exp += random.randint(1,15)
            user.balance += random.randint(user.dungeon.min_treasure,
                                                   user.dungeon.max_treasure)
            user.save(update_fields=['exp','balance'])
            user.enemy.delete()
        elif self.is_winner is False:
            request.session['winner'] = False
            user.enemy.delete()
        response = self.generate_response(user, logs)
        return response