from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import Image, paragraph, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, LETTER, landscape, portrait
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
# Fall back to StringIO in environments where cStringIO is not available
try:
        from cStringIO import StringIO
except ImportError:
        from StringIO import StringIO
import gom.models

def justifyStyle(fontName='Helvetica-Bold',fontSize=5):
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    styles['Justify'].fontSize=fontSize
    styles['Justify'].fontName=fontName
    styles['Justify'].leading=6
    styles['Justify'].autoLeading="min"
    return styles['Justify']

def drawStats(p, grunt, WIDTH, HEIGHT):
    locations=[]
    for i in range(0,3):
        for j in range(0,2):
            locations.append([.42*WIDTH + (i*.5*inch), .695*HEIGHT +(j*.3*inch), None, None] )
    locations[0][2] = grunt.shoot
    locations[1][2] = grunt.getGuard()
    locations[2][2] = grunt.assault
    locations[3][2] = grunt.getSoak()
    locations[4][2] = grunt.mental
    locations[5][2] = grunt.skill
    locations[0][3] = _('Shoot')
    locations[1][3] = _('Guard')
    locations[2][3] = _('Assault')
    locations[3][3] = _('Soak')
    locations[4][3] = _('Mental')
    locations[5][3] = _('Skill')

    p.setFillColor(colors.darkgrey)
    p.roundRect(.4*WIDTH, .47*HEIGHT, (.6*WIDTH)-1, .23*HEIGHT+(.6*inch), radius=4, fill=1, stroke=0)
    p.setStrokeColor(colors.white)
    # Only display guard, soak and skill for vehicles
    if grunt.isVehicle():
        locations = locations[1::2]

    for l in locations:
        p.setFillColor(colors.white)
        p.roundRect(l[0], l[1], .4*inch, .25*inch, radius=2, fill=1)
        p.setFillColor(colors.black)
        p.setFont("Helvetica", 6)
        p.drawCentredString(l[0]+.2*inch, l[1]+.15*inch, l[3])
        p.setFont("Helvetica-Bold", 8)
        p.drawCentredString(l[0]+.2*inch, l[1]+.03*inch, str(l[2]))

def getForceUnits(force):
    units = {}
    try:
        entries = gom.models.ForceEntry.objects.filter(force=force)
        for entry in entries:
            if entry.unit in units:
                units[entry.unit]=units[entry.unit]+entry.count
            else:
                units[entry.unit]=entry.count
    except Exception,e:
        print 'getForceUnits caught exception:', e
    return units

def getPerkText(grunt):
    modz = None
    perkz = None
    if grunt.isInfantry() or grunt.unitType == 16:
        if grunt.unitType == 2: # Squad attachments display no perk string
            return
        perkString = _('No Perks')
        perkz = grunt.perks.all()
    if grunt.isVehicle():
        perkString = _('No Modz')
        modz = grunt.modz.all()

    count = 0
    for list in perkz, modz:
        if list != None:
            for perk in list:
                if count > 0:
                    perkString = perkString + '<br/>%s: %s' % (perk.perkName, perk.perkEffect)
                else:
                    perkString = '%s: %s' % (perk.perkName, perk.perkEffect)
                count = count+1
    return perkString

def calcCriticalInterval(dmg):
    if dmg >= 50:
        return 15
    if dmg >= 46:
        return 14
    if dmg >= 42:
        return 12
    if dmg >= 38:
        return 11
    if dmg >= 34:
        return 10
    if dmg >= 26:
        return 7
    elif dmg >= 20:
        return 6
    elif dmg >= 16:
        return 5
    elif dmg >= 13:
        return 4
    return 3

