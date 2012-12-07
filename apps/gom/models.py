from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from math import ceil
from django.db.models.signals import pre_delete, post_save
import profiles.models
import django.contrib.auth.models
import os

# Needed to over-ride ModelChoiceField class
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.html import escape, conditional_escape
from itertools import chain

User.profile = property(lambda u: profiles.models.Profile.objects.get_or_create(user=u)[0])

# Create your models here.

SIZE_CHOICES = (
    # Translators: Scout size class
    (1,  _('Scout')),
    (2,  _('Light')),
    (3,  _('Medium')),
    (4,  _('Heavy')),
    # Translators: Assault size class
    (5,  _('Assault'))
)
RATING_CHOICES = (
    # Translators: 1/5 star card rating
    (1,  _('Bad')),
    # Translators: 2/5 star card rating
    (2,  _('Poor')),
    # Translators: 3/5 star card rating
    (3,  _('OK')),
    # Translators: 4/5 star card rating
    (4,  _('Good')),
    # Translators: 5/5 star card rating
    (5,  _('Great'))
)
INFANTRY_TYPE_CHOICES = (
    (1,  _('Grunt Squad')),
    (2,  _('Squad Attachment')),
    (3,  _('Specialist')),
    (4,  _('Commander'))
)
VEHICLE_TYPE_CHOICES = (
    (11,  _('Tank')),
    # Translators: Mecha vehicle, such as a battle-mech.
    (12,  _('Mecha')),
    # Translators: Ground Support Vehicle
    (13,  _('GSV')),
    # Translators: AIR Support Vehicle
    (14,  _('ASV')),
    (15,  _('Artillery')),
    (16,  _('Vehicle Specialist')),
    # Translators: Air Attack Vehicle
    (17,  _('AAV')),
    (18,  _('Fighter')),
    (19,  _('Super Heavy Tank')),
    (20,  _('Super Heavy Air Support')),
    (30,  _('Monster'))
)
GRUNTZ_TYPE_CHOICES = INFANTRY_TYPE_CHOICES + VEHICLE_TYPE_CHOICES

MOBILITY_FIXED, MOBILITY_WALK, MOBILITY_WALK_MECHA, MOBILITY_TRACK, MOBILITY_WHEEL, MOBILITY_HOVER, MOBILITY_BIKE, MOBILITY_GRAV, MOBILITY_JUMP, MOBILITY_FLIGHT, MOBILITY_HYPER, MOBILITY_HELI, MOBILITY_PROP_VTOL, MOBILITY_JET_VTOL, MOBILITY_PROP, MOBILITY_JET, MOBILITY_AEROSPACE = range(0,17)
CHOICE_MOBILITY_FIXED = (MOBILITY_FIXED, _('Fixed Mount'))
# Translators: Walking mobility type
CHOICE_MOBILITY_WALK = (MOBILITY_WALK, _('Walk'))
# Translators: Walking Mech mobility type
CHOICE_MOBILITY_WALK_MECHA = (MOBILITY_WALK_MECHA, _('Mecha Walk'))
# Translators: Tracked mobility type
CHOICE_MOBILITY_TRACK = (MOBILITY_TRACK,  _('Track'))
# Translators: Wheeled mobility type
CHOICE_MOBILITY_WHEEL = (MOBILITY_WHEEL,  _('Wheels'))
# Translators: Hover mobility type
CHOICE_MOBILITY_HOVER = (MOBILITY_HOVER,  _('Hover'))
CHOICE_MOBILITY_BIKE = (MOBILITY_BIKE, _('Motor-Bike'))
# Translators: Gravity based mobility typ
CHOICE_MOBILITY_GRAV = (MOBILITY_GRAV,  _('Grav'))
CHOICE_MOBILITY_JUMP = (MOBILITY_JUMP,  _('Jump/Glide'))
CHOICE_MOBILITY_FLIGHT = (MOBILITY_FLIGHT,  _('Flight'))
CHOICE_MOBILITY_HYPER = (MOBILITY_HYPER,  _('Hyper-Sonic'))
CHOICE_MOBILITY_HELI = (MOBILITY_HELI, _('Helicopter'))
# Translators: Propeller vertical take off & landing mobility type
CHOICE_MOBILITY_PROP_VTOL = (MOBILITY_PROP_VTOL, _('Prop VTOL'))
# Translators: Jet vertical take off & landing mobility type.
CHOICE_MOBILITY_JET_VTOL = (MOBILITY_JET_VTOL, _('Jet VTOL'))
CHOICE_MOBILITY_PROP = (MOBILITY_PROP, _('Propeller Flight'))
CHOICE_MOBILITY_JET = (MOBILITY_JET, _('Jet Flight'))
CHOICE_MOBILITY_AEROSPACE (MOBILITY_AEROSPACE, _('Aerospace'))

BASIC_MOBILITY_CHOICES = (
    CHOICE_MOBILITY_WALK, CHOICE_MOBILITY_TRACK, CHOICE_MOBILITY_WHEEL, CHOICE_MOBILITY_HOVER, CHOICE_MOBILITY_GRAV )

COMMANDER_MOBILITY_CHOICES = (
    CHOICE_MOBILITY_WALK, CHOICE_MOBILITY_WALK_MECHA, CHOICE_MOBILITY_TRACK, CHOICE_MOBILITY_WHEEL, CHOICE_MOBILITY_HOVER, CHOICE_MOBILITY_GRAV )

