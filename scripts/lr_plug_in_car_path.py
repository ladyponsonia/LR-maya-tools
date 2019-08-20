####################################
##  ADD PATH TO CAR RIG           ##
##  lr_plug_in_car_path.py        ##
##  Created by Lorena Rother      ##
##  Updated: 20 Aug 2019          ##
####################################

import maya.cmds as mc

sel = mc.ls(sl=1)

def connect_motionPath(sel):
    #check selection
    if (len(sel) == 3):
        motion_path = sel[0]
        curve = sel[1]
        move_ctrl = sel[2]
    else:
        warning_msg("Please select exactly 3 objects. \nMotion path, curve, car control, in that order.")
        return
    
    if ( not(mc.objectType(motion_path, isType="motionPath"))):
        warning_msg("First object selected should be a motion path.")
        return
    if ( mc.listRelatives(curve, s=1)):
        curve_shape = mc.listRelatives(curve, s=1)[0]
        if (not(mc.objectType(curve_shape, isType="nurbsCurve") or mc.objectType(curve_shape, isType="bezierCurve"))):
            warning_msg("Second object selected should be a curve.")
            return
    else:
        warning_msg("Second object selected should be a curve.")
        return

    #connect curve length and uValue to car rig
    curveInfo_node = mc.createNode("curveInfo", n= str(path_curve)+ "_curveInfo")
    mc.connectAttr(str(curve_shape) + ".worldSpace[0]", str(curveInfo_node) + ".inputCurve")
    mc.connectAttr(str(curveInfo_node) + ".arcLength", str(move_ctrl) + ".arcLength")
    mc.connectAttr(str(motion_path) + ".uValue", str(move_ctrl) + ".uValue")

def warning_msg(msg, arg=None):
    mc.confirmDialog(title='Warning', message=msg, button='ok')

connect_motionPath(sel)