def drawDamage(p, grunt, WIDTH, HEIGHT):
    dmg = grunt.getDam()
    interval = calcCriticalInterval(dmg)

    dmgString = str(dmg)

    p.setStrokeColor(colors.black)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 6)
    x = .07*WIDTH
   
    if grunt.getDam() > 40:
        y = .21 * HEIGHT
    else:
        y = .19*HEIGHT
    boxWidth = WIDTH/19
    boxGap = WIDTH/119
    for i in range(0, dmg):
        boxX = x+((i%10)*(boxWidth+boxGap))
        boxY = y-((i/10)*(boxWidth+boxGap))
        p.roundRect(boxX, boxY, boxWidth, boxWidth, radius=2, fill=1, stroke=1)
        if (i+1)%interval == 0 and grunt.nonVSpecVehicle():
            if (i+1)/interval <= 3:
                p.setFillColor(colors.black)
                # Translators: This is the first letter of 'Critical' and is used to flag critical boxes on vehicles cards.
                p.drawCentredString( boxX+(boxWidth/2), boxY+.01*HEIGHT , _('C'))
                p.setFillColor(colors.white)
    p.setFillColor(colors.black)
    p.drawString(.7 * WIDTH, .225*HEIGHT, _('Damage:'))
    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(.9*WIDTH, .215*HEIGHT, dmgString)
    p.setStrokeColor(colors.lightgrey)
    p.circle( .9*WIDTH, .227*HEIGHT, .035*WIDTH, fill=0, stroke=1)
    # Draw Critical boxes if this is a vehicle other than vehicle specialist
    if grunt.nonVSpecVehicle():
        strings=(_('Armour'), _('Engine'),
                # Translators: Abbreviation of CmdTek - Gruntz term for vehicle carried command and control technology.
                _('Tek'))
        for i in range(0,len(strings)):
            dy = (.16*HEIGHT)-((boxWidth+boxGap)*i)
            p.setStrokeColor(colors.black)
            p.setFillColor(colors.white)
            p.roundRect(.88*WIDTH, dy, boxWidth, boxWidth, radius=2, fill=1, stroke=1)
            p.setFillColor(colors.black)
            p.drawRightString(.87 *WIDTH, dy+(boxWidth/4), strings[i])

def drawSlots(p, grunt, WIDTH, HEIGHT):
    slots = grunt.getSlots()
    if slots:
        x = .026*WIDTH
        boxWidth = WIDTH/23
        boxGap = WIDTH/119
        y = .51*HEIGHT
        p.setStrokeColor(colors.lightgrey)
        p.setFillColor(colors.white)
        p.roundRect(x, y, 8*boxWidth, boxWidth, radius=3, fill=1, stroke=1)
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", 6)
        p.drawCentredString(x + 4*boxWidth, y+(boxWidth/4), "%s %s" % (_('Transport Slots:'), slots) )

def drawMedicEngineer(p, grunt, WIDTH, HEIGHT):
    try: # draw engineer or medic boxes if necessary
        if grunt.unitType == 3:
            boxWidth = WIDTH/19
            boxGap = WIDTH/119
            dy = .14*HEIGHT
            if False and grunt.medicSpecialist:
                p.setStrokeColor(colors.lightgrey)
                p.setFillColor(colors.white)
                p.roundRect(.80*WIDTH, dy, 3*boxWidth, boxWidth, radius=3, fill=1, stroke=1)
                p.setFillColor(colors.black)
                p.drawCentredString((.80*WIDTH) + 1.5*boxWidth, dy+(boxWidth/4), _('Medic'))
                dy = dy - (boxWidth+boxGap)
            if False and grunt.engineerSpecialist:
                p.setStrokeColor(colors.lightgrey)
                p.setFillColor(colors.white)
                p.roundRect(.80*WIDTH, dy, 3*boxWidth, boxWidth, radius=3, fill=1, stroke=1)
                p.setFillColor(colors.black)
                # Translators: Abbreviation of Engineer
                p.drawCentredString((.80*WIDTH) + 1.5*boxWidth, dy+(boxWidth/4), _('Eng.'))
    except Exception, e:
        print 'drawMedicEngineer exception:', e
        pass