VEHICLE_SPEC_MOBILITY_CHOICES = (
    CHOICE_MOBILITY_FIXED, CHOICE_MOBILITY_WALK, CHOICE_MOBILITY_TRACK, CHOICE_MOBILITY_WHEEL, CHOICE_MOBILITY_HOVER, CHOICE_MOBILITY_BIKE, CHOICE_MOBILITY_GRAV )

MONSTER_MOBILITY_CHOICES = (
    CHOICE_MOBILITY_WALK, CHOICE_MOBILITY_JUMP, CHOICE_MOBILITY_FLIGHT, CHOICE_MOBILITY_HYPER )

AIR_MOBILITY_CHOICES = (
    CHOICE_MOBILITY_HELI, CHOICE_MOBILITY_PROP_VTOL, CHOICE_MOBILITY_JET_VTOL, CHOICE_MOBILITY_GRAV )

STAT_CHOICES = (
    (2,  _('Green (2)')),
    (3,  _('Trained (3)')),
    (4,  _('Seasoned (4)')),
    (5,  _('Veteran (5)')),
    (6,  _('Expert (6)')),
    (7,  _('Elite (7)')),
)
MENTAL_CHOICES = (
    (6,  _('Green (6)')),
    (7,  _('Trained (7)')),
    (8,  _('Seasoned (8)')),
    (9,  _('Veteran (9)')),
    (10,  _('Expert (10)')),
    (11,  _('Elite (11)')),
)
GUARD_CHOICES = (
    (10, _('Slow (10)')),
    (11, _('Average (11)')),
    (12, _('Medium (12)')),
    (13, _('Quick (13)')),
    (14, _('Superfast (14)')),
)
SOAK_CHOICES = (
    (10, _('None (10)')),
    (11, _('Scout (11)')),
    (12, _('Light (12)')),
    (13, _('Medium (13)')),
    (14, _('Heavy (14)')),
    (15, _('Assault (15)')),
    (16, _('Vehicle (16)')),
    (17, _('Vehicle (17)')),
    (18, _('Vehicle (18)')),
    (19, _('Vehicle (19)')),
)

WEAPON_TYPE_CHOICES = (
    (-1, _('None')),
    # Translators: Close Combat Weapon
    (0, _('CCW')),
    (1, _('Pistol')),
    (2, _('Rifle')),
    (3, _('Grenade')),
    # Translators: Squad Attachment Weapon
    (4, _('SA')),
    (5, _('Specialist')),
    # Translators: Anti-Infantry weapon
    (6, _('AI')),
    (7, _('Generic Vehicle')),
    (8, _('Medium')),
    (9, _('Heavy')),
    (10, _('Assault')),
    (11, _('Artillery'))
)

MOUNT_TYPE_CHOICES = (
        (0, _('Main Weapon')),
        (1, _('Anti-Infantry')),
        (2, 'Inline')
)

MODZ_AVAILABILITY_CHOICES = (
        (0, _('All')),
        (1, _('Mecha'))
)

MODZ_TYPE_CHOICES = (
    (0, _('Signature')),
    (1, _('Targeting')),
    (2, _('Mobility')),
    (3, _('Armour')),
    (4, _('Repair')),
    (5, _('Anti Infantry'))
)

# Over-ride ModelChoiceField to return weaponSize as well as name, rather than just unicode name
class WeaponChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return (obj.weaponSize, obj.weaponType, obj.weaponName)

class WeaponSelect(forms.Select):
    def render_option(self, selected_choices, option_value, option):
        option_value = force_unicode(option_value)
        selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
        # May not be a tuple if it's the empty value
        if isinstance(option, (list, tuple)):
            weaponSize = option[0]
            weaponType = option[1]
            option_label = option[2]
        else:
            weaponSize = 1
            weaponType = 1
            option_label = option
        return u'<option value="%s" weaponSize="%s" weaponType="%s" %s>%s</option>' % (
            escape(option_value), weaponSize, weaponType, selected_html,
            conditional_escape(force_unicode(option_label)))

    def render_options(self, choices, selected_choices):
        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        for option_value, option_label in chain(self.choices, choices):
            output.append(self.render_option(selected_choices, option_value, option_label))
        return u'\n'.join(output)

class DynamicChoiceField(forms.ChoiceField):
    # Over-ride the validate function so that we can return values that are not in the original choices.
    # Needed for the case where javascript is adding extra options to the selects, due to unit type change.
    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])

class ForceEntry(models.Model):
    force = models.ForeignKey('Force')
    unit = models.ForeignKey('Unit')
    # How many of these units to put in the force
    count = models.SmallIntegerField(default=1, blank=False)
    # Used to order entries in a force. Set to id on first access.
    ordering = models.IntegerField(default=0, blank=True)

    @property
    def order(self): # Shouldn't be needed due to post_save but will leave enabled
        if self.ordering == 0:
            self.ordering == self.id
            self.save()
        return self.ordering

