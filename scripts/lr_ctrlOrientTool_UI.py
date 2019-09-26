####################################
##  CTRL ORIENT UI                ##
##  lr_ctrlOrientTool_UI.py       ##
##  Created by Lorena Rother      ##
##  Updated: 26 Sep 2019          ##
####################################

import maya.cmds as mc
import math 
import maya.OpenMaya as om
from functools import partial

#check if UI is already open
if mc.window("ctrlOrientUI", query=True, exists=True):
    mc.deleteUI("ctrlOrientUI", window=True)

#turn on track selection order
if ( not mc.selectPref(trackSelectionOrder=1, q=1)):
    mc.selectPref(trackSelectionOrder=True)

plane01 = None
plane02 = None
control = None

class DummyPlane():
    def __init__(self, sel):
        #check that sel is 3 vertices or 1 face
        if len(sel)==3:
            if (".vtx[" in sel[0] and ".vtx[" in sel[1] and ".vtx[" in sel[2]):
                self.components = sel
                self.components_string = ', '.join(self.components)
            else:
                raise Exception("Selection must be 3 vertices or 1 face")
        elif len(sel)==1:
            if (".f[" in sel[0]):
                self.components = sel
                self.components_string = sel[0]
            else:
                raise Exception("Selection must be 3 vertices or 1 face")
        else:
            raise Exception("Selection must be 3 vertices or 1 face")

    def get_normal(self):
        dplane=None
        if (".f[" in self.components[0]):
            face_verts = mc.polyListComponentConversion( self.components, ff=True, tv=True )
            verts = mc.ls(face_verts, fl=1)
            dplane= mc.polyCreateFacet( p=[mc.pointPosition(verts[0]), mc.pointPosition(verts[1]), mc.pointPosition(verts[2])] )
        else:
            dplane= mc.polyCreateFacet( p=[mc.pointPosition(self.components[0]), mc.pointPosition(self.components[1]), mc.pointPosition(self.components[2])] )
        str_normal = mc.polyInfo(dplane, fn=1)[0].split()
        mc.delete(dplane)
        return om.MVector(float(str_normal[2]), float(str_normal[3]), float(str_normal[4]))


def warning_msg(msg, arg=None):
    mc.confirmDialog(title='Warning', message=msg, button='ok')

#save and display selections
def assignSelection(number, *args):
    global plane01
    global plane02
    global control
    sel = mc.ls(os=1, sn=1)
    if sel:
        if number ==1:
            plane01= DummyPlane(sel)
            mc.text(plane01_list, e=True, l= plane01.components_string)
        elif number==2:
            plane02= DummyPlane(sel)
            mc.text(plane02_list, e=True, l= plane02.components_string)
        else:
            control = sel[0]
            mc.text(anm_control, e=True, l= str(control))

    #if nothing selected, empty field
    else:
        if number == 1:
            mc.text(plane01_list, e=True, l='')
            plane01=None
        elif number==2:
            mc.text(plane02_list, e=True, l='')
            plane02=None
        else:
            mc.text(anm_control, e=True, l='')
            control=None