# Draw the weapon stat for a unitWeapon OR a weapon. Handles both.
# Which is number of box this is, as we offset downwards for each box.
# dxs are the x co-ords of the breaks in the weapon box.
def drawWeaponBox(p, x, y, dxs, textYOffset, which, WIDTH, HEIGHT, BOX_HEIGHT, weapon, unit=None):
        p.setFillColor(colors.white)
        dy = y-(which*BOX_HEIGHT)
        p.rect(x, dy, .52*WIDTH, BOX_HEIGHT, stroke=1, fill=1)
        p.setFillColor(colors.black)
        p.drawString(x+(.03*inch), dy+(.03*inch), weapon.__unicode__())

        # Now that we've gotten the name, which may be an override from a unitWeapon
        # get the associated weapon if this is a unitWeapon. So that either way, we have a weapon from here on.
        try:
            weapon = weapon.weapon
        except:
            pass
        if weapon.weaponFA:
            p.drawImage('static/FA.png', .46*WIDTH, dy+(.1*BOX_HEIGHT) , width=.9*BOX_HEIGHT, height=.8*BOX_HEIGHT, preserveAspectRatio=True, mask='auto')

        dx = dxs[0]
        p.setFillColor(colors.white)
        p.rect(dx, dy, .11*WIDTH, BOX_HEIGHT, stroke=1, fill=1)
        p.setFillColor(colors.black)
        if weapon.weaponRange > 0:
            p.drawCentredString( dx+((.11*WIDTH)/2), dy+textYOffset, str(weapon.weaponRange) )
        else:
            p.drawCentredString( dx+((.11*WIDTH)/2), dy+textYOffset, '-' )

        dx = dxs[1]
        p.setFillColor(colors.white)
        p.rect(dx, dy, .11*WIDTH, BOX_HEIGHT, stroke=1, fill=1)
        p.setFillColor(colors.black)
        if weapon.weaponDamage != -1:
            p.drawCentredString( dx+((.11*WIDTH)/2), dy+textYOffset, str(weapon.weaponDamage) )
        else:
            p.drawCentredString( dx+((.11*WIDTH)/2), dy+textYOffset, '*' )

        dx = dxs[2]
        p.setFillColor(colors.white)
        p.rect(dx, dy, .11*WIDTH, BOX_HEIGHT, stroke=1, fill=1)

        p.setFillColor(colors.black)
        if weapon.weaponAP != 0 :
            p.drawCentredString( dx+((.11*WIDTH)/2), dy+textYOffset, str(weapon.weaponAP) )
        else:
            # Check if it's a Mecha using  a CCW weapon - affects AP value
            if unit and unit.unitType == 12 and weapon.weaponType == 0:
                apString=str([1,2,3,4,5][unit.size-1])
            else:
                apString = '-'
            p.drawCentredString( dx+((.11*WIDTH)/2), dy+textYOffset, apString )


        dx = dxs[3]
        p.setFillColor(colors.white)
        p.rect(dx, dy, .11*WIDTH, BOX_HEIGHT, stroke=1, fill=1)
        p.setFillColor(colors.black)
        if weapon.weaponAE == 0 :
            AEstring = '-'
        else:
            if weapon.weaponAE == -1:
                AEstring='*'
            else:
                AEstring=str(weapon.weaponAE)
        p.drawCentredString( dx+((.11*WIDTH)/2), dy+textYOffset, AEstring )

