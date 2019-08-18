####################################
##  VRAY ZDEPTH TOOL              ##
##  lr_zDepth_tool.py             ##
##  Created by Lorena Rother      ##
####################################

import maya.cmds as mc

if (mc.pluginInfo('vrayformaya.mll', q=1, l=1) == 0):
    mc.loadPlugin ('vrayformaya.mll')

#check for zDepth render element
re = mc.ls(typ='VRayRenderElement')
if (u'Z_depth' not in re):
    mc.confirmDialog(title='Warning', message='Cannot find Z_depth render element. \n This tool is intended to be used in a Light Rig  file that has a Z_depth render element.', button='ok') 
else:

    #save camera and focus object selections
    sel = mc.ls(sl=1)
    if (len(sel) == 2):
        cam = sel[0]
        obj = sel[1]

        #create camera locator
        camLoc = mc.spaceLocator(name= cam+'_loc')
        constraint1 = mc.pointConstraint( cam, camLoc)

        #create obj, white depth and black depth locators
        objLoc = mc.spaceLocator(name= str(obj)+'_loc')
        constraint2 = mc.pointConstraint( obj, objLoc)

        whiteLoc = mc.spaceLocator(name= 'whiteDepth_loc')
        constraint3 = mc.pointConstraint( obj, whiteLoc)
        mc.delete(constraint3)
        mc.parent(whiteLoc, objLoc)
        blackLoc = mc.duplicate(name= 'blackDepth_loc')

        #create  white depth distance measurement
        wd_Distance = mc.distanceDimension(camLoc, whiteLoc)
        #create  black depth distance measurement
        bd_Distance = mc.distanceDimension(camLoc, blackLoc)

        #conect distance to zDepth
        mc.connectAttr(str(wd_Distance)+'.distance', 'Z_depth.vray_depthWhite')
        mc.connectAttr(str(bd_Distance)+'.distance', 'Z_depth.vray_depthBlack')

        #group distance measurements and locators
        zDepth_grp = mc.group(wd_Distance, bd_Distance, camLoc, objLoc, n='zDepth_grp')
        #add black depth and white depth attributes
        mc.addAttr(zDepth_grp, ln='blackDepth', at='float', k=True)
        mc.addAttr(zDepth_grp, ln='whiteDepth', at='float', k=True)
        #lock and hide attrs not needed
        grp_attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz','visibility']
        for att in grp_attrs:
            mc.setAttr(str(zDepth_grp)+'.'+att, k=0, l=1)

        #get object boundingbox
        bbox = mc.exactWorldBoundingBox(obj)
        xLength = bbox[3] - bbox[0]
        yLength = bbox[4] - bbox[1]
        zLength = bbox[5] - bbox[2]
        locDistance = max(xLength,yLength,zLength)/2

        #set white/black depth attrs as locDistance
        mc.setAttr(str(zDepth_grp)+'.blackDepth', locDistance)
        mc.setAttr(str(zDepth_grp)+'.whiteDepth', -locDistance)

        #create object-cam vector and normalize
        mc.createNode('plusMinusAverage', name='cam_'+str(obj)+'_Vector')
        mc.setAttr('cam_'+str(obj)+'_Vector.operation', 2)
        mc.connectAttr(str(camLoc[0])+'Shape.worldPosition','cam_'+str(obj)+'_Vector.input3D[0]')
        mc.connectAttr(str(objLoc[0])+'Shape.worldPosition','cam_'+str(obj)+'_Vector.input3D[1]')

        mc.createNode('vectorProduct', name='cam_'+str(obj)+'_VectorNormalized')
        mc.setAttr('cam_'+str(obj)+'_VectorNormalized.operation', 0)
        mc.setAttr('cam_'+str(obj)+'_VectorNormalized.normalizeOutput', 1)
        mc.connectAttr('cam_'+str(obj)+'_Vector.output3D','cam_'+str(obj)+'_VectorNormalized.input1')

        #create locators' move vectors
        mc.createNode('multiplyDivide', name='whiteLoc_Distance')
        mc.connectAttr(str(zDepth_grp)+'.whiteDepth','whiteLoc_Distance.input2X')
        mc.connectAttr(str(zDepth_grp)+'.whiteDepth','whiteLoc_Distance.input2Y')
        mc.connectAttr(str(zDepth_grp)+'.whiteDepth','whiteLoc_Distance.input2Z')
        mc.connectAttr('cam_'+str(obj)+'_VectorNormalized.output','whiteLoc_Distance.input1')

        mc.createNode('multiplyDivide', name='blackLoc_Distance')
        mc.connectAttr(str(zDepth_grp)+'.blackDepth','blackLoc_Distance.input2X')
        mc.connectAttr(str(zDepth_grp)+'.blackDepth','blackLoc_Distance.input2Y')
        mc.connectAttr(str(zDepth_grp)+'.blackDepth','blackLoc_Distance.input2Z')
        mc.connectAttr('cam_'+str(obj)+'_VectorNormalized.output','blackLoc_Distance.input1')

        #connect locator vectors to locators translates
        mc.connectAttr('blackLoc_Distance.output', str(blackLoc[0])+'.translate')
        mc.connectAttr('whiteLoc_Distance.output', str(whiteLoc[0])+'.translate')

    else:
        mc.confirmDialog(title='Warning', message='Please select one camera and one focus object', button='ok') 

mc.select(cl=1)

####################################
##  VRAY ZDEPTH TOOL              ##
##  lr_zDepth_tool.py             ##
##  Created by Lorena Rother      ##
####################################
