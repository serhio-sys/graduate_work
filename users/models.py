from django.db import models
from django.contrib.auth.models import AbstractUser
from allauth.account.models import EmailAddress
from game.models import Enemy
from django.contrib.sites.models import Site
from django.conf import settings
from django.urls import reverse
import random
import datetime


class NewUser(AbstractUser):
    health = models.IntegerField("HP", default=100)
    attack = models.IntegerField("ATTACK", default=5)
    defence = models.IntegerField("ARMOR", default=3)
    agility = models.IntegerField("AGILITY", default=1)
    strength = models.IntegerField("STRENGTH", default=1)
    upgrade_points = models.PositiveIntegerField("UPGRADE POINTS", default=0)
    img = models.ImageField("IMG", upload_to="img/", default=None, null=True, blank=True)
    balance = models.DecimalField("MONEY", default=100, decimal_places=0, max_digits=10)
    lvl = models.IntegerField("LEVEL", default=1)
    exp = models.IntegerField("EXP", default=0)
    role = models.CharField("ROLE", default=None, max_length=40, blank=True, null=True)
    current_position = models.CharField("POSITION IN THE GAME", max_length=200, blank=True, null=True, default=None)
    weapon_equiped = models.ForeignKey('game.Weapon', verbose_name="WEAPON", default=None, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='equipped_weapon_user')
    armor_equiped = models.ForeignKey('game.Armor', verbose_name="ARMOR", default=None, null=True, blank=True,
                                      on_delete=models.SET_NULL, related_name='equipped_armor_user')
    weapon2_equiped = models.ForeignKey('game.Weapon', verbose_name="SEC WEAPON", default=None, null=True, blank=True,
                                        on_delete=models.SET_NULL, related_name='equipped_weapon2_user')
    dungeon = models.ForeignKey("game.DungeonLvl", default=None, null=True, blank=True, on_delete=models.SET_NULL)
    is_fight = models.BooleanField("IS FIGHT", default=False)
    enemy = models.ForeignKey("game.Enemy", verbose_name="ENEMY", default=None, null=True, blank=True,
                              on_delete=models.SET_NULL)

    def email_verified(self):
        return EmailAddress.objects.filter(user=self, verified=True).exists()

    def get_class_img(self):
        url = f"{settings.PROTOCOL}://127.0.0.1:8000"
        return url + "/static/img/classes/" + settings.ROLES[self.role]['img']

    def get_max_hp(self):
        bonus = settings.ROLES[self.role]['hp']
        return 100 + (self.strength * bonus)

    def get_current_hp(self):
        bonus = settings.ROLES[self.role]['hp']
        return self.health + (self.strength * bonus)

    def return_all_damage(self):
        bonus = settings.ROLES[self.role]['dmg']
        attack = self.attack + (self.agility * bonus)
        if self.weapon_equiped is None and self.weapon2_equiped is None:
            return attack
        if self.weapon_equiped:
            bonus += self.weapon_equiped.damage
        if self.weapon2_equiped:
            bonus += self.weapon2_equiped.damage
        return attack + bonus

    def return_all_armor(self) -> int:
        bonus = settings.ROLES[self.role]['dmg']
        defence = self.defence + round(self.agility * bonus)
        if self.armor_equiped is None:
            return defence
        else:
            return defence + self.armor_equiped.armor

    def get_summary_damage(self) -> dict:
        bonus = round(self.agility * settings.ROLES[self.role]['dmg'], 1)
        if self.weapon_equiped is None and self.weapon2_equiped is None:
            return {"hero": self.attack, "bonus": bonus, "total": self.attack + bonus}
        if self.weapon_equiped:
            bonus += self.weapon_equiped.damage
        if self.weapon2_equiped:
            bonus += self.weapon2_equiped.damage
        return {"hero": self.attack, "bonus": bonus, "total": self.attack + bonus}

    def get_summary_stats(self) -> dict:
        total_str = self.strength
        total_ag = self.agility
        effects = self.effect_set.all()
        effects_to_delete = [effect for effect in effects if effect.deleted_time <= datetime.datetime.now()]

        for effect in effects_to_delete:
            effect.delete()
        active_effects = [effect for effect in effects if effect not in effects_to_delete]
        sum_str = sum(effect.strength for effect in active_effects)
        sum_ag = sum(effect.agility for effect in active_effects)

        return {
            "str": {"hero": total_str, "sum": sum_str, "total": total_str + sum_str if total_str + sum_str >= 0 else 0},
            "ag": {"hero": total_ag, "sum": sum_ag, "total": total_ag + sum_ag if total_ag + sum_ag >= 0 else 0},
            "effects": active_effects}

    def CheckEXP(self):
        if self.lvl >= 99 and self.exp > 99:
            self.lvl = 99
            self.exp = 99
            self.save(update_fields=['lvl', 'exp'])
        else:
            if self.exp >= 100:
                self.lvl += 1
                self.upgrade_points = self.upgrade_points + 3
                self.exp = 0
                self.save(update_fields=['lvl', 'exp', 'upgrade_points'])
        return self.lvl

    # def get_absolute_url(self):
    #    return reverse("del", kwargs={"pk": self.pk})

    # def get_absolute_url_upd(self):
    #    return reverse("upd", kwargs={"pk": self.pk})

    # def get_absolute_url_sleep(self):
    #    return reverse("sleeping", kwargs={"pk": self.pk})

    # def get_absolute_url_fight(self):
    #    return reverse("fight", kwargs={"pk": self.pk})

    # def get_absolute_url_bossfight(self):
    #    return reverse("bossfight", kwargs={"pk": self.pk})

    # def get_absolute_url_bossfight_st(self):
    #    return reverse("bossfight_st", kwargs={"pk": self.pk})

    # def get_absolute_url_urs(self):
    #    return reverse("user", kwargs={"pk": self.pk})

    # def __str__(self):
    #    return self.username


def return_all_health(obj: NewUser | Enemy) -> int:
    bonus = settings.ROLES[obj.role]['hp']
    return obj.health + (obj.strength * bonus)


def return_all_damage_taken(obj: NewUser | Enemy) -> int:
    bonus = settings.ROLES[obj.role]['dmg']
    if obj.weapon is None:
        attack = obj.attack + (bonus * obj.agility)
    else:
        attack = obj.attack + (bonus * obj.agility) + obj.weapon_equiped.damage
    if settings.ROLES[obj.role]['double_dmg']:
        if random.randint(100) <= 10:
            return attack * 1.8
    return attack
