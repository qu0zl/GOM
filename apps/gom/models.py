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
SQUAD_SIZE_CHOICES = map ( (lambda x,y: (x,y)), range(1,31), range(1,31))

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

GRUNT, SA, SPEC, COMMANDER = range(1,5)
INFANTRY_TYPE_CHOICES = (
    (GRUNT,  _('Grunt Squad')),
    (SA,  _('Squad Attachment')),
    (SPEC,  _('Specialist')),
    (COMMANDER,  _('Commander'))
)
TANK, MECHA, GSV, ASV, ARTI, VSPEC, FIELD_ARTI, AAV, FIGHTER, SHT, SHAS, MONSTER = range(11,23)
VEHICLE_TYPE_CHOICES = (
    (TANK,  _('Tank')),
    # Translators: Mecha vehicle, such as a battle-mech.
    (MECHA,  _('Mecha')),
    # Translators: Ground Support Vehicle
    (GSV,  _('GSV')),
    # Translators: AIR Support Vehicle
    (ASV,  _('ASV')),
    (ARTI,  _('Artillery')),
    (VSPEC,  _('Vehicle Specialist')),
    (FIELD_ARTI,  _('Field Artillery')),
    # Translators: Air Attack Vehicle
    (AAV,  _('AAV')),
    (FIGHTER,  _('Fighter')),
    (SHT,  _('Super Heavy Tank')),
    (SHAS,  _('Super Heavy Air Support')),
    (MONSTER,  _('Monster'))
)

GRUNTZ_TYPE_CHOICES = INFANTRY_TYPE_CHOICES + VEHICLE_TYPE_CHOICES

MOBILITY_FIXED, MOBILITY_WALK, MOBILITY_WALK_MECHA, MOBILITY_TRACK, MOBILITY_WHEEL, MOBILITY_HOVER, MOBILITY_BIKE, MOBILITY_GRAV, MOBILITY_JUMP, MOBILITY_FLIGHT, MOBILITY_HYPER, MOBILITY_HELI, MOBILITY_PROP_VTOL, MOBILITY_JET_VTOL, MOBILITY_PROP, MOBILITY_JET, MOBILITY_AEROSPACE, MOBILITY_TOWED, MOBILITY_WALK_QUAD = range(0,19)
CHOICE_MOBILITY_FIXED = (MOBILITY_FIXED, _('Fixed Mount'))
# Translators: Walking mobility type
CHOICE_MOBILITY_WALK = (MOBILITY_WALK, _('Walk'))
# Translators: Quadrupedal walk mobility type
CHOICE_MOBILITY_WALK_QUAD = (MOBILITY_WALK_QUAD, _('Quadruped Walk'))
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
# Translators: Propeller based flight.
CHOICE_MOBILITY_PROP = (MOBILITY_PROP, _('Prop. Flight'))
CHOICE_MOBILITY_JET = (MOBILITY_JET, _('Jet Flight'))
CHOICE_MOBILITY_AEROSPACE = (MOBILITY_AEROSPACE, _('Aerospace'))
# Translators: Towed (eg by another vehicle)
CHOICE_MOBILITY_TOWED = (MOBILITY_TOWED, _('Towed'))

ALL_MOBILITY_CHOICES = (CHOICE_MOBILITY_FIXED, CHOICE_MOBILITY_WALK, CHOICE_MOBILITY_WALK_MECHA, CHOICE_MOBILITY_TRACK, CHOICE_MOBILITY_WHEEL, CHOICE_MOBILITY_HOVER, CHOICE_MOBILITY_BIKE, CHOICE_MOBILITY_GRAV, CHOICE_MOBILITY_JUMP, CHOICE_MOBILITY_FLIGHT, CHOICE_MOBILITY_HYPER, CHOICE_MOBILITY_HELI, CHOICE_MOBILITY_PROP_VTOL, CHOICE_MOBILITY_JET_VTOL, CHOICE_MOBILITY_PROP, CHOICE_MOBILITY_JET, CHOICE_MOBILITY_AEROSPACE, CHOICE_MOBILITY_WALK_QUAD, CHOICE_MOBILITY_TOWED)
BASIC_MOBILITY_CHOICES = (
    CHOICE_MOBILITY_WALK, CHOICE_MOBILITY_TRACK, CHOICE_MOBILITY_WHEEL, CHOICE_MOBILITY_HOVER, CHOICE_MOBILITY_GRAV )