def drawWeapons(p, unit, WIDTH, HEIGHT):
    x=.02*WIDTH
    BOX_HEIGHT=.16*inch
    MAX_HEIGHT=.068*HEIGHT
    y=.462*HEIGHT
    TOTAL_HEIGHT=.182*HEIGHT

    # Work out how big weapon stat boxes can be - based on number of weapons
    count = 0
    unitWeaponList = gom.models.UnitWeapon.objects.filter(unit=unit).order_by('mountType')
    ram = unit.getRam()

    try:
        count = unitWeaponList.count()
        if ram > 0:
            ramWeapon = gom.models.Weapons(weaponName=_('Ram'),weaponRange=0,weaponDamage=ram,weaponAE=0,weaponAP=0)
            count = count+1
        BOX_HEIGHT = TOTAL_HEIGHT/count
        if BOX_HEIGHT > MAX_HEIGHT:
            BOX_HEIGHT=MAX_HEIGHT
    except:
        pass

    print 'box height is', BOX_HEIGHT, MAX_HEIGHT, TOTAL_HEIGHT

    p.setFillColor(colors.black)
    p.drawString(x, y+(.04*inch), _('Attacks:'))
    
    p.setStrokeColor(colors.darkgrey)
    p.setFillColor(colors.darkgrey)
    p.rect(x,y-BOX_HEIGHT, .96*WIDTH, BOX_HEIGHT, fill=1)
    p.setStrokeColor(colors.lightgrey)
    # Lines in the title bar of weapons box.
    dxs = (x+.52*WIDTH, x+.63*WIDTH, x+.74*WIDTH, x+.85*WIDTH)
    dys = (y-BOX_HEIGHT, y)
    p.lines( [(dxs[0], dys[0], dxs[0],dys[1]),\
             (dxs[1], dys[0], dxs[1],dys[1]),\
             (dxs[2], dys[0], dxs[2],dys[1]),\
             (dxs[3], dys[0], dxs[3],dys[1])])

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 6)
    # Make sure only to shift box text proportionally to how much we have shrunk boxes
    textYOffset = (BOX_HEIGHT/MAX_HEIGHT) * (.01*HEIGHT) 
    p.drawString( x+.02*WIDTH, dys[0]+textYOffset, _('WEAPON'))
    p.drawCentredString( dxs[0]+((.11*WIDTH)/2), dys[0]+textYOffset, _('Range'))
    # Translators: Abbreviation of 'Damage'
    p.drawCentredString( dxs[1]+((.11*WIDTH)/2), dys[0]+textYOffset, _('Dam'))
    # Translators: Abbreviation of 'Armour Piercing'
    p.drawCentredString( dxs[2]+((.11*WIDTH)/2), dys[0]+textYOffset, _('AP'))
    # Translators: Abbreviation of 'Area of Effect'
    p.drawCentredString( dxs[3]+((.11*WIDTH)/2), dys[0]+textYOffset, _('AE'))

    i = 0
    try: # If we have a ram weapon, draw it
        drawWeaponBox(p, x, y, dxs, textYOffset, i+1, WIDTH, HEIGHT, BOX_HEIGHT, ramWeapon)
        i = i + 1 # do this after the draw, as we only want to do it if a ramWeapon really exists
    except Exception, e:
        pass
    for unitWeapon in unitWeaponList:
        i = i + 1
        drawWeaponBox(p, x, y, dxs, textYOffset, i, WIDTH, HEIGHT, BOX_HEIGHT, unitWeapon, unit)

def drawDesc(p, unit, WIDTH, HEIGHT):
    p.setFillColor(colors.white)
    p.setStrokeColor(colors.darkgrey)
    # Description box 
    fontSize=8
    MIN_FONT_SIZE = 1
    try:
        if unit.isVehicle():
            p.roundRect(.42*WIDTH, .48*HEIGHT, .56*WIDTH, .29*HEIGHT, radius=2, fill=1)
            descHeight=.278*HEIGHT
        else:
            p.roundRect(.42*WIDTH, .48*HEIGHT, .56*WIDTH, .2005*HEIGHT, radius=2, fill=1)
            descHeight=.188*HEIGHT
        descY=.488*HEIGHT
        descX=.43*WIDTH
        descWidth=.54*WIDTH
        desc=unit.desc
        if desc:
            desc = desc +'<br/><br/>'
        desc = desc + getPerkText(unit)
    except: # must be a force
        p.roundRect(.05*WIDTH,.72 *HEIGHT, .9*WIDTH, .16*HEIGHT, radius=2, fill=1)
        descY=.74*HEIGHT
        descX=.06*WIDTH
        descWidth=.88*WIDTH
        descHeight=.15*HEIGHT
        desc=unit.description

    if desc:
        while fontSize >= MIN_FONT_SIZE:
            para = paragraph.Paragraph(desc, justifyStyle(fontSize=fontSize))
            width, height = para.wrapOn(p, descWidth, descHeight)
            if height < descHeight:
                break
            fontSize = fontSize - 1
        para.canv = p
        p.translate(descX, descY)
        para.drawPara()
        p.translate(-descX, -descY)

