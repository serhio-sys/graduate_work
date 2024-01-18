from django.db import models
from django.contrib.auth.models import AbstractUser
from allauth.account.models import EmailAddress
from game.models import Enemy
from django.conf import settings
from django.urls import reverse

class NewUser(AbstractUser):
    health = models.IntegerField("HP",default=100)
    attack = models.IntegerField("ATTACK",default=5)
    defence = models.IntegerField("ARMOR",default=3)
    agility = models.IntegerField("AGILITY", default=1)
    strength = models.IntegerField("STRENGTH", default=1)
    img = models.ImageField("IMG",upload_to="img/",default="")
    balance = models.DecimalField("MONEY", default=100, decimal_places=0,max_digits=10)
    lvl = models.IntegerField("LEVEL",default=1)
    exp = models.IntegerField("EXP",default=0)
    role = models.CharField("ROLE", default=None, max_length=40, blank=True, null=True)
    current_position = models.CharField("POSITION IN THE GAME", max_length=200, blank=True, null=True, default=None)
    weapon = models.ForeignKey('game.Weapon',verbose_name="WEAPON",default='',null=True,blank=True,on_delete=models.SET_NULL)
    armor = models.ForeignKey('game.Armor',verbose_name="ARMOR",default='',null=True,blank=True,on_delete=models.SET_NULL)
    dungeon_lvl = models.IntegerField("DUNGEON LVL",default=1)
    dungeon_loc = models.IntegerField("DUNGEON LOCATION", default=0)
    is_fight = models.BooleanField("IS FIGHT",default=False)
    activated = models.BooleanField("ACTIVATED EMAIL",default=False)
    enemy = models.ForeignKey("game.Enemy",verbose_name="ENEMY",default='',null=True,blank=True,on_delete=models.SET_NULL)
    effect = models.ForeignKey("game.Effect",verbose_name="EFFECT",default='',null=True,blank=True,on_delete=models.SET_NULL)

    def email_verified(self):
        return EmailAddress.objects.filter(user=self, verified=True).exists()

    def ReturnAllDamage(self):
        if self.weapon is None:
            return self.attack
        else:
            return self.attack+self.weapon.damage

    def ReturnAllArmor(self):
        if self.armor is None:
            return self.defence
        else:
            return self.defence+self.armor.armor

    def CheckEXP(self):
        if self.lvl >= 99:
            self.lvl=99
            self.exp=99
        else:
            if self.exp>=100:
                self.lvl+=1
                self.defence=self.defence+1
                self.attack=self.attack+1
                self.exp=0
        self.save()
        return self.lvl

    #def get_absolute_url(self):
    #    return reverse("del", kwargs={"pk": self.pk})

    #def get_absolute_url_upd(self):
    #    return reverse("upd", kwargs={"pk": self.pk})
    
    #def get_absolute_url_sleep(self):
    #    return reverse("sleeping", kwargs={"pk": self.pk})
    
    #def get_absolute_url_fight(self):
    #    return reverse("fight", kwargs={"pk": self.pk})

    #def get_absolute_url_bossfight(self):
    #    return reverse("bossfight", kwargs={"pk": self.pk})

    #def get_absolute_url_bossfight_st(self):
    #    return reverse("bossfight_st", kwargs={"pk": self.pk})

    #def get_absolute_url_urs(self):
    #    return reverse("user", kwargs={"pk": self.pk})

    #def __str__(self):
    #    return self.username

def ReturnAllHealth(obj: NewUser|Enemy) -> int:
    try:
        bonus = settings.ROLE[obj.role]['hp']
        return obj.health+(obj.strength*bonus)
    except KeyError:
        return obj.health

def ReturnAllDamage(obj: NewUser|Enemy) -> int:
    try:
        bonus = settings.ROLE[obj.role]['dmg']
    except KeyError:
        pass
    if obj.weapon is None:
        return obj.attack+(bonus*obj.agility)
    else:
        return obj.attack+(bonus*obj.agility)+obj.weapon.damage