COMMANDER_MOBILITY_CHOICES = (
    CHOICE_MOBILITY_WALK, CHOICE_MOBILITY_WALK_MECHA, CHOICE_MOBILITY_TRACK, CHOICE_MOBILITY_WHEEL, CHOICE_MOBILITY_HOVER, CHOICE_MOBILITY_GRAV )

VEHICLE_SPEC_MOBILITY_CHOICES = (
    CHOICE_MOBILITY_FIXED, CHOICE_MOBILITY_WALK_MECHA, CHOICE_MOBILITY_TRACK, CHOICE_MOBILITY_WHEEL, CHOICE_MOBILITY_HOVER, CHOICE_MOBILITY_BIKE, CHOICE_MOBILITY_GRAV )

MONSTER_MOBILITY_CHOICES = (
    CHOICE_MOBILITY_WALK, CHOICE_MOBILITY_WALK_QUAD, CHOICE_MOBILITY_JUMP, CHOICE_MOBILITY_FLIGHT, CHOICE_MOBILITY_HYPER )

AIR_MOBILITY_CHOICES = (
    CHOICE_MOBILITY_HELI, CHOICE_MOBILITY_PROP_VTOL, CHOICE_MOBILITY_JET_VTOL, CHOICE_MOBILITY_GRAV )

FIGHTER_MOBILITY_CHOICES = (
        CHOICE_MOBILITY_PROP_VTOL, CHOICE_MOBILITY_JET_VTOL, CHOICE_MOBILITY_PROP, CHOICE_MOBILITY_JET, CHOICE_MOBILITY_AEROSPACE)

FIELD_ARTI_MOBILITY_CHOICES = (
        CHOICE_MOBILITY_FIXED, CHOICE_MOBILITY_TOWED, CHOICE_MOBILITY_WALK, CHOICE_MOBILITY_HOVER, CHOICE_MOBILITY_GRAV )

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
    (11, _('Artillery')),
    (12, _('Bomb'))
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
    (5, _('Anti Infantry')),
    (6, _('Assault'))
)

# Over-ride ModelChoiceField to return weaponSize as well as name, rather than just unicode name
class WeaponChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return (obj.weaponSize, obj.weaponType, obj.weaponName)

# Over-ride ModelChoiceField to return availability as well as name, rather than just unicode name
class AvailChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return (obj.modzType, obj.modzAvailability, obj.perkName)

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

