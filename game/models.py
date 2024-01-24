from django.db import models
from django.urls import reverse


class DungeonLvl(models.Model):
    lvl = models.PositiveIntegerField("DUNGEON LVL")
    min_treasure = models.PositiveIntegerField("MIN Treasure")
    max_treasure = models.PositiveIntegerField("MAX Treasure")
    fine = models.PositiveIntegerField("FINE")
    heal = models.PositiveIntegerField("HEAL")
    map = models.FileField(upload_to="maps/", default="maps/map1.json")
    unlock_lvl = models.PositiveIntegerField("LVL FOR UNLOCK BOSS")


class Weapon(models.Model):
    name = models.CharField("WEAPON NAME", max_length=30)
    damage = models.IntegerField("DAMAGE+")
    img = models.ImageField("IMG", upload_to="weapon")
    balance = models.IntegerField("SUM")
    lvl = models.IntegerField("LVL")
    dun_lvl = models.IntegerField("DUNGEON LVL")
    user = models.ForeignKey("users.NewUser", verbose_name="Owner", default=None, null=True, blank=True,
                             on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse("buy_w", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Armor(models.Model):
    name = models.CharField("ARMOR NAME", max_length=30)
    img = models.ImageField("IMG", upload_to="armor")
    armor = models.IntegerField("AROMOR+")
    balance = models.IntegerField("SUM")
    lvl = models.IntegerField("LVL")
    dun_lvl = models.IntegerField("DUNGEON LVL")
    user = models.ForeignKey("users.NewUser", verbose_name="Owner", default=None, null=True, blank=True,
                             on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse("buy_a", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class Effect(models.Model):
    name = models.CharField("NAME", max_length=50, default="")
    desc = models.TextField("Desc")
    is_positive = models.BooleanField("IS_POSITIVE", default=True)
    is_church_ef = models.BooleanField("IS CHURCH EFFECT", default=False)
    agility = models.IntegerField("AGILITY", default=1)
    strength = models.IntegerField("STRENGTH", default=1)
    user = models.ForeignKey("users.NewUser", default=None, null=True, blank=True, on_delete=models.SET_NULL)
    deleted_time = models.DateTimeField("DELETED TIME", default=None, null=True, blank=True)


class Enemy(models.Model):
    name = models.CharField("NAME", max_length=40)
    health = models.IntegerField("HP", default=100)
    attack = models.IntegerField("ATTACK", default=1)
    defence = models.IntegerField("ARMOR", default=1)
    agility = models.IntegerField("AGILITY", default=1)
    strength = models.IntegerField("STRENGTH", default=1)
    lvl = models.IntegerField("LEVEL", default=1)
    role = models.CharField("ROLE", max_length=40, default="strength")
    slug = models.SlugField("URL", unique=True)
    img = models.ImageField("IMG", upload_to="enemy/", default="")
    is_boss = models.BooleanField("IS_BOSS", default=False),
    weapon_equiped = models.ForeignKey('game.Weapon', verbose_name="WEAPON", default=None, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='equipped_weapon_enemy')
    armor_equiped = models.ForeignKey('game.Armor', verbose_name="ARMOR", default=None, null=True, blank=True,
                                      on_delete=models.SET_NULL, related_name='equipped_armor_enemy')
    weapon2_equiped = models.ForeignKey('game.Weapon', verbose_name="SEC WEAPON", default=None, null=True, blank=True,
                                        on_delete=models.SET_NULL, related_name='equipped_weapon2_enemy')
    dungeon = models.ForeignKey('DungeonLvl', default=None, null=True, blank=True, on_delete=models.SET_NULL)

    def ReturnAllArmor(self):
        if self.armor is None:
            return self.defence
        else:
            return self.defence + self.armor.armor
