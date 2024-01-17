from django.db import models
from django.urls import reverse

class DungeonLvl(models.Model):
    min_treasure = models.PositiveIntegerField("MIN Treasure")
    max_treasure = models.PositiveIntegerField("MAX Treasure")
    fine = models.PositiveIntegerField("FINE")
    heal = models.PositiveIntegerField("HEAL")
    min_enemy_stats = models.PositiveIntegerField("MIN_DPS")
    max_enemy_stats = models.PositiveIntegerField("MAX_DPS")
    weapon = models.ForeignKey('Weapon',verbose_name="WEAPON",default=None,null=True,blank=True,on_delete=models.SET_NULL)
    armor = models.ForeignKey('Armor',verbose_name="ARMOR",default=None,null=True,blank=True,on_delete=models.SET_NULL)
    boss = models.ForeignKey("Enemy", verbose_name="BOSS", null=True, blank=True, default=None, on_delete=models.CASCADE)


class Weapon(models.Model):
    name = models.CharField("WEAPON NAME",max_length=30)
    damage = models.IntegerField("DAMAGE+")
    img = models.ImageField("IMG",upload_to="weapon")
    balance = models.IntegerField("SUM")
    lvl = models.IntegerField("LVL")
    dun_lvl = models.IntegerField("DUNGEON LVL")

    def get_absolute_url(self):
        return reverse("buy_w", kwargs={"weapon": self.pk})
    

    def __str__(self):
        return self.name
    

class Armor(models.Model):
    name = models.CharField("ARMOR NAME",max_length=30)
    img = models.ImageField("IMG",upload_to="armor")
    armor = models.IntegerField("AROMOR+")
    balance = models.IntegerField("SUM")
    lvl = models.IntegerField("LVL")
    dun_lvl = models.IntegerField("DUNGEON LVL")

    def get_absolute_url(self):
        return reverse("buy_a", kwargs={"armor": self.pk})

    def __str__(self):
        return self.name


class Effect(models.Model):
    health = models.IntegerField("HP",default=100)
    attack = models.IntegerField("ATTACK",default=1)
    defence = models.IntegerField("ARMOR",default=1)

class Enemy(models.Model):
    name = models.CharField("NAME",max_length=40)
    health = models.IntegerField("HP",default=100)
    attack = models.IntegerField("ATTACK",default=1)
    defence = models.IntegerField("ARMOR",default=1)
    agility = models.IntegerField("AGILITY", default=1)
    strength = models.IntegerField("STRENGTH", default=1)
    lvl = models.IntegerField("LEVEL",default=1)
    role = models.CharField("ROLE", max_length=40, default="strength")
    slug = models.SlugField("URL",unique=True)
    img = models.ImageField("IMG",upload_to="enemy/",default="")

    weapon = models.ForeignKey('Weapon',verbose_name="WEAPON",default=None,null=True,blank=True,on_delete=models.SET_NULL)
    armor = models.ForeignKey('Armor',verbose_name="ARMOR",default=None,null=True,blank=True,on_delete=models.SET_NULL)

    def ReturnAllArmor(self):
        if self.armor is None:
            return self.defence
        else:
            return self.defence+self.armor.armor