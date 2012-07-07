from django.utils.translation import ugettext as _
from django.db.models import Q
from reportlab.pdfgen import canvas
from django.contrib.auth.models import User
from decimal import *
from PIL import Image
import os
import pdf
import json
# Fall back to StringIO in environments where cStringIO is not available
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import hashlib
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from django.core.files import File
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
import gom.models

def setFilters(request):
    try:
        if request.is_ajax() and request.user.is_authenticated():
            try:
                user_profile = request.user.profile
            except Exception ,e:
                print 'user_profile access exception:', e

            filters = {}
            try:
                if request.POST['owner']:
                    filters['owner']=int(request.POST['owner'])
                if request.POST['unit_type']:
                    filters['unit_type'] = int(request.POST['unit_type'])
                if request.POST['manu']:
                    filters['manu'] = int(request.POST['manu'])
                if request.POST['cost_max']:
                    filters['cost_max'] = int(request.POST['cost_max'])
                if request.POST['cost_min']:
                    filters['cost_min'] = int(request.POST['cost_min'])
                if request.POST['rating_min']:
                    filters['rating_min']=Decimal(request.POST['rating_min'])
                if request.POST['image']:
                    filters['image']=int(request.POST['image'])
            except KeyError: # Should be a reset call
                pass
            user_profile.filterSettings=filters
            user_profile.save()
            return HttpResponse()
        else:
            return HttpResponseBadRequest(_('User unauthorised.'))
    except Exception, e:
        return HttpResponseBadRequest(_('Failed to update user filters.'))

def unitRate(request, uid):
    try:
        if request.is_ajax() and request.user.is_authenticated():
            unit = gom.models.Unit.objects.get(id=uid)
            unit.addRating(request.POST['score'], request.user)
            return HttpResponse()
        else:
            return HttpResponseBadRequest(_('User unauthorised.'))
    except Exception, e:
        return HttpResponseBadRequest(_('Failed to rate unit.'))

def updateEntryCount(request):
    try:
        if request.is_ajax() and request.user.is_authenticated():
            entry_id = request.POST['entry'][6:]
            count = int(request.POST['count'])
            entry = gom.models.ForceEntry.objects.get(id=entry_id)
            force = entry.force
            if force.owner.get() == request.user:
                print 'owner match'
            else:
                print "trying to adjust force entry in someone else's force"
                return HttpResponseBadRequest(_('Attempt to modify force not owned by this user'))
            rDict = {}
            if count > 0:
                entry.count = count
                entry.save()
                rDict['forceUpdate'] = 1
            else:
                print 'trying to delete entry %s' % entry.id
                entry.delete()
                rDict['forceUpdate'] = 2
                rDict['delete']=entry_id
            cost = force.getCost(True)
            rDict.update({'cost':cost})
            json_data = json.dumps(rDict)
            # json data is just a JSON string now. 
            return HttpResponse(json_data, mimetype="application/json")
        else:
            return HttpResponseBadRequest(_('Only Ajax queries may use this interface'))
    except Exception, e:
        print e
        return HttpResponseBadRequest(_('Failed to update force entry. Please try again.'))

def forceForm(request, force_id):
    force_owner = None
    force = None
    if ( force_id != "0" ):
        try:
            force = gom.models.Force.objects.get(id=force_id)
            form = gom.models.ForceForm(instance=force)
        except:
            return HttpResponseBadRequest(_('No such force id. It may have been deleted.'))
        force_owner = force.owner.get()
    else:
        form = gom.models.ForceForm()
    #import pdb; pdb.set_trace()
    return render_to_response('gom/force.html', \
        {
            'force':force,
            'force_id':force_id,
            'force_owner':force_owner,
            'formObject':form,
            'saved':0

        }, \
        RequestContext(request))