def mobString(unit):
    for i, string in gom.models.ALL_MOBILITY_CHOICES:
        if i == unit.mobility:
            return string
    return _('Error')

def drawSizeAndMobility(p, unit, WIDTH, HEIGHT):
    sizeString = (_('None'),_('Scout'),_('Light'),_('Medium'),_('Heavy'),_('Assault'))
    p.setStrokeColor(colors.darkgrey)
    p.setFillColor(colors.white)
    x = .05*WIDTH
    y = .88 * HEIGHT
    p.roundRect( x, y, .46*WIDTH, .04*HEIGHT, radius=5, fill=1, stroke=1)
    p.roundRect( .52*WIDTH, y, .345*WIDTH, .04*HEIGHT, radius=5, fill=1, stroke=1)
    p.roundRect( .01*WIDTH, y-.005*HEIGHT, .12*WIDTH, .05*HEIGHT, radius=6, fill=1, stroke=1)
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 6)
    p.drawString( .14*WIDTH , y+.01*HEIGHT, '%s %s' % (_('Mobility:'),mobString(unit)) )

    p.drawString( .54*WIDTH , y+.01*HEIGHT, '%s %s' % (_('Size:'),sizeString[unit.size]) )
    p.setFont("Helvetica-Bold", 8)
    speed = unit.getSpeed()
    if speed < 0:
        speed = "*"
    else:
        speed = str(speed)
    p.drawCentredString( .065*WIDTH , y+.01*HEIGHT, speed )

def drawCmdTek(p, unit, WIDTH, HEIGHT):
    if not unit.cmdTek:
        return
    p.setStrokeColor(colors.darkgrey)
    p.setFillColor(colors.white)
    x = .75*WIDTH
    y = .03 * HEIGHT
    p.roundRect( x, y, .18*WIDTH, .037*HEIGHT, radius=5, fill=1, stroke=1)
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 7)
    p.drawCentredString( x+ (.18*WIDTH/2), y+.008*HEIGHT, _('CmdTek'))

def drawType(p, unit, WIDTH, HEIGHT):
    p.setStrokeColor(colors.darkgrey)
    p.setFillColor(colors.white)
    x = .02*WIDTH
    y = .54 * HEIGHT
    p.roundRect( x, y, .37*WIDTH, .035*HEIGHT, radius=5, fill=1, stroke=1)
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 7)
    if unit.unitType == 1:
        uString = _('Gruntz Squad')
    elif unit.unitType == 2:
        uString = _('Squad Attachment')
    elif unit.unitType == 3:
        uString = _('Specialist')
    elif unit.unitType == 4:
        uString = _('Commander')
    elif unit.unitType == 11:
        uString = _('Tank')
    elif unit.unitType == 12:
        uString = _('Mecha')
    elif unit.unitType == 13:
        uString = _('Support Vehicle')
    elif unit.unitType == 14:
        uString = _('ASV')
    elif unit.unitType == 15:
        uString = _('Artillery')
    elif unit.unitType == 16:
        uString = _('Vehicle Spec.')
    elif unit.unitType == 17:
        uString = _('Field Artillery')
    elif unit.unitType == 18 :
        uString = _('Air Attack Vehicle')
    elif unit.unitType == 19 :
        uString = _('Fighter')
    elif unit.unitType == 20:
        uString = _('Super-Heavy Tank')
    elif unit.unitType == 21:
        uString = _('S.H. Air Support')
    elif unit.unitType == 22:
        uString = _('Monster')
    p.drawCentredString( x+ (.37*WIDTH/2), y+.007*HEIGHT, uString)

# Calculate how small we need text in Helvetica-Bold font to be, in order to
# fit inside width
# Start at initialSize and shrink font size only if necessary
def shrinkToFitHB(p, text, width, initialSize):
    return shrinkToFit(p, text, width, initialSize, 'Helvetica-Bold')

def shrinkToFit(p, text, width, initialSize, font='Helvetica'):
    doLoop = True
    while doLoop and initialSize >= 1:
        space = p.stringWidth(text, font, initialSize)
        if space <= width:
            doLoop = False
        else:
            initialSize = initialSize -1
    return initialSize

