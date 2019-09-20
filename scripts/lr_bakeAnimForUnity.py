####################################
##  BAKE ANIMATION                ##
##  lr_bakeAnimForUnity.py        ##
##  Created by Lorena Rother      ##
##  Updated: 25 Oct 2018          ##
####################################

import maya.cmds as mc
import string
from functools import partial

#check if UI is already open
if mc.window('bakeAnimUI', query=True, exists=True):
    mc.deleteUI('bakeAnimUI', window=True)

locators = []
meshes = []
jnts = []
#save mesh selection
def assignMeshes(locators, meshes, *args):
    sel = mc.ls(sl=True, sn=1)
    #give mesh unique name
    if sel:
        for mesh in sel: 
            meshName = mesh.split('|')[-1]
            parents = mc.listRelatives(mesh, ap=1, pa=1)
            grandParent = mc.listRelatives(parents[0], ap=1, pa=1)
            uniqueName = grandParent[0][:-5]+'_'+ meshName
            #parentConstrain  locator to mesh
            newLoc = mc.spaceLocator(name= uniqueName+'_locRef')
            locators.append(newLoc[0])
            constraint = mc.parentConstraint( mesh, newLoc)
            newName = mc.rename(mesh, uniqueName)
            meshes.append(newName)
            #display selected meshes in textfield
            if meshes:
                meshStr = ', '.join(meshes)
                mc.text(meshList, e=True, l=meshStr)
    else:
        warningMsg('Please select at least one mesh')

def resetMeshes(meshes, *args):
    meshes[:] = []
    mc.text(meshList, e=True, l='Select meshe(s)') 

#save jnt selection
def assignJnts(locators, jnts, *args):
    sel = mc.ls(sl=True, sn=1)
    if sel:
        #give base jnt unique name
        for jnt in sel: 
            jntName = jnt.split('|')[-1]
            parents = mc.listRelatives(jnt, ap=1, pa=1)
            grandParent = mc.listRelatives(parents[0], ap=1, pa=1)
            uniqueName = grandParent[0][:-5]+'_'+ jntName
            #parentConstrain  locator to jnt
            newLoc = mc.spaceLocator(name= uniqueName+'_locRef')
            locators.append(newLoc[0])
            constraint = mc.parentConstraint( jnt, newLoc)
            newName = mc.rename(jnt, uniqueName)
            jnts.append(newName)
            #display selected meshes in textfield
            if jnts:
                jntStr = ', '.join(jnts)
                mc.text(jntList, e=True, l=jntStr)
    else:
        warningMsg('Please select at least one joint')

def resetJnts(jnts, *args):
    jnts[:] = []
    mc.text(jntList, e=True, l='Select joint(s)')

def deleteLocators(locators, *args):
    mc.delete(locators)
    locators[:] = []

#bake to locators
def bakeToLocators(locators, *args):
    timeRange = getTimeline()
    channels = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
    mc.bakeResults(locators, t =timeRange, at = channels , sm=1)


#bake back to mesh
def bakeToMeshes(locators, meshes, jnts, *args):
    #delete locator parent Constraints
    constraints = mc.listRelatives(locators, typ="parentConstraint")
    mc.delete(constraints)
    #transfer visibility keys from ctrl to mesh
    for mesh in meshes: 
        parents = mc.listRelatives(mesh, ap=1, pa=1)
        grandParent = mc.listRelatives(parents[0], ap=1, pa=1)
        con = mc.connectAttr(grandParent[0]+".visibility", mesh +".visibility")
    #parent constrain mesh/jnt to corresponding locator
    objects = meshes +jnts
    #Remove meshes and jnts from hierarchy 
    mc.parent(objects, world = 1)
    for obj in objects: 
        for loc in locators:
            if (loc.find(obj)!=-1):
                    mc.parentConstraint( loc, obj)
    #for jnts bake hierarchy below
    timeRange = getTimeline()
    channels = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "visibility"]
    mc.bakeResults(objects, t =timeRange, at = channels , hi="below", sm=1)

#clean up
def cleanUp(locators, meshes, jnts, *args):
    #delete constraints
    objects = meshes + jnts
    constraints = mc.listRelatives(objects, typ="parentConstraint")
    mc.delete(constraints)
    #delete locators
    mc.delete(locators)
    #group
    geoGrp = mc.group(meshes, name = "geo", w=1)
    if (jnts):
        jntGrp = mc.group(jnts, name = "joints", w=1)
        mc.group(geoGrp, jntGrp, name = "product_name_RENAME", w=1)

#####Helper functions----------------------------------------------
def warningMsg(msg, *args):
    mc.confirmDialog(title='Warning', message=msg, button='ok') 

#get timeline range
def getTimeline(arg=None):
    minTime = mc.playbackOptions(query=True, minTime=True)
    maxTime = mc.playbackOptions(query=True, maxTime=True)
    print (minTime, maxTime)
    return (minTime, maxTime)


##### GUI ---------------------------------------------------------
win = mc.window('bakeAnimUI', title='Bake animation for Unity')
mc.columnLayout( cw=500 )
#Select
mc.frameLayout( label='SELECT', bgc = [0, 0.5, 1])
mc.rowColumnLayout(numberOfColumns=4, columnWidth=[(1, 100), (2, 200), (3, 100), (4, 100)])
mc.text(label='Assign meshes:', align='left')
meshList  =  mc.text(label='Select meshe(s)',font='obliqueLabelFont', align='left')
mc. button(label=' assign', command= partial(assignMeshes, locators, meshes))
mc. button(label=' reset', command= partial(resetMeshes, meshes))
mc.text(label='Assign base joints:', align='left')
jntList  =  mc.text(label='Select joint(s)',font='obliqueLabelFont', align='left')
mc. button(label='assign', command= partial(assignJnts, locators, jnts))
mc. button(label=' reset', command= partial(resetJnts, jnts))
mc.setParent( '..' )
mc.setParent( '..' )
mc. button(label='DELETE LOCATORS', w=500, command= partial(deleteLocators, locators))
#Bake
mc.frameLayout( label='BAKE', bgc = [0, 0.5, 1])
mc.columnLayout(cw=500)
mc. button(label='Bake to LOCATORS', w=500, command= partial(bakeToLocators, locators))
mc. button(label='Bake to MESHES and JOINTS', w=500, command= partial(bakeToMeshes, locators, meshes, jnts))
mc. button(label='Clean up', w=500, command= partial(cleanUp,  locators, meshes, jnts))
#Show
mc.showWindow('bakeAnimUI')


####################################
##  BAKE ANIMATION                ##
##  lr_bakeAnimForUnity.py        ##
##  Created by Lorena Rother      ##
##  Updated: 25 Oct 2018          ##
####################################