def unitForm(request, unit_id):
    image = None
    unit_owner = 0
    if ( unit_id != "0" ):
        unit = gom.models.Unit.objects.get(id=unit_id);
        unit_owner = unit.owner.get()
        image = '%d/%s' % (unit_owner.id, unit.image)
        form = gom.models.UnitForm(instance=unit)
        return render_to_response('gom/unit.html', \
            {
                'unit_owner':unit_owner,
                'formObject':form,
                'filename':image,
                'saved':0,
                'unit':unit,
                'weapons':weaponCosts(),
                'perkz':perkCosts(),
                'modz':modCosts(),
            }, \
            RequestContext(request))
    else: # Make a new temporary unit
        if (request.user.is_authenticated()):
            unit = gom.models.Unit(tempInstance=True)
            unit.save() # Need to be able to do owner M2M below
            unit.owner=request.user,
            unit.save()
            return redirect('/gom/unit/%d/' % unit.id)
        else:
            return HttpResponseForbidden(_('You must be logged in to create a new unit.'))

def scale_dimensions(width, height, longest_side):
    if width > height:
        if width > longest_side:
            ratio = longest_side*1./width
            return (int(width*ratio), int(height*ratio))
    elif height > longest_side:
        ratio = longest_side*1./height
        return (int(width*ratio), int(height*ratio))
    return (width, height)

def handle_uploaded_image(unit, i):
    # resize image
    imagefile  = StringIO(i.read())
    imageImage = Image.open(imagefile)

    (original_width, original_height) = imageImage.size
    (width, height) = scale_dimensions(original_width, original_height, longest_side=512)

    if width != original_width or height != original_height:
        print 'pre-scale w:%d, h:%d' % (original_width, original_height)
        print 'post-scale w:%d, h:%d' % (width, height)
        resizedImage = imageImage.resize((width, height), Image.ANTIALIAS)
    else:
        resizedImage = imageImage

    imagefile = StringIO()
    resizedImage.save(imagefile,'JPEG', quality=90 )

    # Make the user's image directory if not already present
    user_dir = 'user_media/%d/' % unit.owner.get().id
    if not os.path.isdir(user_dir):
        print 'trying to make user media directory %s' % user_dir
        os.mkdir(user_dir)
    else:
        print 'user media directory %s exists.' % user_dir

    # delete the old image
    try:
        if unit.image:
            # Only delete old image if not used by another unit of this user's
            sameImageCount = gom.models.Unit.objects.filter(image=unit.image, owner=unit.owner.get()).count()
            if sameImageCount < 2: # No other objects have this image
                os.remove('user_media/%d/%s' % (unit.owner.get().id, unit.image))
    except OSError:
        pass

    filename = hashlib.md5(imagefile.getvalue()).hexdigest()+'.jpg'

    # save to disk
    fullpath = os.path.join(user_dir, filename)
    imagefile = open(fullpath, 'w')
    resizedImage.save(imagefile,'JPEG', quality=90)
    os.chmod(fullpath, 0660)
    unit.image = filename
    unit.save()

# not complete, barely started
def vehicleSaveAjax(request, unit_id=0):
    print 'vehicle save'
    if request.user.is_authenticated() and request.method == 'POST': # If the form has been submitted...
        if request.is_ajax():
            print 'Ajax request'
            return render(request, 'gom/vehicle.html')
        else:
            print 'Non Ajax request'
        pass
    return tankForm(request, unit_id)