def create_orient_group(*args):
    plane01_normal=None
    plane02_normal=None
    if(plane01 and control and not plane02):
        print("no plane02")
        #create helper plane. Find normals 
        plane01_normal = plane01.get_normal()
        # if only one plane is provided, find which one of the world axes is orthogonal to the normal
        if (plane01_normal*om.MVector(1,0,0) == 0):
            plane02_normal = om.MVector(1,0,0)
        elif (plane01_normal*om.MVector(0,1,0) == 0):
            plane02_normal = om.MVector(0,1,0)
        elif (plane01_normal*om.MVector(0,0,1) == 0):
            plane02_normal = om.MVector(0,0,1)
        else:
            #if none of the axes are aligned with a world axis, ask for more verts to define a 2nd plane
            warning_msg("No axes are aligned with a world axis. You'll need to select 6 vertices and then ctrl.")
            return
    elif(plane01 and control and plane02):
        #create helper plane/s. Find normals 
        plane01_normal = plane01.get_normal()
        plane02_normal = plane02.get_normal()
        if plane01_normal== plane02_normal:
            warning_msg("1st plane and 2nd plane are the same.Please select 2 different planes.")
            return


    else:
        warning_msg("Please assign at least 1 plane and a control.")
        return

    #find 3rd vector
    plane03_normal = plane01_normal^plane02_normal

    #create orient grp with same pivot as ctrl then parent ctrl
    orientGrp = mc.group(n=str(control).replace('_Ctrl', '_')+'orientGrp', em=1)
    constraint = mc.parentConstraint( control, orientGrp)
    mc.delete(constraint)
    mc.parent(control, orientGrp)

    #make rotation matrix from vectors
    #query matrix to use position row
    orientGrp_matrix = mc.xform(orientGrp,q=1, m=1)
    #query axes selection
    plane01_axis = mc.radioCollection(xyz_collection01, q=1, sl=1)
    plane02_axis = mc.radioCollection(xyz_collection02, q=1, sl=1)
    #assign vector order
    vectorX = None
    vectorY = None
    vectorZ = None
    if plane01_axis == xrb01.split("|")[-1]:
        vectorX = plane01_normal
        if plane02_axis == yrb02.split("|")[-1]:
            vectorY = plane02_normal
            vectorZ = plane03_normal
        if plane02_axis == zrb02.split("|")[-1]:
            vectorZ = plane02_normal
            vectorY = plane03_normal
    if plane01_axis == yrb01.split("|")[-1]:
        vectorY = plane01_normal
        if plane02_axis == xrb02.split("|")[-1]:
            vectorX = plane02_normal
            vectorZ = plane03_normal
        if plane02_axis == zrb02.split("|")[-1]:
            vectorZ = plane02_normal
            vectorX = plane03_normal
    if plane01_axis == zrb01.split("|")[-1]:
        vectorZ = plane01_normal
        if plane02_axis == xrb02.split("|")[-1]:
            vectorX = plane02_normal
            vectorY = plane03_normal
        if plane02_axis == yrb02.split("|")[-1]:
            vectorY = plane02_normal
            vectorX = plane03_normal

    #assign rotation matrix to orientGrp 
    mc.xform(orientGrp, m=(vectorX.x, vectorX.y, vectorX.z, 0, vectorY.x, vectorY.y, vectorY.z, 0, vectorZ.x, vectorZ.y, vectorZ.z, 0,orientGrp_matrix[12],orientGrp_matrix[13],orientGrp_matrix[14],orientGrp_matrix[15] ))
    #freeze transforms
    mc.makeIdentity(orientGrp, apply=1, t=1, n=0)


def radioSwitch (rb, *args):
    state = mc.radioButton( rb, q=1, en=1)
    alt_sel =None
    if rb==xrb02:
        alt_sel=yrb02
    if rb==yrb02:
        alt_sel=zrb02
    if rb==zrb02:
        alt_sel=xrb02
    if state:
        mc.radioButton(rb, e=1, enable=0 )
        mc.radioButton(alt_sel, e=1, sl=1 )
    else:
        mc.radioButton(rb, e=1, enable=1)

##### GUI ---------------------------------------------------------
win = mc.window('ctrlOrientUI', title='Control orient Tool', rtf=1)
mc.window(win, e=1, widthHeight=(580, 100))
mc.columnLayout( cw=500 )
#Select
mc.rowColumnLayout(numberOfColumns=6, cs=[(1, 0), (2, 5), (3, 0), (4, 10), (5, 5), (6, 5)], columnWidth=[(1, 80), (2, 300), (3, 80), (4, 30), (5, 30), (6, 30)])
mc.text(label='1st Plane:', align='left', bgc = [0.5, 0.5, 0.5])
plane01_list = mc.text(label='Select a face or 3 vertices',font='obliqueLabelFont', align='left')
mc.button(label=' assign', command= partial(assignSelection,1))
xyz_collection01 = mc.radioCollection()
xrb01 = mc.radioButton( label='x', sl=1)
yrb01 = mc.radioButton( label='y' )
zrb01 = mc.radioButton( label='z' )
mc.text(label='2nd Plane:', align='left', bgc = [0.5, 0.5, 0.5])
plane02_list  =  mc.text(label='Select a face or 3 vertices',font='obliqueLabelFont', align='left')
mc.button(label='assign', command= partial(assignSelection, 2))
xyz_collection02 = mc.radioCollection()
xrb02 = mc.radioButton( label='x' , en=0)
yrb02 = mc.radioButton( label='y' , sl=1)
zrb02 = mc.radioButton( label='z' )
mc.text(label='Control:', align='left', bgc = [0.5, 0.5, 0.5])
anm_control =  mc.text(label='Select animation control',font='obliqueLabelFont', align='left')
mc.button(label=' assign', command= partial(assignSelection, 3))
mc.setParent( '..' )
mc.setParent( '..' )
mc.radioButton( xrb01, e=1, cc = partial(radioSwitch, xrb02 ))
mc.radioButton( yrb01, e=1, cc = partial(radioSwitch, yrb02 ))
mc.radioButton( zrb01, e=1, cc = partial(radioSwitch, zrb02 ))
#Process
mc.columnLayout(cw=500)
mc. button(label='Orient control', w=575, command= partial(create_orient_group))
#Show
mc.showWindow('ctrlOrientUI')

####################################
##  CTRL ORIENT UI                ##
##  lr_ctrlOrientTool_UI.py       ##
##  Created by Lorena Rother      ##
##  Updated: 26 Sep 2019          ##
####################################