class Force(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ManyToManyField(User, related_name='Force Owner Table', default=None, blank=False)
    description = models.TextField(max_length=300, blank=True)
    # Cost of army
    cost = models.PositiveIntegerField(default=0, blank=True)
    def units(self):
        return ForceEntry.objects.filter(force=self).order_by('ordering')
    def reorder(self, entry, direction):
        try:
            if direction == False: # down
                entries = ForceEntry.objects.filter(force=self, ordering__gt=entry.order).order_by('ordering')
                swap = entries[0]
            else:
                entries = ForceEntry.objects.filter(force=self, ordering__lt=entry.order).order_by('ordering')
                swap = entries[entries.count()-1]
        except IndexError:
            pass
        except Exception, e:
            print 'Re-order exception:', e
        temp = swap.ordering
        swap.ordering = entry.ordering
        entry.ordering = temp
        entry.save()
        swap.save()

    def getCost(self, forceUpdate=False):
        if forceUpdate or self.cost == 0:
            self.updateCost()
        return self.cost
    def updateCost(self):
        print 'updateCost called on %s' % self.name
        cost = 0
        entries = ForceEntry.objects.filter(force=self)
        for entry in entries:
            cost = cost + (entry.unit.cost * entry.count)
        self.cost = cost
        self.save()

class UnitRating(models.Model):
    unit = models.ForeignKey('Unit')
    user = models.ForeignKey(User)
    rating = models.DecimalField(blank=False, decimal_places=2, max_digits=4)

class UnitWeapon(models.Model):
    weapon = models.ForeignKey('Weapons')
    unit = models.ForeignKey('Unit')
    nameOverride = models.CharField(max_length=100, blank=True)
    # Is it a main-weapon or an anti-infantry weapon?
    mountType = models.SmallIntegerField(choices=MOUNT_TYPE_CHOICES, default=0, blank=False)
    def __unicode__(self):
        if self.nameOverride:
            return self.nameOverride
        else:
            return unicode(self.weapon)

class Unit(models.Model):
    name = models.CharField(max_length=100)
    shoot = models.SmallIntegerField(choices=STAT_CHOICES, default=3, blank=False)
    assault = models.SmallIntegerField(choices=STAT_CHOICES, default=3, blank=False)
    guard = models.SmallIntegerField(choices=GUARD_CHOICES, default=12, blank=False)
    soak = models.SmallIntegerField(choices=SOAK_CHOICES, default=12, blank=False)
    mental = models.SmallIntegerField(choices=MENTAL_CHOICES, default=7, blank=False)
    skill = models.SmallIntegerField(choices=STAT_CHOICES, default=3, blank=False)
    weapons = models.ManyToManyField('Weapons', default=None, through='UnitWeapon', blank=True)
    owner = models.ManyToManyField(User, related_name='Owner Table', default=None, blank=False)
    image = models.CharField(max_length=200)
    perks = models.ManyToManyField('Perks', related_name='Perk Table', default=None, blank=True)
    desc = models.TextField(max_length=300, blank=True)
    manu = models.ManyToManyField('Manufacturer', related_name='Manu Table', default=None)
    mobility = models.SmallIntegerField(choices=COMMANDER_MOBILITY_CHOICES, default=1, blank=False)
    size = models.SmallIntegerField(choices=SIZE_CHOICES, default=1, blank=False)
    cost = models.PositiveIntegerField(default=0, blank=True)
    tempInstance = models.BooleanField(default=False)
    creationTime = models.DateTimeField(auto_now_add=True, null=True)
    rating = models.DecimalField(blank=True, decimal_places=2, max_digits=4, default=0)

    unitType = models.SmallIntegerField(choices=GRUNTZ_TYPE_CHOICES, default=1, blank=False)

    # specialist specific fields
    engineerSpecialist = models.BooleanField(default=False, blank=False)
    medicSpecialist = models.BooleanField(default=False, blank=False)

    # vehicle specific fields
    modz = models.ManyToManyField('Modz', related_name='Modz Table', default=None)
    cmdTek = models.BooleanField(default=False, blank=False)

    # Should this unit be published
    publish = models.BooleanField(default=False, blank=False)

    def __unicode__(self):
        s = "Name: %s\n" % self.name
        for weapon in self.weapons.all():
            s = s + repr(weapon)
        return s
    def addRating(self, rating, user):
        if rating=='null':
            print 'Null rating, trying to remove user rating'
            try:
                UnitRating.objects.get(user=user, unit=self).delete()
            except:
                pass
        else:
            try:
                r=UnitRating.objects.get(user=user, unit=self)
                r.rating=rating
            except:
                r = UnitRating(rating=rating, user=user, unit=self)
            r.save()
        self.updateRating()
    def getRating(self):
        return self.rating
    def updateRating(self):
        ratings = UnitRating.objects.filter(unit=self)
        len = ratings.count()
        if len > 0:
            average = 0
            for r in ratings:
                average = average + r.rating
            self.rating = average/len
        else:
            self.rating=0
        print 'updated unit %d rating to %d' % (self.id, self.rating)
        self.save()

    def dumpObject(self, f):
        f.write('g = gom.models.Unit(name="%s", shoot=%d, assault=%d, guard=%d, soak=%d, mental=%d, skill=%d, desc=%s, mobility=%d, size=%d, unitType=%d, image=%s, engineerSpecialist=%s, medicSpecialist=%s, cmdTek=%s)\n' % (self.name, self.shoot, self.assault, self.guard, self.soak, self.mental, self.skill, repr(self.desc), self.mobility, self.size, self.unitType, repr(self.image), self.engineerSpecialist, self.medicSpecialist, self.cmdTek))
        f.write('g.save()\n') # Needed so that we can do below M2M relations
        try:
            f.write('m = gom.models.Manufacturer.objects.get(manuName="%s")\n' % self.manu.get().manuName)
            f.write('g.manu.add(m)\n')
        except:
            pass
        try:
            f.write('import django.contrib.auth.models\n')
            f.write('u = django.contrib.auth.models.User.objects.get(username="%s")\n' % self.owner.get().username)
            f.write('g.owner.add(u)\n')
        except Exception, e:
            pass
        for uw in UnitWeapon.objects.filter(unit=self):
            try:
                f.write('w = gom.models.Weapons.objects.get(weaponName="%s")\n' % uw.weapon.weaponName)
                f.write('wM2M = gom.models.UnitWeapon(weapon=w, unit=g, mountType=%d, nameOverride=%s)\n' % (uw.mountType, repr(uw.nameOverride)))
                f.write('wM2M.save()\n')
            except:
                pass
        for perk in self.perks.all():
            try:
                f.write('p = gom.models.Perks.objects.get(perkName="%s")\n' % perk.perkName)
                f.write('g.perks.add(p)\n')
            except:
                pass
        f.write('g.save()\n')
        
    def isVehicle(self):
        if self.unitType >= 10:
            return True
        return False
    def isInfantry(self):
        return not self.isVehicle()
    def getSoak(self):
        return self.soak
    def getGuard(self):
        return self.guard
    def isPowerArmour(self):
        return self.unitType == 1 and self.soak >= 14
    def inlineCount(self):
        if self.unitType == 1:
            return UnitWeapon.objects.filter(unit=self,mountType=2).count()
        return 0
    def weaponCost(self):
        unitWeaponList = UnitWeapon.objects.filter(unit=self,mountType__in=[0,1])
        total = 0
        for weaponEntry in unitWeaponList:
            # See if it's a SA weapon on a power armour squad
            if self.isPowerArmour() and weaponEntry.weapon.weaponType == 4:
                total = total + (6*weaponEntry.weapon.weaponPoints)
            else:
                total = total + weaponEntry.weapon.weaponPoints
        if self.unitType == 1: # inline squad attachments
            unitInlineList = UnitWeapon.objects.filter(unit=self,mountType=2)
            for weaponEntry in unitInlineList:
                print 'adding new weapon cost and sa entry'
                # Inlude base SA cost for an inline sqad attachement
                total = total + weaponEntry.weapon.weaponPoints +2
        return total
    def getBaseCost(self):
        if self.unitType == 1:
            return 1
        elif self.unitType== 2:
            return 0
        elif self.unitType== 3:
            # Work out if there's any extra engineer or medic cost
            specCost = 0
            if self.engineerSpecialist:
                specCost = 5
            if self.medicSpecialist:
                specCost = specCost + 5
            t=(0,2,4,6,8,10) # includes specialist base cost of 1
            return specCost+t[self.size]
        elif self.unitType == 4:
            t=(13,15,17,19,21) # includes commander base cost of 1
            return t[self.size]
        elif self.unitType == 11:
            t = (0, 14, 19, 24, 29, 34) # Includes base tank cost of 1
        elif self.unitType == 12:
            t = (0, 11, 14, 17, 22, 27) # Includes base mecha cost of 1
        elif self.unitType == 13:
            t = (0, 9, 13, 20, 27, 32) # Includes base GSV cost of 1
        elif self.unitType == 14:
            t = (0, 7, 11, 15, 20, 25) # Includes base ASV cost of 1
        elif self.unitType == 15:
            t = (0, 3, 5, 9, 13, 16) # Includes base artillery cost of 1
        else:
            raise Exception('getBaseCost, unsupported unit type')
        return t[self.size]
    def getDam(self):
        if self.unitType == 1:
            return 6 + self.inlineCount()
        elif self.unitType == 2:
            return 1
        elif self.unitType == 3:
            t=(0,4,5,6,7,8)
        elif self.unitType == 4:
            t=(0,12,14,16,18,20)
        elif self.unitType == 11:
            t = (0, 14, 18, 22, 26, 30)
        elif self.unitType == 12:
            t = (0, 12, 14, 16, 20, 24)
        elif self.unitType == 13:
            t = (0, 10, 12, 16, 20, 22)
        elif self.unitType == 14:
            t = (0, 10, 12, 14, 16, 18)
        elif self.unitType == 15:
            t = (0, 12, 14, 18, 22, 24)
        return t[self.size]
    def getSoak(self):
        if self.unitType == 1 or self.unitType == 2 or self.unitType == 4:
            return self.soak
        elif self.unitType == 3:
            return 11+self.size
        elif self.unitType == 11:
            return 14+self.size
        elif self.unitType == 12 or self.unitType == 15:
            return 13+self.size
        elif self.unitType == 14:
            return 12+self.size
        elif self.unitType == 13:
            t = (0,15,15,16,17,18)
            return t[self.size]
    def getGuard(self):
        if self.unitType == 1 or self.unitType == 2 or self.unitType == 4:
            return self.guard
        elif self.unitType == 3:
            return 15-self.size
        elif self.unitType == 11 or self.unitType == 13 or self.unitType == 15:
            return 14-self.size
        elif self.unitType == 12 or self.unitType == 14:
            return 15-self.size
    def mobilityCost(self):
        if self.unitType == 1 or self.unitType == 2 or self.unitType == 3:
            return 0
        elif self.unitType == 4:
            t = { MOBILITY_WALK:0, MOBILITY_WALK_MECHA:1, MOBILITY_TRACK:3, MOBILITY_WHEEL:5, MOBILITY_HOVER:7, MOBILITY_GRAV:9 }
            cost=t[self.mobility]
        elif self.isVehicle():
            if self.unitType == 12: # MECHA
                return 0
            elif self.unitType == 14: #ASV
                t = (0, 0, 1, 1, 2, 999)
            elif self.unitType == 11: # Tank
                t = { greg
            else:
                t = (0, 0, 1, 1, 2, 3)
            return t[self.mobility]
        else:
            return 0
    def shootCost(self):
        if self.isInfantry() and self.unitType != 2:
            t = {2:0, 3:1, 4:3, 5:5, 6:7, 7:9}
            return t[self.shoot]
        else:
            return 0
    def assaultCost(self):
        if self.isInfantry() and self.unitType != 2:
            t = {2:0, 3:1, 4:3, 5:5, 6:7, 7:9}
            return t[self.assault]
        else:
            return 0
    def guardCost(self):
        if self.unitType in (1,3,4):
            t = {10:1, 11:3, 12:5, 13:7, 14:9}
            return t[int(self.guard)]
        else:
            return 0
    def soakCost(self):
        try:
            if self.unitType in (1,3,4):
                t = {10:0, 11:1, 12:3, 13:5, 14:7, 15:9, 16:11}
                return t[self.soak]
            else:
                return 0
        except Exception, e:
            print 'soakCost exception on unit %d : %s' % (self.id,e)
        return 0
    def mentalCost(self):
        if self.isInfantry() and self.unitType != 2:
            t = {6:0, 7:1, 8:3, 9:5, 10:7, 11:9}
            try:
                return t[self.mental]
            except exception as e:
                print 'mentalCost expection. Did you remember to adjust unit mental range for 1.1?', e
                return 0
        else:
            return 0
    def skillCost(self):
        if self.isVehicle():
            t = {2:0, 3:1, 4:2, 5:5, 6:8, 7:12}
            return t[self.skill]
        elif self.unitType != 2:
            t = {2:0, 3:1, 4:3, 5:5, 6:7, 7:9}
            return t[self.skill]
        else:
            return 0
    def mountCost(self):
        # 0 mount cost for infantry and vehicle specialists
        if self.isInfantry() or self.unitType == 16 :
            return 0
        if self.unitType == 13 or self.unitType == 14:
            # Ensure an exception is thrown if we somehow end up with main weapons
            # on a GSV or ASV
            mainCosts = (0,)
        else:
            mainCosts = (0, 1, 4, 8, 13)
        AICosts = (0, 2, 4)
        mainWeapons = UnitWeapon.objects.filter(unit=self, mountType=0).count()
        AIWeapons = UnitWeapon.objects.filter(unit=self, mountType=1).count()
        print 'mainWeapons:%d, AIWeapons:%d' % (mainWeapons, AIWeapons)
        mountCosts = mainCosts[mainWeapons] + AICosts[AIWeapons]
        return mountCosts
    def perkCost(self):
        if self.isVehicle():
            cost=0
            try:
                cost = cost+self.modz.all()[0].perkCost
                print 'First modz cost %d' % cost
                try:
                    cost = cost + 5 + self.modz.all()[1].perkCost
                    print 'Second perk found, cost:%d' % cost
                except Exception, e:
                    print e
                    pass
                print 'perkCost returning %d' % cost
            except Exception, e:
                pass
            try:
                if (self.unitType == 13 or self.unitType == 14) and self.cmdTek: # ASV or GSV
                    cost=cost+6
            except:
                pass
            return cost
        # Infantry
        if self.unitType != 2: # Not a SA
            try:
                cost = self.perks.all()[0].perkCost
                print 'First perk cost %d' % cost
                try:
                    cost = cost + 5 + self.perks.all()[1].perkCost
                    print 'Second perk found, cost:%d' % cost
                except Exception, e:
                    print e
                    pass
                print 'perkCost returning %d' % cost
                return cost
            except Exception, e:
                pass
        return 0
    def getSpeed(self):
        if self.unitType in (1,2,4):
            return 4 # any modifiers?
        elif self.unitType == 3:
            t={1:4,2:6,3:7,4:8,5:10}
            speed=t[self.mobility]
            return speed
        elif self.unitType in (11,13,15):
            speedArray = ((7,6,6,5,4), (8,7,7,6,6), (9,8,8,7,7), (8,8,7,6,5), (10,9,8,8,7))
            return speedArray[self.mobility-1][self.size-1]
        elif self.unitType == 12:
            t = (0, 7, 6, 6, 5, 4)
        elif self.unitType == 14:
            speedArray = ((10,10,9,8,8), (13,13,12,11,10), (14,14,13,12,11), (15,15,14,13,12))
            return speedArray[self.mobility-1][self.size-1]
        return t[self.size]
    def getSlots(self):
        if self.unitType == 13:
            t=[0,1,1,2,2,4]
            return t[self.size]
        elif self.unitType == 14:
            t=[0,0,0,1,2,3]
            return t[self.size]
        else:
            return 0
    def getRam(self):
        if self.unitType == 12:
            return 6+self.size
        elif self.unitType in (11,13,14,15):
            return 8+self.size
        return 0
    def getCost(self):
        if self.cost == 0:
            self.updateCost()
        return self.cost
    def updateCost(self):
        self.oldCost = self.cost
        print 'base:%d, shoot:%d, assault:%d, guard:%d, soak:%d, mental:%d, skill:%d, weapons:%d, perks:%d, mob:%d, mount:%d' % ( self.getBaseCost(), self.shootCost(), self.assaultCost(), self.guardCost(), self.soakCost(), self.mentalCost(), self.skillCost(), self.weaponCost(), self.perkCost(), self.mobilityCost(), self.mountCost() )
        total = self.getBaseCost() + self.shootCost() + self.assaultCost() + self.guardCost() + self.soakCost() + self.mentalCost() + self.skillCost() + self.weaponCost() + self.perkCost() + self.mobilityCost() + self.mountCost()
        if self.isInfantry():
            halved = int(ceil(total /float(2)))
            print 'total %d, halved %d' % (total, halved)
            self.cost = halved
        else:
            self.cost = total
        if self.cost != self.oldCost:
            self.save()
            # Update costs of any forces that include this unit
            forceEntries = ForceEntry.objects.filter(unit=self)
            checked = []
            # Make sure we only update each force once, even if it includes multiple entries for this unit
            for entry in forceEntries:
                if entry.force.id not in checked:
                    checked.append(entry.force.id)
                    entry.force.updateCost()


class Weapons(models.Model):
    def __unicode__(self):
        return self.weaponName
    weaponName = models.CharField(max_length=100)
    weaponType = models.SmallIntegerField(choices=WEAPON_TYPE_CHOICES)
    weaponSize = models.SmallIntegerField(choices=SIZE_CHOICES, default=1)
    weaponRange = models.SmallIntegerField(default=10)
    weaponDamage = models.SmallIntegerField(default=10)
    weaponAE = models.SmallIntegerField(default=0)
    weaponAP = models.SmallIntegerField(default=0)
    weaponPoints = models.SmallIntegerField(default=999)

class PerksBase(models.Model):
    class Meta:
        abstract = True
    def __unicode__(self):
        return self.perkName
    perkName = models.CharField(max_length=100)
    perkDescription = models.CharField(max_length=300, default='Empty Perk Description')
    perkEffect = models.CharField(max_length=200, default='Empty Perk Effect')
    perkCost = models.SmallIntegerField(default=999)

class Perks(PerksBase):
    pass

class Modz(PerksBase):
    modzType = models.SmallIntegerField(choices=MODZ_TYPE_CHOICES)
    modzAvailability = models.SmallIntegerField(choices=MODZ_AVAILABILITY_CHOICES, default=0)

class Manufacturer(models.Model):
    def __unicode__(self):
        return self.manuName
    manuName = models.CharField(max_length=100)
    manuWeb = models.CharField(max_length=100)

class UnitForm(forms.ModelForm):
    image = forms.ImageField(required=False, label=_('Image'))
    # Grunt Rifles and Pistols only
    basicWeapons = forms.ModelChoiceField(queryset=Weapons.objects.filter(weaponType__gte=1, weaponType__lte=2), required=False)
    SAWeapons = forms.ModelChoiceField(queryset=Weapons.objects.filter(weaponType__in=[1,2,4]), required=False)
    SpecWeapons = forms.ModelChoiceField(queryset=Weapons.objects.filter(weaponType__in=[1,2,4,5]), required=False)
    mainWeapons = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=11).order_by('weaponSize'), required=False, label=_('Main Weapons'), widget=WeaponSelect)
    mainWeapons2 = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=11).order_by('weaponSize'), required=False, widget=WeaponSelect)
    mainWeapons3 = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=11).order_by('weaponSize'), required=False, widget=WeaponSelect)
    mainWeapons4 = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=11).order_by('weaponSize'), required=False, widget=WeaponSelect)
    AIWeapons = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=6).order_by('weaponSize'), required=False, label=_("Anti Infantry"), widget=WeaponSelect)
    AIWeapons2 = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=6).order_by('weaponSize'), required=False, widget=WeaponSelect)
    inlineWeapons = forms.ModelChoiceField(queryset=Weapons.objects.filter(weaponType__in=[1,2,4]), required=False)
    inlineWeapons2 = forms.ModelChoiceField(queryset=Weapons.objects.filter(weaponType__in=[1,2,4]), required=False)
    # Grunt CCWs only
    CCW = forms.ModelChoiceField(queryset=Weapons.objects.filter(weaponType=0), required=False, empty_label=None, label=_('CCW'))
    # Grunt grenades only
    grenades = forms.ModelChoiceField(queryset=Weapons.objects.filter(weaponType=3), required=False, label=_('Grenade'))
    # Translators: Label for User customisable weapon name box.
    MW_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    MW2_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    MW3_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    MW4_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    AI_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    AI2_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    basic_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    SA_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    Spec_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    inline_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    inline2_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    CCW_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    grenades_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    OR_MW = forms.BooleanField(required=False)
    OR_MW2 = forms.BooleanField(required=False)
    OR_MW3 = forms.BooleanField(required=False)
    OR_MW4 = forms.BooleanField(required=False)
    OR_AI = forms.BooleanField(required=False)
    OR_AI2 = forms.BooleanField(required=False)
    OR_basic = forms.BooleanField(required=False)
    OR_SA = forms.BooleanField(required=False)
    OR_Spec = forms.BooleanField(required=False)
    OR_CCW = forms.BooleanField(required=False)
    OR_grenades = forms.BooleanField(required=False)
    OR_inline = forms.BooleanField(required=False)
    OR_inline2 = forms.BooleanField(required=False)
    perks = forms.ModelChoiceField(queryset=Perks.objects.all().order_by('perkName'), required=False, label=_("Perk"))
    perks2 = forms.ModelChoiceField(queryset=Perks.objects.all().order_by('perkName'), required=False, label=_("Perk 2"))
    modz = forms.ModelChoiceField(queryset=Modz.objects.filter(modzAvailability=0), required=False) # Add mecha modz for mechas
    modz2 = forms.ModelChoiceField(queryset=Modz.objects.filter(modzAvailability=0), required=False) # Add mecha modz for mechas
    manu = forms.ModelChoiceField(queryset=Manufacturer.objects.all().order_by('manuName'), required=False)
    # Use a DynamicChoiceField so that we will accept values outside of GUARD_CHOICES. Needed for assault class tanks.
    guard = DynamicChoiceField(required=True, choices=GUARD_CHOICES)
    air_mobility = forms.ChoiceField(choices=AIR_MOBILITY_CHOICES, required=False, label=_("Air Mobility"))
    commander_mobility = forms.ChoiceField(choices=COMMANDER_MOBILITY_CHOICES, required=False, label=_("Commander Mobility"))

    class Meta:
        model = Unit
        fields = ['id', 'name', 'unitType', 'size', 'shoot', 'assault', 'soak', 'mental', 'skill', 'mobility', 'desc', 'engineerSpecialist', 'medicSpecialist', 'cmdTek', 'publish' ]
    def __init__(self, *args, **kwargs):
        super(UnitForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            print kwargs['instance'].weapons.all()
            try:
                basic_instance = UnitWeapon.objects.filter(unit=kwargs['instance'], weapon__weaponType__gte=1, weapon__weaponType__lte=2, mountType=0).all()[0]
                self.fields['basicWeapons'].initial=basic_instance.weapon
                if basic_instance.nameOverride:
                    self.fields['basic_Custom'].initial=basic_instance.nameOverride
                    self.fields['OR_basic'].initial=True
            except (ObjectDoesNotExist, IndexError):
                pass
            try:
                SA_instance = UnitWeapon.objects.filter(unit=kwargs['instance'], weapon__weaponType__in=[1,2,4], mountType=0).all()[0]
                self.fields['SAWeapons'].initial=SA_instance.weapon
                if SA_instance.nameOverride:
                    self.fields['SA_Custom'].initial=SA_instance.nameOverride
                    self.fields['OR_SA'].initial=True
            except (ObjectDoesNotExist, IndexError):
                pass
            try:
                Spec_instance = UnitWeapon.objects.filter(unit=kwargs['instance'], weapon__weaponType__in=[1,2,4,5], mountType=0).all()[0]
                self.fields['SpecWeapons'].initial=Spec_instance.weapon
                if Spec_instance.nameOverride:
                    self.fields['Spec_Custom'].initial=Spec_instance.nameOverride
                    self.fields['OR_Spec'].initial=True
            except (ObjectDoesNotExist, IndexError):
                pass
            try:
                CCW_instance = UnitWeapon.objects.filter(unit=kwargs['instance'], weapon__weaponType=0, mountType=0).get()
                self.fields['CCW'].initial=CCW_instance.weapon
                if CCW_instance.nameOverride:
                    self.fields['CCW_Custom'].initial=CCW_instance.nameOverride
                    self.fields['OR_CCW'].initial=True
            except ObjectDoesNotExist:
                pass
            try:
                grenades_instance = UnitWeapon.objects.filter(unit=kwargs['instance'], weapon__weaponType=3, mountType=0).get()
                self.fields['grenades'].initial=grenades_instance.weapon
                if grenades_instance.nameOverride:
                    self.fields['grenades_Custom'].initial=grenades_instance.nameOverride
                    self.fields['OR_grenades'].initial=True
            except ObjectDoesNotExist:
                pass
            try:
                mainWeapons = UnitWeapon.objects.filter(unit=kwargs['instance'], mountType=0)
                self.fields['mainWeapons'].initial=mainWeapons[0].weapon
                if mainWeapons[0].nameOverride:
                    self.fields['MW_Custom'].initial=mainWeapons[0].nameOverride
                    self.fields['OR_MW'].initial=True
                self.fields['mainWeapons2'].initial=mainWeapons[1].weapon
                if mainWeapons[1].nameOverride:
                    self.fields['MW2_Custom'].initial=mainWeapons[1].nameOverride
                    self.fields['OR_MW2'].initial=True
                self.fields['mainWeapons3'].initial=mainWeapons[2].weapon
                if mainWeapons[2].nameOverride:
                    self.fields['MW3_Custom'].initial=mainWeapons[2].nameOverride
                    self.fields['OR_MW3'].initial=True
                self.fields['mainWeapons4'].initial=mainWeapons[3].weapon
                if mainWeapons[3].nameOverride:
                    self.fields['MW4_Custom'].initial=mainWeapons[3].nameOverride
                    self.fields['OR_MW4'].initial=True
            except IndexError:
                pass
            try:
                AIWeapons = UnitWeapon.objects.filter(unit=kwargs['instance'], mountType=1)
                self.fields['AIWeapons'].initial=AIWeapons[0].weapon
                if AIWeapons[0].nameOverride:
                    self.fields['AI_Custom'].initial=AIWeapons[0].nameOverride
                    self.fields['OR_AI'].initial=True
                self.fields['AIWeapons2'].initial=AIWeapons[1].weapon
                if AIWeapons[1].nameOverride:
                    self.fields['AI2_Custom'].initial=AIWeapons[1].nameOverride
                    self.fields['OR_AI2'].initial=True
            except IndexError:
                pass
            try:
                inlineWeapons = UnitWeapon.objects.filter(unit=kwargs['instance'], mountType=2)
                self.fields['inlineWeapons'].initial=inlineWeapons[0].weapon
                if inlineWeapons[0].nameOverride:
                    self.fields['inline_Custom'].initial=inlineWeapons[0].nameOverride
                    self.fields['OR_inline'].initial=True
                self.fields['inlineWeapons2'].initial=inlineWeapons[1].weapon
                if inlineWeapons[1].nameOverride:
                    self.fields['inline2_Custom'].initial=inlineWeapons[1].nameOverride
                    self.fields['OR_inline2'].initial=True
            except IndexError:
                pass
            try:
                self.fields['perks'].initial=kwargs['instance'].perks.all()[0]
            except IndexError:
                pass
            try:
                self.fields['perks2'].initial=kwargs['instance'].perks.all()[1]
            except IndexError:
                pass
            try:
                self.fields['modz'].initial=kwargs['instance'].modz.all()[0]
            except IndexError:
                pass
            try:
                self.fields['modz2'].initial=kwargs['instance'].modz.all()[1]
            except IndexError:
                pass
            try:
                self.fields['manu'].initial=kwargs['instance'].manu.get()
            except ObjectDoesNotExist:
                pass
            try:
                self.fields['medicSpecialist'].initial=kwargs['instance'].medicSpecialist
            except Exception, e:
                print 'MedicSpecialist exception:', e
                pass
            try:
                self.fields['guard'].initial=kwargs['instance'].getGuard()
            except Exception, e:
                print "guard exception", e
                pass
            try:
                self.fields['engineerSpecialist'].initial=kwargs['instance'].engineerSpecialist
            except Exception, e:
                print "engineer exception", e
                pass
            try:
                if kwargs['instance'].unitType == 14: #ASV
                    self.fields['air_mobility'].initial = kwargs['instance'].mobility
            except Exception, e:
                print "air mobility exception", e
                pass
        else:
            print 'no unit instance'

class ForceForm(forms.ModelForm):
    class Meta:
        model = Force
        fields = ['name', 'description', 'cost']

def unitDump():
    f = open('/tmp/gomDump', 'w')
    for u in Unit.objects.all():
        u.dumpObject(f)
    f.close()

def force_entry_postsave(sender, **kwargs):
    obj = kwargs['instance']
    if obj.ordering == 0:
        obj.ordering = obj.id
        obj.save()

def force_predelete(sender, **kwargs):
    # the object which is about to be deleted can be accessed via the kwargs 'instance' key.
    obj = kwargs['instance']
    # Find any ForceEntry objects related to this force and delete them
    try:
        entries = ForceEntry.objects.filter(force=obj)
        for entry in entries:
            entry.delete()
    except Exception, e:
        print 'ForceEntry deletion on force deletion failed:', e

def unit_predelete(sender, **kwargs):
    # the object which is about to be deleted can be accessed via the kwargs 'instance' key.
    obj = kwargs['instance']
    # See if this is the only unit belonging to this user using this image file.
    # If so, delete the image file.
    if obj.image:
        try:
            sameImageCount = Unit.objects.filter(image=obj.image, owner=obj.owner.get()).count()
            print 'sameImage count is %d' % sameImageCount
            if sameImageCount < 2: # No other objects have this image
                os.remove('user_media/%d/%s' % (obj.owner.get().id, obj.image))
        except Exception, e:
            print 'unit_predelete exception: %s' % e

    # see if there are any force entries using this unit. If so, delete them
    try:
        print 'attempting delete of this object from any forces'
        entries = ForceEntry.objects.filter(unit=obj)
        print entries
        forceList = []
        for entry in entries:
            # Keep note of which forces had this entry, so we can update their cost after this loop
            if entry.force not in forceList:
                forceList.append(entry.force)
            entry.delete()
        for force in forceList:
            force.updateCost()
    except Exception, e:
        print e

# Set up unit_predelete method to be called whenever a Unit or its subclass is about to be deleted.
# Use this to delete any image files no longer needed.
pre_delete.connect(unit_predelete, sender=Unit)
# pre-delete method to remove any relevant force entry objects when a force is deleted
pre_delete.connect(force_predelete, sender=Force)
# Use to set initial ForceEntry ordering value to be equal to id, which is only available after saving
post_save.connect(force_entry_postsave, sender=ForceEntry)