def saveVehicleWeapons(unit, form):
    unit.weapons.clear()
    if form.cleaned_data['AIWeapons']:
        addUnitWeapon(unit, form.cleaned_data['AIWeapons'], 1, custom=form.cleaned_data['AI_Custom'] if form.cleaned_data['OR_AI'] else None)
    if unit.unitType == 11 or unit.unitType == 12: # Tank or Mecha
        if form.cleaned_data['mainWeapons']:
            try:
                addUnitWeapon(unit, form.cleaned_data['mainWeapons'], custom=form.cleaned_data['MW_Custom'] if form.cleaned_data['OR_MW'] else None)
            except:
                addUnitWeapon(unit, form.cleaned_data['mainWeapons'])
        if unit.size > 1:
            if form.cleaned_data['mainWeapons2']:
                addUnitWeapon(unit, form.cleaned_data['mainWeapons2'], custom=form.cleaned_data['MW2_Custom'] if form.cleaned_data['OR_MW2'] else None)
            if unit.size > 2:
                if form.cleaned_data['mainWeapons3']:
                    addUnitWeapon(unit, form.cleaned_data['mainWeapons3'], custom=form.cleaned_data['MW3_Custom'] if form.cleaned_data['OR_MW3'] else None)
                if unit.size > 4 and form.cleaned_data['mainWeapons4']:
                    addUnitWeapon(unit, form.cleaned_data['mainWeapons4'], custom=form.cleaned_data['MW4_Custom'] if form.cleaned_data['OR_MW4'] else None)
        if unit.size > 2 and form.cleaned_data['AIWeapons2']:
            addUnitWeapon(unit, form.cleaned_data['AIWeapons2'], 1, custom=form.cleaned_data['AI2_Custom'] if form.cleaned_data['OR_AI2'] else None)
    elif unit.unitType == 13 or unit.unitType == 14:
        # Don't save main weapons for GSV or ASV
        if unit.size >= 3 and form.cleaned_data['AIWeapons2']:
            addUnitWeapon(unit, form.cleaned_data['AIWeapons2'], 1, custom=form.cleaned_data['AI2_Custom'] if form.cleaned_data['OR_AI2'] else None)
    elif unit.unitType == 15: # Artillery
        if form.cleaned_data['mainWeapons']:
            addUnitWeapon(unit, form.cleaned_data['mainWeapons'], custom=form.cleaned_data['MW_Custom'] if form.cleaned_data['OR_MW'] else None)
        if unit.size >= 3:
            if form.cleaned_data['mainWeapons2']:
                addUnitWeapon(unit, form.cleaned_data['mainWeapons2'], custom=form.cleaned_data['MW2_Custom'] if form.cleaned_data['OR_MW2'] else None)
            if form.cleaned_data['AIWeapons2']:
                addUnitWeapon(unit, form.cleaned_data['AIWeapons2'], 1, custom=form.cleaned_data['AI2_Custom'] if form.cleaned_data['OR_AI2'] else None)
    else:
        print 'Unknown unit type:%d'
        raise Exception

def forceSave(request, force_id=0):
    print 'trying to save force %s' % force_id
    force_id = int(force_id)
    original_force_id = force_id # use later to determine if redirect or not
    force_owner = None
    if request.user.is_authenticated() and request.method == 'POST': # If the form has been submitted...
        form = gom.models.ForceForm(request.POST) # A form bound to the POST data
        print 'form created'
        if form.is_valid(): # All validation rules pass
            print 'force form valid'
            if (force_id == 0): # new force object
                print 'trying to make new force'
                force = gom.models.Force( name=form.cleaned_data['name'] )
                force.save() # Needed before we can access M2M fields or id
                force.owner.add(request.user)
                force.save()
                force_id = force.id
                print 'saved new force - %d' % force.id
            else:
                force = gom.models.Force.objects.get(id=force_id)
                # If the authenticated user is not the owner of this object then don't let them edit it!
                if (request.user != force.owner.get()): # If they want a PDF allow that, but nothing else
                    if 'pdf' in request.POST:
                        return forcePDF(request, force)
                    print 'Attempt by user %s to edit force owned by user %s' % (request.user, force.owner.get())
                    return HttpResponseForbidden()
                if 'delete' in request.POST:
                    force.delete()
                    return HttpResponseRedirect('/gom/list/all//')
                force.name = form.cleaned_data['name']

            # Now update any units in the force
            #saveForceUnits(force, form)
            if form.cleaned_data['description']:
                force.description=form.cleaned_data['description']
            print 'saving updated force %d' % force.id
            force.updateCost()
            force.save()
            if 'pdf' in request.POST:
                return forcePDF(request, force)
        else:
            print form._errors
            return HttpResponseBadRequest(_('Invalid Force data. Please sanity check data values'))

        force_owner = force.owner.get()
    else:
        if request.method == 'POST' and 'pdf' in request.POST:
            try:
                force = gom.models.Force.objects.get(id=force_id)
                return forcePDF(request, force)
            except Exception, e:
                print e
                return HttpResponseForbidden(_('Unable to produce PDF for this force.'))
        else:
            if user.is_authenticated():
                return HttpResponseForbidden(_('Attempt to modify force that does not belong to your account.'))
            else:
                return HttpResponseForbidden(_('You must login to modify forces.'))

    if original_force_id == 0:
        # New Force, so redirect to update the id in the user's URL bar
        return redirect('/gom/force/%d/' % force_id)
    else:
        return forceForm(request, force_id)