class AvailSelect(forms.Select):
    def render_option(self, selected_choices, option_value, option):
        option_value = force_unicode(option_value)
        selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
        # May not be a tuple if it's the empty value
        if isinstance(option, (list, tuple)):
            modzType = option[0]
            modzAvailability = option[1]
            option_label = option[2]
        else:
            modzType = 0
            modzAvailability = 0
            option_label = option
        return u'<option value="%s" modzType="%s" modzAvailability="%s" %s>%s%s</option>' % (
            escape(option_value), modzType, modzAvailability, selected_html,
            conditional_escape(force_unicode(option_label)),"" if not modzAvailability else " (mecha only)")

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
    owner = models.ForeignKey(User, null=True)
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
    owner = models.ForeignKey(User,null=True)
    image = models.CharField(max_length=200)
    perks = models.ManyToManyField('Perks', related_name='Perk Table', default=None, blank=True)
    desc = models.TextField(max_length=300, blank=True)
    manu = models.ManyToManyField('Manufacturer', related_name='Manu Table', default=None)
    mobility = models.SmallIntegerField(choices=ALL_MOBILITY_CHOICES, default=1, blank=False)
    size = models.SmallIntegerField(choices=SIZE_CHOICES, default=1, blank=False)
    cost = models.PositiveIntegerField(default=0, blank=True)
    creationTime = models.DateTimeField(auto_now_add=True, null=True)
    rating = models.DecimalField(blank=True, decimal_places=2, max_digits=4, default=0)

    unitType = models.SmallIntegerField(choices=GRUNTZ_TYPE_CHOICES, default=1, blank=False)
    squadSize = models.SmallIntegerField(choices=SQUAD_SIZE_CHOICES, default=6, blank=False)

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
    def test(self):
        mainCount = UnitWeapon.objects.filter(unit=self, mountType=0).count()
        if mainCount > 6:
            print 'Too many main weapons on unit %d', self.id
        if UnitWeapon.objects.filter(unit=self, mountType=1).count() >2:
            print 'Too many main weapons on unit %d' % self.id
        if self.unitType in (13,14) and mainCount > 0:
            print 'Main weapons on an invalid unit type. Unit id %d' % self.id

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
        f.write('g = gom.models.Unit(name="%s", shoot=%d, assault=%d, guard=%d, soak=%d, mental=%d, skill=%d, desc=%s, mobility=%d, size=%d, unitType=%d, image=%s, cmdTek=%s)\n' % (self.name, self.shoot, self.assault, self.guard, self.soak, self.mental, self.skill, repr(self.desc), self.mobility, self.size, self.unitType, repr(self.image), self.cmdTek))
        f.write('g.save()\n') # Needed so that we can do below M2M relations
        try:
            f.write('m = gom.models.Manufacturer.objects.get(manuName="%s")\n' % self.manu.get().manuName)
            f.write('g.manu.add(m)\n')
        except:
            pass
        try:
            f.write('import django.contrib.auth.models\n')
            f.write('u = django.contrib.auth.models.User.objects.get(username="%s")\n' % self.owner.username)
            f.write('g.owner=u\n')
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
    def isGrunt(self):
        return self.unitType == GRUNT
    def nonVSpecVehicle(self):
        if self.isVehicle() and self.unitType != VSPEC:
            return True
        return False
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
        return total
    def inlineSACost(self): # Calculate cost of inline squad attachments if any
        total = 0
        if self.unitType == GRUNT:
            unitInlineList = UnitWeapon.objects.filter(unit=self,mountType=2)
            for weaponEntry in unitInlineList:
                total = total + weaponEntry.weapon.weaponPoints
        return total
    def getBaseCost(self):
        if self.unitType == 1:
            return 1
        elif self.unitType== 2:
            return 0
        elif self.unitType== 3:
            t = (5,6,7,8,9) # includes specialist base cost of 1
        elif self.unitType == 4:
            t = (13,15,17,19,21) # includes commander base cost of 1
        elif self.unitType == TANK:
            t = (14, 19, 24, 29, 34) # Includes base tank cost of 1
        elif self.unitType == MECHA:
            t = (11, 14, 17, 22, 27) # Includes base mecha cost of 1
        elif self.unitType == GSV:
            t = (9, 13, 20, 27, 32) # Includes base GSV cost of 1
        elif self.unitType == ASV:
            t = (7, 11, 15, 20, 25) # Includes base ASV cost of 1
        elif self.unitType == ARTI:
            t = (12, 15, 20, 25, 28) # Includes base artillery cost of 1
        elif self.unitType == VSPEC:
            t = (2, 4, 6, 8, 10)
        elif self.unitType == SHT:
            t = (39, 44, 49, 54, 59)
        elif self.unitType == SHAS:
            t = (47, 54, 61, 68, 75)
        elif self.unitType == MONSTER:
            t = (16, 23, 28, 33, 38)
        elif self.unitType == AAV:
            t = (7, 10, 13, 16, 19)
        elif self.unitType == FIGHTER:
            t = (10, 13, 16, 19, 22)
        elif self.unitType == FIELD_ARTI:
            t = (3, 6, 9, 13, 16)
        else:
            raise Exception('getBaseCost, unsupported unit type')
        return t[self.size-1]
    def getDam(self):
        if self.unitType == 1:
            # Now that SAs replace gruntz rather than add to them
            # no longer add the inline SA count.
            return self.squadSize
        elif self.unitType == 2:
            return 1
        elif self.unitType == 3 or self.unitType == VSPEC:
            t=(4,5,6,7,8)
        elif self.unitType in (COMMANDER,FIGHTER):
            t=(12,14,16,18,20)
        elif self.unitType == TANK:
            t = (14,18,22,26,30)
        elif self.unitType == MECHA:
            t = (12,14,16,20,24)
        elif self.unitType == GSV:
            t = (10,12,16,17,18)
        elif self.unitType == ASV:
            t = (10,12,14,16,18)
        elif self.unitType == ARTI:
            t = (12,14,18,22,24)
        elif self.unitType == FIELD_ARTI:
            t = (9,11,13,15,17)
        elif self.unitType in (SHT, SHAS):
            t = (34,38,42,46,50)
        elif self.unitType == MONSTER:
            t = (15,20,25,30,35)
        elif self.unitType == AAV:
            t = (8,10,12,14,16)
        return t[self.size-1]
    def getSoak(self):
        if self.unitType in (1,2,3,4):
            return self.soak
        elif self.unitType in (FIGHTER,VSPEC):
            return 11+self.size
        elif self.unitType == TANK:
            return 14+self.size
        elif self.unitType == MECHA or self.unitType == ARTI:
            return 13+self.size
        elif self.unitType in (ASV, FIELD_ARTI):
            return 12+self.size
        elif self.unitType == GSV:
            t = (15,15,16,17,18)
        elif self.unitType == AAV:
            return 12+self.size
        elif self.unitType == SHAS:
            return 17+self.size
        elif self.unitType == SHT:
            return 19+self.size
        elif self.unitType == MONSTER:
            t = (14,15,18,19,20)
        return t[self.size-1]
    def getGuard(self):
        if self.unitType in (1,2,3,4):
            return self.guard
        elif self.unitType in (TANK, GSV, ARTI, FIELD_ARTI):
            return 14-self.size
        elif self.unitType in (MECHA, VSPEC):
            return 15-self.size
        elif self.unitType in (ASV,AAV):
            t = (14,13,13,12,11)
        elif self.unitType == SHT:
            return 9-self.size
        elif self.unitType == SHAS:
            return 11-self.size
        elif self.unitType in (MONSTER, FIGHTER):
            return 16-self.size
        return t[self.size-1]
    def mobilityCost(self):
        if self.unitType == 1 or self.unitType == 2 or self.unitType == 3:
            return 0
        elif self.unitType == 4:
            t = { MOBILITY_WALK:0, MOBILITY_WALK_MECHA:1, MOBILITY_TRACK:3, MOBILITY_WHEEL:5, MOBILITY_HOVER:7, MOBILITY_GRAV:9 }
            return t[self.mobility]
        elif self.isVehicle():
            if self.unitType == 12: # MECHA
                return 0
            elif self.unitType in (TANK,GSV,ARTI,SHT):
                t = { MOBILITY_WALK:0, MOBILITY_TRACK:1, MOBILITY_WHEEL:1, MOBILITY_HOVER:2, MOBILITY_GRAV:4 }
            elif self.unitType in (ASV,AAV,SHAS):
                t = { MOBILITY_HELI:0, MOBILITY_PROP_VTOL:2, MOBILITY_JET_VTOL:3, MOBILITY_GRAV:4 };
            elif self.unitType == VSPEC:
                t = { MOBILITY_FIXED:0, MOBILITY_WALK_MECHA:1, MOBILITY_TRACK:2, MOBILITY_WHEEL:2, MOBILITY_HOVER:3, MOBILITY_BIKE:4, MOBILITY_GRAV:6 }
            elif self.unitType == MONSTER:
                t = {MOBILITY_WALK:0, MOBILITY_WALK_QUAD:0, MOBILITY_JUMP:2, MOBILITY_FLIGHT:5, MOBILITY_HYPER:8}
            elif self.unitType == FIGHTER:
                t = {MOBILITY_PROP_VTOL:1, MOBILITY_JET_VTOL:2, MOBILITY_PROP:5, MOBILITY_JET:8, MOBILITY_AEROSPACE:12}
            elif self.unitType == FIELD_ARTI:
                t = {MOBILITY_FIXED:0, MOBILITY_TOWED:1, MOBILITY_WALK:3, MOBILITY_HOVER:3, MOBILITY_GRAV:3}
            else:
                raise Exception('Unsupported unit type (%d) for mobilityCost' % self.unitType)
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
            t = {2:0, 3:1, 4:3, 5:5, 6:8, 7:12}
            return t[self.skill]
        elif self.unitType != 2:
            t = {2:0, 3:1, 4:3, 5:5, 6:7, 7:9}
            return t[self.skill]
        else:
            return 0
    def mountCost(self):
        try:
            # 0 mount cost for infantry and vehicle specialists
            if self.isInfantry() or self.unitType == 16 :
                return 0
            if self.unitType == 13 or self.unitType == 14:
                # Ensure an exception is thrown if we somehow end up with main weapons
                # on a GSV or ASV
                mainCosts = (0,)
            elif self.unitType in (SHT,SHAS):
                mainCosts = (0,1,4,8,12,14,16)
            else:
                mainCosts = (0, 1, 4, 8, 13)
            AICosts = (0, 2, 4)
            # Don't include CCW weapons when calculating mount cost - for example on Mechas
            mainWeapons = UnitWeapon.objects.filter(unit=self, mountType=0).exclude(weapon__weaponType=0).count()
            AIWeapons = UnitWeapon.objects.filter(unit=self, mountType=1).count()
            print 'mainWeapons:%d, AIWeapons:%d' % (mainWeapons, AIWeapons)
            mountCosts = mainCosts[mainWeapons] + AICosts[AIWeapons]
            return mountCosts
        except Exception as e:
            print 'MountCost exception %s on unit %d' % (e, self.id)
            return 999
    def perkCost(self):
        perkCount = 0 # only track positive cost perks
        cost=0
        if self.isVehicle():
            for item in self.modz.all():
                if item.perkCost > 0:
                    perkCount = perkCount + 1
                cost = cost + item.perkCost
            if self.unitType in (ASV,GSV,TANK,MECHA,SHT,SHAS,AAV,ARTI) and self.cmdTek:
                cost=cost+6
        # Infantry
        if (self.isInfantry() and self.unitType != SA) or self.unitType==VSPEC:
            for item in self.perks.all():
                if item.perkCost > 0:
                    perkCount = perkCount + 1
                cost = cost + item.perkCost
                
        if perkCount > 1:
            cost = cost + ((perkCount-1)*5)
        print 'perkCost returning %d' % cost
        return cost
    def soakMods(self):
        soakMod = 0
        soakOverride = 0
        if self.isInfantry() or self.unitType==VSPEC:
            for item in self.perks.all():
                soakMod = soakMod + item.soakMod
                if item.soakAlternative != 0:
                    soakOverride = item.soakAlternative
        if self.isVehicle():
            for item in self.modz.all():
                soakMod = soakMod + item.soakMod
                if item.soakAlternative != 0:
                    soakOverride = item.soakAlternative
        return (soakMod,soakOverride)
    def getSoakStr(self):
        soak = self.getSoak()
        soakMod, soakOverride = self.soakMods()
        if soakMod != 0:
            soakStr = "%s*" % (soak+soakMod)
        else:
            soakStr = "%s" % soak

        if soakOverride != 0:
            soakStr = ("%s/" % soakOverride) + soakStr
        return soakStr
    def speedMods(self):
        speedMod = 0
        if self.isInfantry() or self.unitType==VSPEC:
            for item in self.perks.all():
                speedMod = speedMod + item.moveMod
        if self.isVehicle():
            for item in self.modz.all():
                speedMod = speedMod + item.moveMod
        return speedMod
    def getSpeedStr(self):
        speed = self.getSpeed()
        if speed == -1:
            return '*'
        speedMod = self.speedMods()
        if speedMod != 0:
            return "%s*" % (speed+speedMod)
        else:
            return str(speed)
    def getSpeed(self):
        if self.unitType in (1,2,3):
            return 4 # any modifiers?
        elif self.unitType == 3:
            t={1:4,2:6,3:7,4:8,5:10}
            return t[self.mobility]
        elif self.unitType == 4:
             t = { MOBILITY_WALK:4, MOBILITY_WALK_MECHA:5, MOBILITY_TRACK:6, MOBILITY_WHEEL:7, MOBILITY_HOVER:8, MOBILITY_GRAV:10 }
             return t[self.mobility]
        elif self.unitType in (TANK,GSV,ARTI):
            t = {
                MOBILITY_WALK:(7,6,6,5,4),
                MOBILITY_TRACK:(8,7,7,6,6),
                MOBILITY_WHEEL:(9,8,8,7,7),
                MOBILITY_HOVER:(8,8,7,6,5),
                MOBILITY_GRAV:(10,9,8,8,7) }
            return t[self.mobility][self.size-1]
        elif self.unitType == 12:
            t = (0, 7, 6, 6, 5, 4)
        elif self.unitType in (ASV, AAV):
            t = {
                MOBILITY_HELI:(10,10,9,8,8),
                MOBILITY_PROP_VTOL:(13,13,12,11,10),
                MOBILITY_JET_VTOL:(14,14,13,12,11),
                MOBILITY_GRAV:(15,15,14,13,12) }
            return t[self.mobility][self.size-1]
        elif self.unitType == VSPEC: 
            t = {
                MOBILITY_FIXED:(0,0,0,0,0),
                MOBILITY_WALK_MECHA:(7,6,6,5,4),
                MOBILITY_TRACK:(8,7,7,6,6),
                MOBILITY_WHEEL:(9,8,8,7,7),
                MOBILITY_HOVER:(9,8,8,7,6),
                MOBILITY_BIKE:(11,10,9,8,7),
                MOBILITY_GRAV:(16,15,14,13,12) }
            return t[self.mobility][self.size-1]
        elif self.unitType == SHT:
            t = {
                MOBILITY_WALK:(5,4,3,3,2),
                MOBILITY_TRACK:(6,5,5,4,4),
                MOBILITY_WHEEL:(7,6,5,5,5),
                MOBILITY_HOVER:(6,6,5,4,3),
                MOBILITY_GRAV:(8,7,6,6,5) }
            return t[self.mobility][self.size-1]
        elif self.unitType == SHAS:
            t = {
                MOBILITY_HELI:(9,9,8,7,7),
                MOBILITY_PROP_VTOL:(12,12,11,10,9),
                MOBILITY_JET_VTOL:(13,13,12,11,10),
                MOBILITY_GRAV:(14,14,13,12,11) }
            return t[self.mobility][self.size-1]
        elif self.unitType == FIGHTER:
            t = {
                MOBILITY_PROP_VTOL:(12,12,10,10,9),
                MOBILITY_JET_VTOL:(14,14,13,12,11),
                MOBILITY_PROP:(16,16,15,14,13),
                MOBILITY_JET:(18,18,17,16,15),
                MOBILITY_AEROSPACE:(20,20,19,18,17) }
            return t[self.mobility][self.size-1]
        elif self.unitType == MONSTER:
            t = {
                MOBILITY_WALK:(7,6,5,5,4),
                MOBILITY_WALK_QUAD:(8,7,6,5,5),
                MOBILITY_JUMP:(9,8,7,6,6),
                MOBILITY_FLIGHT:(11,10,9,8,7),
                MOBILITY_HYPER:(12,11,10,9,8) }
            return t[self.mobility][self.size-1]
        elif self.unitType == FIELD_ARTI:
            t = {
                MOBILITY_WALK:(4,4,4,4,4),
                MOBILITY_FIXED:(0,0,0,0,0),
                MOBILITY_TOWED:(-1,-1,-1,-1,-1) }
            return t[self.mobility][self.size-1]
        return t[self.size]
    def getSlots(self):
        if self.unitType == GSV:
            t=[None,"1/2",1,2,2,4]
            return t[self.size]
        elif self.unitType == ASV:
            t=[None,None,"1/2",1,2,3]
            return t[self.size]
        elif self.unitType == SHAS:
            t=[None,4,5,6,7,8]
            return t[self.size]
        else:
            return 0
    def getRam(self):
        if self.unitType == MECHA:
            return 6+self.size
        elif self.unitType in (TANK,GSV,ASV,ARTI,AAV,FIGHTER,MONSTER):
            return 8+self.size
        elif self.unitType in (SHT,SHAS):
            return 13+self.size
        return 0
    def getCost(self):
        if self.cost == 0:
            self.updateCost()
        return self.cost
    def updateCost(self):
        self.oldCost = self.cost
        print 'base:%d, shoot:%d, assault:%d, guard:%d, soak:%d, mental:%d, skill:%d, weapons:%d, SA:%d, perks:%d, mob:%d, mount:%d' % ( self.getBaseCost(), self.shootCost(), self.assaultCost(), self.guardCost(), self.soakCost(), self.mentalCost(), self.skillCost(), self.weaponCost(), self.inlineSACost(), self.perkCost(), self.mobilityCost(), self.mountCost() )
        subTotal = self.getBaseCost() + self.shootCost() + self.assaultCost() + self.guardCost() + self.soakCost() + self.mentalCost() + self.skillCost() + self.mobilityCost()
        debugTotal1 = subTotal
        if self.isInfantry():
            halved = int(ceil(subTotal /float(2)))
            print 'subTotal %d, halved %d' % (subTotal, halved)
            subTotal = halved
        subTotal = subTotal + self.weaponCost() + self.perkCost() + self.mountCost()
        debugTotal2 = subTotal
        # See if it's a non-standard grunt unit size
        # greg this should not be applied to SA inclusive total
        if self.unitType == GRUNT and self.squadSize != 6:
            subTotal = int(round((subTotal * self.squadSize)/6.0))
        debugTotal3 = subTotal
        self.cost = subTotal + self.inlineSACost()
        print 'Debug totals: %d, %d, %d, %d' % (debugTotal1, debugTotal2, debugTotal3, self.cost)
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
    class Meta:
        ordering = ['weaponSize', 'weaponName']
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
    weaponFA = models.BooleanField(default=False)

