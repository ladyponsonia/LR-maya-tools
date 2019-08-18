####################################
##  CONTROL ORIENT TOOL           ##
##  lr_ctrlOrientTool.py          ##
##  Created by Lorena Rother      ##
##  Updated: 05 Jan 2018          ##
####################################
import maya.cmds as mc
import math 

sel =  mc.ls(sl=True, fl=1)
verts = sel[0:3]
ctrl = sel[3]

#helper function to align vectors
def aimY(vect):
    xyLength = math.sqrt((vect[0] * vect[0]) + (vect[1] * vect[1]))
    vectLength =  math.sqrt((vect[0] * vect[0]) + (vect[1] * vect[1]) + (vect[2] * vect[2]))
    #xyLength will be zero when vect is pointing along the +z or -z axis
    if(xyLength == 0):
        if (vect[0] > 0):
            zAngle = math.radians(90) 
        else:
            zAngle = math.radians(-90)
    else:
        zAngle = math.acos(vect[1]/xyLength)
    xAngle = math.acos(xyLength/vectLength)
    if (vect[2] > 0):
        xAngle = xAngle 
    else:
        xAngle = -xAngle
    if (vect[0] > 0):
        zAngle = -zAngle
    else:
        zAngle = zAngle
    out = [math.degrees(xAngle), math.degrees(zAngle)]
    return out

#create orient grp with same pivot as ctrl then parent ctrl
orientGrp = mc.group(n=str(ctrl).replace('_Ctrl', '_')+'orientGrp', em=1)
constraint = mc.parentConstraint( ctrl, orientGrp)
mc.delete(constraint)
mc.parent(ctrl, orientGrp)
#freeze transforms
mc.makeIdentity(orientGrp, apply=1, t=1, r=1, s=1, n=0)
#get verts positions
vert1Pos = mc.pointPosition(verts[0])
vert2Pos = mc.pointPosition(verts[1])
vert3Pos = mc.pointPosition(verts[2])
#create helper plane. Find normal 
dummyPlane = mc.polyCreateFacet( p=[vert1Pos, vert2Pos, vert3Pos] )
stringNormal = mc.polyInfo(fn=1)[0].split()
mc.delete(dummyPlane)
print(stringNormal)
helperPlaneNormal = (float(stringNormal[2]), float(stringNormal[3]), float(stringNormal[4]))
print(helperPlaneNormal)
# angle with world up vector
rot = aimY(helperPlaneNormal)
#assign rotation to orientGrp and lock
mc.xform(orientGrp, ro=(rot[0], 0, rot[1]))
attributes = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
for attribute in attributes:
    mc.setAttr(str(orientGrp)+'.'+attribute, l=1)

####################################
##  CONTROL ORIENT TOOL           ##
##  lr_ctrlOrientTool.py          ##
##  Created by Lorena Rother      ##
##  Updated: 05 Jan 2018          ##
####################################