def drawNameAndCost(p, unit, WIDTH, HEIGHT):
    cost = unit.getCost()
    NAME_X = WIDTH * .05
    NAME_Y = HEIGHT * .95
    LINE_Y = NAME_Y -.02*HEIGHT
    p.setFillColor(colors.black)
    fontSize = shrinkToFitHB(p, unit.name, .61*WIDTH ,12)
    p.setFont("Helvetica-Bold", fontSize)
    p.drawString( NAME_X, NAME_Y, unit.name )
    p.setFont("Helvetica", 10)
    p.setStrokeColor(colors.darkgrey)
    p.setFillColor(colors.white)
    p.roundRect( .67*WIDTH, NAME_Y-(.005*HEIGHT), .2*WIDTH, .04*HEIGHT, radius=5, fill=1, stroke=1)
    p.setFillColor(colors.black)
    p.drawCentredString( .77 * WIDTH, NAME_Y, '%d Pts' % cost)
    p.setStrokeColor(colors.darkgrey)
    p.lines([ (0,LINE_Y, .85*WIDTH, LINE_Y), (.85*WIDTH,LINE_Y, .88*WIDTH,LINE_Y-(.03*HEIGHT)), (.88*WIDTH, LINE_Y-(.03*HEIGHT), WIDTH, LINE_Y-(.03*HEIGHT)) ])
    # Change to use drawImage once I have a gruntz graphic with transparency
    p.drawInlineImage('static/gruntzLogo.jpg', .88*WIDTH, LINE_Y-(0.033*HEIGHT) , width=.105*WIDTH, height=.105*HEIGHT, preserveAspectRatio=True)

def drawManu(p, unit, WIDTH, HEIGHT):
    p.setFont("Helvetica", 4)
    try:
        manu = unit.manu.get()
        # Translators: Abbreviation of 'Miniature:', i.e. who makes the pictured miniature.
        p.drawString(.45*WIDTH,.01*HEIGHT, _('Mini: %s') % manu)
    except:
        pass
    p.drawString(.05*WIDTH, .01*HEIGHT, _('See Gruntz @ http://www.gruntz.biz'))

def drawBackgroundBox(p, WIDTH, HEIGHT):
    p.setFillColor(colors.lightgrey)
    p.rect(0, 0, WIDTH, HEIGHT, fill=1)

def forceCard(p, WIDTH, HEIGHT, request, force):
    drawBackgroundBox(p, WIDTH, HEIGHT)
    drawNameAndCost(p, force, WIDTH, HEIGHT)
    drawForceUnits(p, force, WIDTH, HEIGHT)
    drawDesc(p, force, WIDTH, HEIGHT)
    return p