def addUnitWeapon(targetUnit, newWeapon, mountType=0, custom=None):
    print 'Adding weapon %s (%s) to unit %s with mount type %d' % (newWeapon, custom, targetUnit.name, mountType)
    if newWeapon:
        if custom != None:
            w = gom.models.UnitWeapon(weapon=newWeapon, unit=targetUnit, mountType=mountType, nameOverride=custom)
        else:
            w = gom.models.UnitWeapon(weapon=newWeapon, unit=targetUnit, mountType=mountType)
        w.save()

def pdfIt(request, unit_id=0):
    if request.method == 'POST' and 'pdf' in request.POST:
        try:
            unit = gom.models.Unit.objects.get(id=unit_id);
            return pdf.PDFit(request, unit)
        except Exception, e:
            print 'Failed to produce PDF:', e
            return HttpResponseForbidden(_('Unable to produce PDF for this unit.'))
    else:
        if request.user.is_authenticated():
            return HttpResponseForbidden(_('Failed to modify unit. Does your account have edit permissions for this unit?'))
        else:
            return HttpResponseForbidden(_('You must login to modify units.'))

def perkCosts():
    p = gom.models.Perks.objects.all()
    perks = ""
    for (a,b) in map (lambda x: (x.id, x.perkCost), p):
        perks = perks + "%s:%s," % (a,b)
    return perks
def modCosts():
    m = gom.models.Modz.objects.all()
    modz = ""
    for (a,b) in map (lambda x: (x.id, x.perkCost), m):
        modz = modz + "%s:%s," % (a,b)
    return modz
def weaponCosts():
    #could try to use django cache system here
    w = gom.models.Weapons.objects.all()
    weapons = ""
    for (a,b) in map (lambda x: (x.id, x.weaponPoints), w):
        weapons = weapons + "%s:%s," % (a,b)
    return weapons
