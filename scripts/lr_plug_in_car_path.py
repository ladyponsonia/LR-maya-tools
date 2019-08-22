####################################
##  ADD PATH TO CAR RIG           ##
##  lr_plug_in_car_path.py        ##
##  Created by Lorena Rother      ##
##  Updated: 22 Aug 2019          ##
####################################

import maya.cmds as mc

def create_motionPath():
    sel = mc.ls(sl=1)
    #check selection
    if (len(sel) == 2):
        curve = sel[0]
        move_ctrl = sel[1]
    else:
        warning_msg("Please select exactly 2 objects. \nCurve then car control.")
        return
    try:
        curve_shape = mc.listRelatives(curve, s=1)[0]
        if (not(mc.objectType(curve_shape, isType="nurbsCurve") or mc.objectType(curve_shape, isType="bezierCurve"))):
            warning_msg("First object selected should be a curve.")
            return
    except TypeError as tError:
        print(tError)
        warning_msg("First object selected should be a curve.")
        return
    move_ctrl_attrs = mc.listAttr(move_ctrl)
    if (("uValue" not in move_ctrl_attrs) or ("arcLength" not in move_ctrl_attrs)):
        warning_msg("Second object should be the car control that has the 'Use Path' attribute.")
        return

    #create motion path with locator
    motion_path = mc.createNode("motionPath", n= str(curve)+ "_motionPath")
    locator = mc.spaceLocator(n= str(curve)+ "_locator")[0]
    mc.connectAttr(str(curve_shape) + ".worldSpace[0]", str(motion_path)+".geometryPath")
    mc.connectAttr(str(motion_path)+".allCoordinates", str(locator) + ".translate")
    mc.connectAttr(str(motion_path)+".rotate", str(locator) + ".rotate")
    mc.connectAttr(str(motion_path)+".rotateOrder", str(locator) + ".rotateOrder")
    mc.setAttr(str(motion_path)+".frontAxis", 2)
    mc.setAttr(str(motion_path)+".upAxis", 1)
    #connect curve length and uValue to car rig
    curveInfo_node = mc.createNode("curveInfo", n= str(curve)+ "_curveInfo")
    mc.connectAttr(str(curve_shape) + ".worldSpace[0]", str(curveInfo_node) + ".inputCurve")
    try:
        mc.connectAttr(str(curveInfo_node) + ".arcLength", str(move_ctrl) + ".arcLength")
        mc.connectAttr(str(motion_path) + ".uValue", str(move_ctrl) + ".uValue")
    except RuntimeError as rtError:
        mc.delete(curveInfo_node)
        print(rtError)
        warning_msg("It looks like the rig already has some input connections.\n Clean the rig and try again")

def connect_motionPath():
    sel = mc.ls(sl=1)
    #check selection
    if (len(sel) == 2):
        motion_path = sel[0]
        move_ctrl = sel[1]
    else:
        warning_msg("Please select exactly 2 objects. \nMotion path then car control.")
        return
    if (mc.objectType(motion_path, isType="motionPath")):
        curve = mc.listConnections(str(motion_path)+".geometryPath")[0]
        curve_shape = mc.listRelatives(curve, s=1)[0]
    else:
        warning_msg("First object selected should be a motion path.")
        return
    move_ctrl_attrs = mc.listAttr(move_ctrl)
    print(move_ctrl_attrs)
    if (("uValue" not in move_ctrl_attrs) or ("arcLength" not in move_ctrl_attrs)):
        warning_msg("Second object should be the car control that has the 'Use Path' attribute.")
        return

    #connect curve length and uValue to car rig
    curveInfo_node = mc.createNode("curveInfo", n= str(curve)+ "_curveInfo")
    mc.connectAttr(str(curve_shape) + ".worldSpace[0]", str(curveInfo_node) + ".inputCurve")
    try:
        mc.connectAttr(str(curveInfo_node) + ".arcLength", str(move_ctrl) + ".arcLength")
        mc.connectAttr(str(motion_path) + ".uValue", str(move_ctrl) + ".uValue")
    except RuntimeError:
        mc.delete(curveInfo_node)
        warning_msg("It looks like the rig already has some input connections.\n Clean the rig and try again")

def warning_msg(msg, arg=None):
    mc.confirmDialog(title='Warning', message=msg, button='ok')


####################################
##  ADD PATH TO CAR RIG           ##
##  lr_plug_in_car_path.py        ##
##  Created by Lorena Rother      ##
##  Updated: 22 Aug 2019          ##
####################################