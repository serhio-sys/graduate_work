import random
import datetime
from django.shortcuts import redirect
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.forms import model_to_dict
from users.models import NewUser, return_all_damage_taken
from .services import get_select_classview, get_with_user_context,\
    post_select_classview, get_inventory_classview, \
    post_church, post_equip_armor, post_equip_weapon, get_buy_armor, get_buy_weapon,\
    BasedDungeon
from .models import Weapon, Armor, Enemy, Effect
from .forms import UserIncreaseStatsForm, AttackForm
from .logs import select_log, get_text_effect


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
    if request.user.enemy is not None:
        return redirect("fight")
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
        response.context_data.update({"form": form})
        return response.render()


class DungeonEnterenceView(LoginRequiredMixin, View):
    template_name = "game/dungeon/dungeon.html"

    def get(self, request: HttpRequest):
        return get_with_user_context(request=request, template_name=self.template_name).render()


class DungeonView(BasedDungeon, LoginRequiredMixin, View):
    template_name = "game/dungeon/dungeon_inside.html"

    def get(self, request: HttpRequest):
        if random.randint(1,100) < request.session.get('fight_posibility', -1):
            request.session['enemy_first'] = True
            return redirect('fight')
        request.session['fight_posibility'] = -1
        response = self.get_based_response(request=request)
        return response.render()

class DungeonEnemyView(DungeonView):
    template_name = "game/dungeon/dungeon_enemy.html"

    def get(self, request: HttpRequest):
        response = self.get_based_response(request=request)
        response.template_name = self.template_name
        request.session['fight_posibility'] = 40
        request.session["x"], request.session["y"] = self.x, self.y
        return response.render()

    def post(self, request: HttpRequest):
        request.session['enemy_first'] = False
        return redirect("fight")

class FightResultsView(LoginRequiredMixin, View):
    template_name = "game/fight/fight_results.html"

    def get(self, request: HttpRequest):
        response = get_with_user_context(request=request, template_name=self.template_name)
        return response.render()


class FightView(LoginRequiredMixin, View):
    template_name = "game/fight/fight.html"
    enemy = None
    is_winner = None
    logs = []
    patterns = ['head','leg','body']

    
    def initial_enemy(self, user:NewUser):
        if user.enemy is None:
            enemies = Enemy.objects.filter(dungeon__lvl = user.dungeon.lvl, is_boss = False)
            user.enemy = Enemy.objects.create(
                **model_to_dict(enemies[random.randint(0,len(enemies)-1)], exclude=['id','dungeon'])
                )
            user.save(update_fields=['enemy'])
            self.enemy = user.enemy
        else:
            self.enemy = user.enemy

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

    def generate_response(self, request: HttpRequest, log: list[str]):
        if self.is_winner is None:
            response = JsonResponse({
                "enemy_hp": self.enemy.health,
                "user_hp": request.user.health,
                "user_stats": request.user.get_summary_stats(),
                "enemy_stats": self.enemy.get_summary_stats(),
                "winner": self.is_winner,
                "log": log
            }, status=200)
        else:
            response = JsonResponse({
                "winner": self.is_winner,
                "redirect_url": reverse("fight_results"),
            }, status=200)
        return response

    def finish_attack(self, request: HttpRequest, logs: list[str]):
        print(self.is_winner)
        if self.is_winner is True:
            request.session['winner'] = True
            request.user.exp += random.randint(1,15)
            request.user.balance += random.randint(request.user.dungeon.min_treasure,
                                                   request.user.dungeon.max_treasure)
            request.user.save(update_fields=['exp','balance'])
            request.user.enemy.delete()
        elif self.is_winner is False:
            request.session['winner'] = False
            request.user.enemy.delete()
        response = self.generate_response(request, logs)
        return response

    def get(self, request: HttpRequest):
        self.initial_enemy(request.user)
        request.session['fight_posibility'] = -1
        if request.session.get('enemy_first', False):
            self.attack(request, self.enemy, request.user)
            request.session['enemy_first'] = False
        response = get_with_user_context(request=request, template_name=self.template_name)
        response.context_data.update(
            {
                "form": AttackForm(),
                "enemy": self.enemy,
                "effects": request.user.get_summary_stats(),
                "enemy_effects": self.enemy.get_summary_stats()
            }
        )
        return response.render()
    
    def post(self, request: HttpRequest):
        self.initial_enemy(request.user)
        if self.enemy.role == "agility":
            if random.randint(0,100) < 5:
                dmg = self.attack(request, self.enemy, request.user)
                self.logs.append(select_log(dmg)(self.enemy.name, 
                                                 request.user.username, 
                                                 type="agility", dmg=dmg))
                response = self.finish_attack(request, self.logs)
                return response
        elif self.enemy.role == "shooter":
            if random.randint(0,100) < 10:
                dmg = self.attack(request, self.enemy, request.user)
                self.logs.append(select_log(dmg)(self.enemy.name, 
                                                 request.user.username, 
                                                 type="shooter", dmg=dmg))
                response = self.finish_attack(request, self.logs)
                return response
        if self.request.user.role == "agility":
            if random.randint(0,100) < 5:
                dmg = self.attack(request, request.user, self.enemy)
                self.logs.append(select_log(dmg)(request.user.username, 
                                                 self.enemy.name, 
                                                 type="agility", dmg=dmg))  
                response = self.finish_attack(request, self.logs)
                return response
        elif self.request.user.role == "shooter":
            if random.randint(0,100) < 10:
                dmg = self.attack(request, request.user, self.enemy)
                self.logs.append(select_log(dmg)(request.user.username, 
                                                 self.enemy.name, 
                                                 type="shooter", dmg=dmg))                
                response = self.finish_attack(request, self.logs)
                return response
        dmg = self.attack(request, request.user, self.enemy)
        self.logs.append(select_log(dmg)(request.user.username, self.enemy.name, dmg=dmg))                    
        dmg = self.attack(request, self.enemy, request.user)
        self.logs.append(select_log(dmg)(self.enemy.name, request.user.username, dmg=dmg))                  
        response = self.finish_attack(request, self.logs)
        return response
                