def drawForceUnits(p, force, WIDTH, HEIGHT):
    x=.02*WIDTH
    y=.50*HEIGHT
    BOX_HEIGHT=.16*inch
    TOTAL_HEIGHT=.6*HEIGHT
    MAX_HEIGHT=.075*HEIGHT

    # Work out how big unit stat boxes can be - based on number of units
    count = 0
    units = getForceUnits(force)

    try:
         count = len(units)
         BOX_HEIGHT = TOTAL_HEIGHT/count
         if BOX_HEIGHT > MAX_HEIGHT:
             BOX_HEIGHT=MAX_HEIGHT
    except:
        pass

    p.setStrokeColor(colors.darkgrey)
    p.setFillColor(colors.darkgrey)
    p.rect(x,y+(.5*inch), .96*WIDTH, BOX_HEIGHT, fill=1)
    p.setStrokeColor(colors.lightgrey)
    # Lines in the title bar of unit box.
    dxs = (x+.63*WIDTH, x+.80*WIDTH)
    dys = (y+(.5*inch), y+(.5*inch)+BOX_HEIGHT)
    p.lines( [(dxs[0], dys[0], dxs[0],dys[1]),\
             (dxs[1], dys[0], dxs[1],dys[1])])
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 7)
    # Make sure only to shift box text proportionally to how much we have shrunk boxes
    textYOffset = (BOX_HEIGHT/MAX_HEIGHT) * (.01*HEIGHT) 
    p.drawString( x+.02*WIDTH, dys[0]+textYOffset, _('Unit'))
    # Translators: How-many of this unit are included in this army.
    p.drawCentredString( dxs[0]+((.11*WIDTH)/2), dys[0]+textYOffset, _('Count'))
    p.drawCentredString( dxs[1]+((.11*WIDTH)/2), dys[0]+textYOffset, _('Cost'))

    i = 0
    for unit in units:
        p.setFillColor(colors.white)
        i = i + 1
        dy = y+(.5*inch)-(i*BOX_HEIGHT)
        p.rect(x, dy, .63*WIDTH, BOX_HEIGHT, stroke=1, fill=1)
        p.setFillColor(colors.black)
        p.drawString(x+(.03*inch), dy+(.03*inch), unit.name)
        dx = dxs[0]
        p.setFillColor(colors.white)
        p.rect(dx, dy, .17*WIDTH, BOX_HEIGHT, stroke=1, fill=1)
        p.setFillColor(colors.black)
        p.drawCentredString( dx+((.17*WIDTH)/2), dy+textYOffset, str(units[unit]) )

        dx = dxs[1]
        p.setFillColor(colors.white)
        p.rect(dx, dy, .165*WIDTH, BOX_HEIGHT, stroke=1, fill=1)
        p.setFillColor(colors.black)
        p.drawCentredString( dx+((.165*WIDTH)/2), dy+textYOffset, str(units[unit]*unit.cost) )

def drawForceUnitsPlatypusTable(p, force, WIDTH, HEIGHT):
    styleSheet = getSampleStyleSheet()
    TABLE_WIDTH=.9*WIDTH
    TABLE_HEIGHT=.65*HEIGHT

    desc=paragraph.Paragraph('''
    <para align=center spaceb=3>blah blah blah blah blah blah blah blah blah blah long description of some very uniteresting force.</para>''', styleSheet["BodyText"])
    unitTitle = paragraph.Paragraph('''
                <para align=center spaceb=3>Unit</para>''',
                styleSheet["BodyText"])
    countTitle = paragraph.Paragraph('Count', styleSheet['BodyText'])
    costTitle = paragraph.Paragraph('Cost', styleSheet['BodyText'])
    units = getForceUnits(force)
    data= [ [unitTitle, countTitle, costTitle]]
    count = int(0)
    for unit in units:
        namePara = paragraph.Paragraph(unit.name, styleSheet['BodyText'])
        data.append([namePara, units[unit], units[unit]*unit.cost])
        print 'appending [%s][%d][%d]' % (namePara, units[unit], units[unit]*unit.cost)
        count = count+1
    print 'i think last cell is 2,%d' % (count-1)
    t=Table(data,style=[('BACKGROUND', (0, 0), (2, 0), colors.darkgrey),
                        ('TEXTCOLOR', (0, 0), (2,0), colors.white),
                        ('BACKGROUND', (0, 1), (2,count-2), colors.white),
                        ('GRID',(0,0),(-1,-1),0.5,colors.black),
                        ('ALIGN',(0,0),(-1,-1),'CENTER'),
    ], colWidths=[.68*TABLE_WIDTH, .17 * TABLE_WIDTH, .15 * TABLE_WIDTH])

    t.wrapOn(p, TABLE_WIDTH, TABLE_HEIGHT)

    t.drawOn(p, (WIDTH-TABLE_WIDTH)/2, .02*HEIGHT)
    return p


