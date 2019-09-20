####################################
##  SNAP                          ##
##  lr_snap.py                    ##
##  Created by Lorena Rother      ##
##  Updated: 24 Jul 2019          ##
####################################

import pymel.core as pm

sel= pm.ls(sl=True)
target = sel[0]
obj = sel[1]

# get target world pos/rot and offset(frozen transforms)
targetPos = target.worldMatrix.get()
#print( "target Pos: " , targetPos)
target_ft_offset = find_ft_offset(target)
#print( "target ft offset: " , target_ft_offset)
#offset for obj frozen transforms
obj_ft_offset = find_ft_offset(obj)
#print( "obj ft offset: " , obj_ft_offset)
#get targetPos + target offset - obj offset in obj space
objParentInv = obj.parentInverseMatrix.get()
objPos = target_ft_offset * obj_ft_offset.inverse() * targetPos * objParentInv
#assign values to obj
obj.setMatrix( objPos)

#find freeze transforms offset
def find_ft_offset(obj):
    #create locator and parent constraint
    objLoc = pm.spaceLocator()
    objConstraint = pm.parentConstraint( obj, objLoc)
    #find diference between obj and loc
    locWorldPos = objLoc.worldMatrix.get()
    objWorldPos = obj.worldMatrix.get()
    offset = locWorldPos * objWorldPos.inverse()
    #print( obj, "offset: " , offset)
    pm.delete(objLoc)
    return offset

####################################
##  SNAP                          ##
##  lr_snap.py                    ##
##  Created by Lorena Rother      ##
##  Updated: 24 Jul 2019          ##
####################################

###Old Script####
'''import maya.cmds as mc

selection =  mc.ls(sl=True)
posSel = selection[0]
objSel = selection[1:]

#create posLoc to find posSel pivot
posLoc = mc.spaceLocator(name= 'posLoc')
constraint = mc.parentConstraint( posSel, posLoc)
mc.delete(constraint)

#get posLoc rotation
tValues = mc.xform( posLoc, ws=True, q=True, t=True)  
tx,ty,tz = tValues[0],tValues[1],tValues[2]
#get posLoc rotation
rValues = mc.xform( posLoc, ws=True, q=True, ro=True)  
rx,ry,rz = rValues[0],rValues[1],rValues[2]


for object in objSel:
    
    #check for freeze transforms on objSel
    objLoc = mc.spaceLocator()
    objConstraint = mc.parentConstraint( object, objLoc)
    objSel_tValues = mc.xform( object, ws=True, q=True, t=True) 
    objLoc_tValues = mc.xform( objLoc, ws=True, q=True, t=True) 
    ft_offset = [objSel_tValues[0] - objLoc_tValues[0], objSel_tValues[1] - objLoc_tValues[1], objSel_tValues[2] - objLoc_tValues[2]]
    mc.delete(objLoc)
    
    #assign values + freeze transform offset to objSel
    mc.xform( object, a=True, t=(tx+ft_offset[0],ty+ft_offset[1],tz+ft_offset[2])) 
    mc.xform( object, a=True, ro=(rx,ry,rz))    
    
    #key existing anim curves  
    attributes = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    
    for attribute in attributes:
        keyCount = mc.keyframe(object, at=attribute, q=True, kc=True)
        if keyCount>0:
            mc.setKeyframe(object, at=attribute)


mc.delete(posLoc[0])'''