class PerksBase(models.Model):
    class Meta:
        abstract = True
    def __unicode__(self):
        return self.perkName
    perkName = models.CharField(max_length=100)
    perkDescription = models.CharField(max_length=300, default='Empty Perk Description')
    perkEffect = models.CharField(max_length=200, default='Empty Perk Effect')
    perkCost = models.SmallIntegerField(default=999)
    moveMod = models.SmallIntegerField(default=0)
    soakMod = models.SmallIntegerField(default=0)
    # Used for perks that give an alternative soak until a condition occurs
    soakAlternative = models.SmallIntegerField(default=0)

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
    mainWeapons1 = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=12), required=False, label=_('Main Weapons'), widget=WeaponSelect)
    mainWeapons2 = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=12), required=False, widget=WeaponSelect)
    mainWeapons3 = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=12), required=False, widget=WeaponSelect)
    mainWeapons4 = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=12), required=False, widget=WeaponSelect)
    mainWeapons5 = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=12), required=False, widget=WeaponSelect)
    mainWeapons6 = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=12), required=False, widget=WeaponSelect)
    AIWeapons = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=6), required=False, label=_("Anti Infantry"), widget=WeaponSelect)
    AIWeapons2 = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType__gte=4, weaponType__lte=6), required=False, widget=WeaponSelect)
    inlineWeapons = forms.ModelChoiceField(queryset=Weapons.objects.filter(weaponType__in=[1,2,4]), required=False)
    inlineWeapons2 = forms.ModelChoiceField(queryset=Weapons.objects.filter(weaponType__in=[1,2,4]), required=False)
    # Grunt CCWs only
    CCW = WeaponChoiceField(queryset=Weapons.objects.filter(weaponType=0), required=False, empty_label=None, label=_('CCW'), widget=WeaponSelect)
    MECHA_CCW = forms.ModelChoiceField(queryset=Weapons.objects.filter(weaponType=0, weaponName__in=['Basic','Small']), required=False, label=_('Mecha CCW'))
    # Grunt grenades only
    grenades = forms.ModelChoiceField(queryset=Weapons.objects.filter(weaponType=3), required=False, label=_('Grenade'))
    # Translators: Label for User customisable weapon name box.
    MW1_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    MW2_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    MW3_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    MW4_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    MW5_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    MW6_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    AI_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    AI2_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    basic_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    SA_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    Spec_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    inline_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    inline2_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    CCW_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    MECHA_CCW_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    grenades_Custom = forms.CharField(max_length=100, required=False, label=_('Custom Name'))
    OR_MW1 = forms.BooleanField(required=False)
    OR_MW2 = forms.BooleanField(required=False)
    OR_MW3 = forms.BooleanField(required=False)
    OR_MW4 = forms.BooleanField(required=False)
    OR_MW5 = forms.BooleanField(required=False)
    OR_MW6 = forms.BooleanField(required=False)
    OR_AI = forms.BooleanField(required=False)
    OR_AI2 = forms.BooleanField(required=False)
    OR_basic = forms.BooleanField(required=False)
    OR_SA = forms.BooleanField(required=False)
    OR_Spec = forms.BooleanField(required=False)
    OR_CCW = forms.BooleanField(required=False)
    OR_MECHA_CCW = forms.BooleanField(required=False)
    OR_grenades = forms.BooleanField(required=False)
    OR_inline = forms.BooleanField(required=False)
    OR_inline2 = forms.BooleanField(required=False)
    perks = forms.ModelChoiceField(queryset=Perks.objects.all().order_by('perkName'), required=False, label=_("Perk"))
    perks2 = forms.ModelChoiceField(queryset=Perks.objects.all().order_by('perkName'), required=False, label=_("Perk 2"))
    modz = AvailChoiceField(queryset=Modz.objects.all(), required=False, widget=AvailSelect) # html responsible for mecha mod filtering
    modz2 = AvailChoiceField(queryset=Modz.objects.all(), required=False, widget=AvailSelect)
    manu = forms.ModelChoiceField(queryset=Manufacturer.objects.all().order_by('manuName'), required=False)
    mobility = forms.ChoiceField(choices=BASIC_MOBILITY_CHOICES, required=False, label=_("Mobility"), initial=MOBILITY_WALK)
    # Use a DynamicChoiceField so that we will accept values outside of GUARD_CHOICES. Needed for assault class tanks.
    guard = DynamicChoiceField(required=True, choices=GUARD_CHOICES)
    soak = DynamicChoiceField(required=True, choices=SOAK_CHOICES)
    air_mobility = forms.ChoiceField(choices=AIR_MOBILITY_CHOICES, required=False, label=_("Air Mobility"), initial=MOBILITY_HELI)
    fighter_mobility = forms.ChoiceField(choices=FIGHTER_MOBILITY_CHOICES, required=False, label=_("Fighter Mobility"), initial=MOBILITY_PROP_VTOL)
    field_artillery_mobility = forms.ChoiceField(choices=FIELD_ARTI_MOBILITY_CHOICES, required=False, label=_("Mobility"), initial=MOBILITY_FIXED)
    monster_mobility = forms.ChoiceField(choices=MONSTER_MOBILITY_CHOICES, required=False, label=_("Mobility"), initial=MOBILITY_WALK)
    commander_mobility = forms.ChoiceField(choices=COMMANDER_MOBILITY_CHOICES, required=False, label=_("Mobility"))
    vspec_mobility = forms.ChoiceField(choices=VEHICLE_SPEC_MOBILITY_CHOICES, required=False, label=_("Mobility"))

    class Meta:
        model = Unit
        fields = ['id', 'name', 'unitType', 'size', 'shoot', 'assault', 'mental', 'skill', 'mobility', 'desc', 'cmdTek', 'publish', 'squadSize' ]
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
                if kwargs['instance'].unitType == MECHA:
                    MECHA_CCW_instance = UnitWeapon.objects.filter(unit=kwargs['instance'], weapon__weaponType=0, mountType=0).get()
                    self.fields['MECHA_CCW'].initial=MECHA_CCW_instance.weapon
                    if MECHA_CCW_instance.nameOverride:
                        self.fields['MECHA_CCW_Custom'].initial=MECHA_CCW_instance.nameOverride
                        self.fields['OR_MECHA_CCW'].initial=True
            except ObjectDoesNotExist:
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
                mainWeapons = UnitWeapon.objects.filter(unit=kwargs['instance'], mountType=0, weapon__weaponType__gte=1) # Avoid CCW weapons, which a Mecha could be carrying
                count = 1
                for item in mainWeapons.all():
                    self.fields['mainWeapons%d' % count].initial=item.weapon
                    if item.nameOverride:
                        self.fields['MW%d_Custom' % count].initial=item.nameOverride
                        self.fields['OR_MW%d' % count].initial = True
                    count=count+1
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
            try: # Use this approach rather than all()[0] & all()[1] as on some querysets
                # but not others, those would return the same result even if iterating through
                # the queryset showed that the components differed. Dunno what caused it, I
                # guess that it's a django bug - I know that querysets are lazy but don't think
                # that's the cause.
                perk1, perk2 = kwargs['instance'].perks.all()
                self.fields['perks'].initial=perk1
                self.fields['perks2'].initial=perk2
            except ValueError:
                try:
                    self.fields['perks'].initial=kwargs['instance'].perks.all()[0]
                except IndexError:
                    pass
            try: # if you have issues with modz being erroneously returned here, read the above perks comment
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
                self.fields['soak'].initial=kwargs['instance'].getSoak()
            except Exception, e:
                pass
            try:
                self.fields['guard'].initial=kwargs['instance'].getGuard()
            except Exception, e:
                pass
            try:
                if kwargs['instance'].unitType == COMMANDER:
                    self.fields['commander_mobility'].initial = kwargs['instance'].mobility
            except Exception, e:
                print "commander mobility exception", e
                pass
            try:
                if kwargs['instance'].unitType == FIGHTER:
                    self.fields['fighter_mobility'].initial = kwargs['instance'].mobility
            except Exception, e:
                print "fighter mobility exception", e
                pass
            try:
                if kwargs['instance'].unitType in [ASV,AAV,SHAS]:
                    self.fields['air_mobility'].initial = kwargs['instance'].mobility
            except Exception, e:
                print "air mobility exception", e
                pass
            try:
                if kwargs['instance'].unitType == MONSTER:
                    self.fields['monster_mobility'].initial = kwargs['instance'].mobility
            except Exception, e:
                print "monster mobility exception", e
                pass
            try:
                if kwargs['instance'].unitType == FIELD_ARTI:
                    self.fields['field_artillery_mobility'].initial = kwargs['instance'].mobility
            except Exception, e:
                print "field artillery mobility exception", e
                pass
            try:
                if kwargs['instance'].unitType == VSPEC:
                    self.fields['vspec_mobility'].initial = kwargs['instance'].mobility
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
            sameImageCount = Unit.objects.filter(image=obj.image, owner=obj.owner).count()
            print 'sameImage count is %d' % sameImageCount
            if sameImageCount < 2: # No other objects have this image
                os.remove('user_media/%d/%s' % (obj.owner.id, obj.image))
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