# p is the ReportLab canvas object to draw on
def oneCard(p, WIDTH, HEIGHT, request, unit):
    RIGHT=WIDTH-1
    TOP=HEIGHT-1
    # card background box
    drawBackgroundBox(p, WIDTH, HEIGHT)

    if unit.image:
        imageFilename = str('user_media/%d/%s' % (unit.owner.get().id, unit.image))
        try:
            p.drawImage(imageFilename, .020*WIDTH, .595*HEIGHT, width=.365*WIDTH,height=.265*HEIGHT, preserveAspectRatio=True)
        except IOError, e:
            print 'pdfOncard draw fail. Grunt id %d' % unit.id, e
    # image background box
    p.setFillColor(colors.white)
    p.setStrokeColor(colors.darkgrey)
    p.setLineWidth(2.5)
    p.roundRect( .015*WIDTH, .59*HEIGHT, .371*WIDTH, .27*HEIGHT, radius=2, fill=0, stroke=1)
    p.setLineWidth(1)

    #Lower square box
    p.setStrokeColor(colors.darkgrey)
    p.setFillColor(colors.white)
    p.rect(0,0,WIDTH, .27*HEIGHT, stroke=1, fill=1)
    p.setStrokeColor(colors.lightgrey)
    p.setFillColor(colors.white)
    # Bottom box 
    p.roundRect(.02*WIDTH, .025*HEIGHT, .98*RIGHT, .235*HEIGHT, radius=10, fill=1, stroke=1) 

    drawNameAndCost(p, unit, WIDTH, HEIGHT)
    drawStats(p, unit, WIDTH, HEIGHT)
    drawWeapons(p, unit, WIDTH, HEIGHT)
    drawDamage(p, unit, WIDTH, HEIGHT)
    drawCmdTek(p, unit, WIDTH, HEIGHT)
    drawSlots(p, unit, WIDTH, HEIGHT)
    drawDesc(p, unit, WIDTH, HEIGHT)
    drawType(p, unit, WIDTH, HEIGHT)
    drawManu(p, unit, WIDTH, HEIGHT)
    drawSizeAndMobility(p, unit, WIDTH, HEIGHT)
    # black box around the edge
    p.setLineWidth(1)
    p.setStrokeColor(colors.black)
    p.rect(0, 0, WIDTH, HEIGHT, stroke=1)
    return p

def newLine(p, HEIGHT, CARD_HEIGHT, CARD_SPACING, ROW):
    x,y = p.absolutePosition(0,0)
    p.translate(-x, (HEIGHT-y)) # reset to top left
    p.translate(CARD_SPACING, -((1+ROW)*(CARD_HEIGHT+CARD_SPACING)))

def PDFmulti(request, grunts, force=None):
    print 'PDFmulti called with %s' % grunts
    # Max 24 cards total
    MAX_CARDS=24
    if force:
        del(grunts[MAX_CARDS-1:])
        count = len(grunts) + 1 # +1 for force card
    else:
        del(grunts[MAX_CARDS:])
        count = len(grunts)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    try:
        response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % force.name
    except:
        try:
            response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % grunts[0].name
        except:
            response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % 'GruntzCards'

    CARD_WIDTH=2.5 * inch
    CARD_HEIGHT=3.5 * inch
    CARD_SPACING=inch/3

    if count == 1 and force==None: # Only one card
        WIDTH=CARD_WIDTH
        HEIGHT=CARD_HEIGHT
    else:
        WIDTH, HEIGHT = landscape(A4)

    buffer = StringIO()

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=(WIDTH, HEIGHT))
    p.setAuthor('Greg Farrell - Gruntomatic')

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    if count == 1 and force == None:
        p = oneCard(p, WIDTH, HEIGHT, request, grunts[0])
    else:
        i = 0
        if force:
            newLine(p, HEIGHT, CARD_HEIGHT, CARD_SPACING, 0)
            p = forceCard(p, CARD_WIDTH, CARD_HEIGHT, request, force)
            # print force card
            i = 1
        for grunt in grunts:
            if i == 8: # End of page
                i = 0
                p.showPage()
                x,y = p.absolutePosition(0,0)
                p.translate(-x, -y)
            if ( i % 4 ) == 0: # End of line of 4 cards
                newLine(p, HEIGHT, CARD_HEIGHT, CARD_SPACING, i/4)
            else:
                p.translate(CARD_WIDTH+CARD_SPACING, 0)
            p = oneCard(p, CARD_WIDTH, CARD_HEIGHT, request, grunt)
            i = i + 1

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def PDFit(request, grunt):
    return PDFmulti(request, [grunt,])