def unitSave(request, unit_id=0):
    print 'trying to save unit %s' % unit_id
    unit_id = int(unit_id)
    original_unit_id = unit_id
    unit_owner = 0

    if request.user.is_authenticated() and request.method == 'POST': # If the form has been submitted...
        form = gom.models.UnitForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            if (unit_id == 0): # new unit object - NOW DEFUNCT, delete soon
                unit = gom.models.Unit( name=form.cleaned_data['name'],
                    unitType=int(form.cleaned_data['unitType']),
                    shoot=int(form.cleaned_data['shoot']),
                    assault=int(form.cleaned_data['assault']),
                    guard=int(form.cleaned_data['guard']),
                    soak=int(form.cleaned_data['soak']),
                    mental=int(form.cleaned_data['mental']),
                    skill=int(form.cleaned_data['skill']),
                    size=int(form.cleaned_data['size']))
                unit.save()
                unit.owner.add(request.user)
                unit.save()
                unit_id = unit.id
                print 'saved new unit - %d' % unit.id
            else:

                unit = gom.models.Unit.objects.get(id=unit_id);
                # If the authenticated user is not the owner of this object then don't let them edit it!
                if (request.user != unit.owner.get()):
                    return pdfIt(request, unit_id)
                print 'Updating unit entry %d' % unit_id
                #test for delete
                if 'delete' in request.POST:
                    unit.delete()
                    return HttpResponseRedirect('/gom/list/all/')
                print form.cleaned_data
                if unit.tempInstance: # Clear the temp object flag if set
                    print 'clearing tempInstance'
                    unit.tempInstance = False
                    unit.save() # Important enough to warrant an immediate save imo
                unit.name = form.cleaned_data['name']
                unit.shoot=int(form.cleaned_data['shoot'])
                unit.assault=int(form.cleaned_data['assault'])
                unit.guard=int(form.cleaned_data['guard'])
                unit.soak=int(form.cleaned_data['soak'])
                unit.mental=int(form.cleaned_data['mental'])
                unit.skill=int(form.cleaned_data['skill'])
                unit.size=int(form.cleaned_data['size'])
                unit.unitType=int(form.cleaned_data['unitType'])

            print form.cleaned_data
            # Now add weapon groups
            unit.weapons.clear()
            if unit.isVehicle():
                saveVehicleWeapons(unit, form)
                if form.cleaned_data['modz']:
                    unit.modz=form.cleaned_data['modz'],
                else:
                    unit.modz.clear()
            else: # infantry
                if unit.unitType == 1:
                    if unit.isPowerArmour():
                        addUnitWeapon(unit, form.cleaned_data['SAWeapons'], custom=form.cleaned_data['SA_Custom'] if form.cleaned_data['OR_SA'] else None)
                    else:
                        addUnitWeapon(unit, form.cleaned_data['basicWeapons'], custom=form.cleaned_data['basic_Custom'] if form.cleaned_data['OR_basic'] else None)
                    # inline squad attachments
                    if form.cleaned_data['inlineWeapons']:
                        addUnitWeapon(unit, form.cleaned_data['inlineWeapons'], mountType=2, custom=form.cleaned_data['inline_Custom'] if form.cleaned_data['OR_inline'] else None)
                    if form.cleaned_data['inlineWeapons2']:
                        addUnitWeapon(unit, form.cleaned_data['inlineWeapons2'], mountType=2, custom=form.cleaned_data['inline2_Custom'] if form.cleaned_data['OR_inline2'] else None)
                elif unit.unitType == 2 or unit.unitType == 4: # SA or Commander
                    addUnitWeapon(unit, form.cleaned_data['SAWeapons'], custom=form.cleaned_data['SA_Custom'] if form.cleaned_data['OR_SA'] else None)
                elif unit.unitType == 3:
                    addUnitWeapon(unit, form.cleaned_data['SpecWeapons'], custom=form.cleaned_data['Spec_Custom'] if form.cleaned_data['OR_Spec'] else None)

                if form.cleaned_data['CCW']:
                    addUnitWeapon(unit, form.cleaned_data['CCW'], custom=form.cleaned_data['CCW_Custom'] if form.cleaned_data['OR_CCW'] else None)
                if form.cleaned_data['grenades']:
                    addUnitWeapon(unit, form.cleaned_data['grenades'], custom=form.cleaned_data['grenades_Custom'] if form.cleaned_data['OR_grenades'] else None)
                if form.cleaned_data['perks']:
                    if form.cleaned_data['perks2'] and unit.canHaveTwoPerks():
                        unit.perks=(form.cleaned_data['perks'], form.cleaned_data['perks2'])
                    else:
                        unit.perks=form.cleaned_data['perks'],
                elif form.cleaned_data['perks2']:
                    unit.perks=form.cleaned_data['perks2'],
                else:
                    unit.perks.clear()

                try:
                    unit.medicSpecialist=form.cleaned_data['medicSpecialist']
                except:
                    unit.medicSpecialist=0
                try:
                    unit.engineerSpecialist=form.cleaned_data['engineerSpecialist']
                except:
                    unit.engineerSpecialist=0
                try:
                    unit.mechaSpecialist=form.cleaned_data['mechaSpecialist']
                except:
                    unit.mechaSpecialist=0
            # General
            if form.cleaned_data['desc']:
                unit.desc=form.cleaned_data['desc']
            if form.cleaned_data['manu']:
                unit.manu=form.cleaned_data['manu'],
            if (unit.unitType == 13 or unit.unitType == 14) and form.cleaned_data['cmdTek']:
                unit.cmdTek=form.cleaned_data['cmdTek']
            else:
                unit.cmdTek = False
            if unit.unitType == 12:
                print 'Setting mecha mobility'
                unit.mobility = 1 # Walk - it's a mecha
            elif unit.unitType == 14:
                try:
                    unit.mobility = int(form.cleaned_data['air_mobility'])
                except:
                    unit.mobility = 1
            else:
                unit.mobility = int(form.cleaned_data['mobility'])

            unit.updateCost()
            unit.save()
            # Now try and save any associated image
            try:
                handle_uploaded_image(unit, request.FILES['image'])
            except KeyError:
                pass
            if 'pdf' in request.POST:
                return pdf.PDFit(request, unit)
        else:
            error_string=_('Invalid unit data. Unable to create PDF. Please sanity check data values')
            if form.errors:
                error_string = '%s\n%s' % (error_string, form.errors)

            print form._errors
            print form
            return HttpResponseBadRequest(error_string)
            # Failed is_valid

        unit_owner = unit.owner.get()
        image = '%d/%s' % (unit_owner.id, unit.image)
    else:
        return pdfIt(request, unit_id)

    if original_unit_id == 0:
        # New unit, so redirect to update the id in the user's URL bar
        return redirect('/gom/unit/%d/' % unit_id)
    else:
        return render_to_response('gom/unit.html', \
            {
                'unit_owner':unit_owner,
                'formObject':form,
                'filename':image,
                'saved':1,
                'unit':unit,
                'weapons':weaponCosts(),
                'perkz':perkCosts(),
                'modz':modCosts(),
            }, \
            RequestContext(request))

