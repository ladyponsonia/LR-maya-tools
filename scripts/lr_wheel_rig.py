####################################
##  WHEEL AUTO ROTATE RIG         ##
##  lr_wheel_rig.py               ##
##  Created by Lorena Rother      ##
##  Updated: 20 Aug 2019          ##
####################################

import maya.cmds as mc

sel = mc.ls(sl=1)
master_ctrl = sel[0]
move_ctrl = sel[1]
wheels = sel[2:]

#create extra attrs on move_ctrl
#user choices
mc.addAttr(move_ctrl, ln="Auto_Rotate", at="bool", k=True, dv=0 )#auto rotate on/off switch
mc.addAttr(move_ctrl, ln="Use_Path", at="bool", k=True, dv=0 )#When 0 calculates using translate value, when 1 uses path uValue
#hidden attrs
mc.addAttr(move_ctrl, ln="arcLength", at="float", k=True, dv=0, h=1) 
mc.addAttr(move_ctrl, ln="uValue", at="float", k=True, dv=0, h=1)


for wheel in wheels:
    #Get wheel diameter
    #get wheel bounding box
    bbox = mc.exactWorldBoundingBox(wheel)
    width = bbox[3] - bbox[0]
    diam = bbox[5] - bbox[2]
    #create distance measurement
    loc_tx = bbox[0] + width/2
    loc_tz = bbox[2] + diam/2
    diam_Shape = mc.distanceDimension( sp=(loc_tx,bbox[1],loc_tz), ep=(loc_tx,bbox[4],loc_tz) )
    diam_Transform = mc.listRelatives(diam_Shape, p=1)
    diam_Transform = mc.rename(diam_Transform[0], str(wheel)+"_diameter")
    mc.parent(diam_Transform, master_ctrl)
    diam_Shape = mc.listRelatives(diam_Transform, s=1)
    wheel_diameter = mc.rename(diam_Shape[0], str(wheel)+"_diameterShape")
    mc.setAttr( str(wheel_diameter)+".visibility", 0 )
    #Add wheel radius attr and connect mesurement distance to it
    mc.addAttr(move_ctrl, ln= str(wheel)+"_wheelRadius", at="float", k=True, dv=0, h=1)
    mc.connectAttr(str(wheel)+ "_diameterShape.distance", str(move_ctrl) + "." + str(wheel)+"_wheelRadius", f=1)
    #rename locators created by distance measurement
    locators = mc.listConnections(wheel_diameter)
    mc.select(locators[0], r=1)
    distLoc01 = mc.rename(locators[0], str(wheel)+"_distLoc01")
    mc.select(locators[1], r=1)
    distLoc02 = mc.rename(locators[1], str(wheel)+"_distLoc02")
    #parent locators to wheel_geo and hide
    mc.parent(distLoc01, wheel)
    mc.parent(distLoc02, wheel)
    mc.setAttr( str(distLoc01)+".visibility", 0 )
    mc.setAttr( str(distLoc02)+".visibility", 0 )

    #Create wheel control and locator
    wheel_Ctrl = mc.circle(n=wheel+"_Ctrl", r=diam/4, nrx=90)
    curve_constraint = mc.parentConstraint( wheel, wheel_Ctrl)
    mc.delete(curve_constraint)
    mc.move((width/2)+(width/8), wheel_Ctrl, r=True, x=True)
    #delete history
    mc.delete(ch=True) 
    #freeze transforms
    mc.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
    #shape
    mc.select(str(wheel_Ctrl[0])+".cv[0]", r=True)
    mc.select(str(wheel_Ctrl[0])+".cv[2]", add=True)
    mc.select(str(wheel_Ctrl[0])+".cv[4]", add=True)
    mc.select(str(wheel_Ctrl[0])+".cv[6]", add=True)
    mc.scale(1,0.2,0.2)
    mc.parent(wheel_Ctrl[0], move_ctrl)
    #locator
    wheelLoc = mc.spaceLocator(name= str(wheel)+"_loc")
    constraint = mc.parentConstraint( wheel, wheelLoc)
    mc.delete(constraint)
    mc.parent(wheel, wheelLoc)
    mc.parent(wheelLoc, wheel_Ctrl[0])
    mc.setAttr( str(wheelLoc[0])+"Shape.visibility", 0 ) 
    
    #Create null groups to track position
    mc.select(cl=1)
    wheelDir = mc.group(n=str(wheel)+"Dir", em=1)
    grp_constraint = mc.parentConstraint(wheelLoc, wheelDir)
    mc.delete(grp_constraint)
    mc.parent(wheelDir, move_ctrl)
    wheelOld = mc.duplicate(wheelDir, n=str(wheel)+"Old")
    mc.parent(wheelOld, master_ctrl)
    radius = (mc.getAttr(str(wheel_diameter)+".distance"))/2
    mc.move(0,0,radius, wheelDir, r=1)

    #Add wheel drive attr
    mc.addAttr(move_ctrl, ln= str(wheel)+"_wheelDrive", at="float", k=True, dv=0, h=1)
    #Add wheel expression
    #based on expression from https://lesterbanks.com/2016/09/build-wheel-rig-maya-using-world-vectors/
    mc.expression( n= str(wheel)+"_exp", s="float $diameter = " + str(move_ctrl) + "." + str(wheel)+"_wheelRadius; vector $moveVectorOld = `xform -q -ws -t "+ str(wheel)+"Old`; vector $moveVector = `xform -q -ws -t "+ str(wheelLoc[0])+"`; vector $dirVector = `xform -q -ws -t "+ str(wheel)+"Dir`; vector $wheelVector = ($dirVector - $moveVector); vector $motionVector = ($moveVector - $moveVectorOld); float $distance = mag($motionVector); $dot = dotProduct($motionVector, $wheelVector, 1); "+ str(move_ctrl) + "." + str(wheel)+ "_wheelDrive = "+ str(move_ctrl) + "." + str(wheel)+ "_wheelDrive + 360 / (3.1416*$diameter) * ($dot*$distance) * (" + str(move_ctrl) +".Auto_Rotate); xform -ws -t ($moveVector.x) ($moveVector.y) ($moveVector.z) "+ str(wheel)+ "Old;")

    #Add path drive attr
    mc.addAttr(move_ctrl, ln= str(wheel)+"_pathDrive", at="float", k=True, dv=0, h=1)
    #Add path expression
    mc.expression( n="path_exp", s="float $circumference = " + str(move_ctrl) + "." + str(wheel)+ "_wheelRadius * 6.2832; float $distance = " + str(move_ctrl) + ".arcLength * " + str(move_ctrl) + ".uValue;" + str(move_ctrl) + "." + str(wheel)+ "_pathDrive = ($distance/$circumference)*360 * (" + str(move_ctrl) + ".Auto_Rotate);")
    
    #Connect wheel drive or path drive to locator rotation depending on user choices
    condition_node = mc.createNode("condition", n= str(wheel)+ "_condition")
    mc.connectAttr( str(move_ctrl) + "." + str(wheel)+ "_wheelDrive", str(condition_node) + ".colorIfFalseR")
    mc.connectAttr( str(move_ctrl) + "." + str(wheel)+ "_pathDrive", str(condition_node) + ".colorIfTrueR")
    mc.connectAttr( str(move_ctrl) + ".Use_Path", str(condition_node) + ".firstTerm")
    mc.connectAttr( str(condition_node) + ".outColorR", str(wheelLoc[0]) + ".rotateX")
    mc.setAttr(str(condition_node) + ".secondTerm", 1)

####################################
##  WHEEL AUTO ROTATE RIG         ##
##  lr_wheel_rig.py               ##
##  Created by Lorena Rother      ##
##  Updated: 20 Aug 2019          ##
####################################