def updateForce(request):
    for item in request.POST:
        if request.POST[item]!= '':
            if item.startswith('force_'):
                unitCount=1
                unitID = item[6:]
                forceID = request.POST[item]
                force = gom.models.Force.objects.get(id=forceID)
                unit = gom.models.Unit.objects.get(id=unitID)
                f = gom.models.ForceEntry(unit=unit, force=force, count=unitCount)
                f.save()
                force.cost = force.cost + (unit.cost*unitCount)
                force.save()
                print 'item:%s, value:%s, unit:%s, force:%s' % (item, request.POST[item], unitID, forceID)
    if request.is_ajax():
        return HttpResponse()
    else:
        return list(request)

def forcePDF(request, force):
    units = []
    try:
        entries = gom.models.ForceEntry.objects.filter(force=force)
    except:
        return HttpResponseBadRequest(_('No units associated with this force'))
    for entry in entries:
        unit = entry.unit
        units.append(unit)
        # Design decision to only print one card per unit entry, no matter the entry's unit count
        #for i in range(entry.count):
        #    units.append(unit)

    return pdf.PDFmulti(request, units, force)

def multiPDF(request):
    if request.method == 'POST': 
        units = []
        for item in request.POST:
            if request.POST[item] != "":
                if item.startswith('pdf_V'):
                    pk = item[5:]
                    try:
                        howMany = int(request.POST[item])
                        for i in range(0, howMany):
                            units.append(gom.models.Tank.objects.get(id=pk))
                    except:
                        pass
                    print 'vehicle', item, pk
                elif item.startswith('pdf_'):
                    pk = item[4:]
                    try:
                        howMany = int(request.POST[item])
                        for i in range(0, howMany):
                            units.append(gom.models.Unit.objects.get(id=pk))
                    except:
                        pass
                    print 'unit', item, pk

        return pdf.PDFmulti(request, units)
    else:
        return HttpResponseBadRequest(_('Invalid request to multi card PDF. Please sanity check data.'))

def force_list(request):
    forces = gom.models.Force.objects.all()
    if not request.user.is_authenticated():
       forces = forces.filter(cost__gt=0)
    else:
        forces = forces.exclude(~Q(owner=request.user),cost=0)

    return render_to_response('gom/force_list.html', \
        {
            'Forces':forces
        }, \
        RequestContext(request))

def listHandler(request, what):
    if what == 'force':
        return force_list(request)
    # See if this isn't a simple list request
    if request.method == 'POST':
        if 'pdf' in request.POST:
            return multiPDF(request)
        if 'force' in request.POST or what == 'addForceEntry':
            return updateForce(request)
    return list(request)

def list(request):
    units = gom.models.Unit.objects.exclude(tempInstance=True)
    try:
        forces = gom.models.Force.objects.filter(owner=request.user)
    except:
        forces = None
    # Find any users who have units, as we may wish to filter on them
    owners=[]
    for unit in units:
        owner = unit.owner.get()
        if owner not in owners:
            owners.append(owner)
    # Put owners list in case-insensitive alphabetical order
    owners.sort(key=lambda x: str.lower(repr(x)))

    filterDict=None
    filterSet=None # use to pass defaults for html selects if this is based on user profile
    if request.is_ajax():
        filterDict = request.POST
    elif request.user.is_authenticated():
        try:
            user_profile = request.user.profile
            filterDict = user_profile.filterSettings
            filterSet=filterDict
        except Exception ,e:
            print 'user_profile access exception:', e
    if filterDict:
        try:
            if filterDict['owner']:
                units = units.filter(owner=filterDict['owner'])
        except KeyError:
            pass
        try:
            if filterDict['unit_type']:
                units = units.filter(unitType=filterDict['unit_type'])
        except KeyError:
            pass
        try:
            if filterDict['manu']:
                units = units.filter(manu=filterDict['manu'])
        except KeyError:
            pass
        try:
            if filterDict['cost_max']:
                units=units.filter(cost__lte=filterDict['cost_max'])
        except KeyError:
            pass
        try:
            if filterDict['cost_min']:
                units=units.filter(cost__gte=filterDict['cost_min'])
        except KeyError:
            pass
        try:
            if filterDict['rating_min']:
                units=units.filter(rating__gte=filterDict['rating_min'])
        except KeyError:
            pass
        #elif filterType == '5' and filterValue2:
        #    if filterValue == '1':
        #        units=units.filter(name__icontains=filterValue2)
        #    elif filterValue == '2':
        #        units=units.filter(name__istartswith=filterValue2)
        #    elif filterValue == '3':
        #        units=units.filter(name__iendswith=filterValue2)
        try:
            # int(1) if via profile, u'1' if via ajax
            if filterDict['image'] == 1 or filterDict['image'] == '1':
                units=units.exclude(image="")
            elif filterDict['image'] != "":
                units=units.filter(image="")
        except KeyError:
            pass
    return render_to_response('gom/list_table.html' if request.is_ajax() else 'gom/list.html', \
        {
            'units':units,
            'forces':forces,
            'owners':owners,
            'manufacturers':gom.models.Manufacturer.objects.all().order_by('manuName'),
            'filter_set':filterSet,
        }, \
        RequestContext(request))



def filterOwner(request, who=None):
    print 'filterOwner'
    return list(request, filter_owner=who)

def filterType(request, which=None):
    print 'filterType'
    return list(request, filter_type=which)

