####################################
##  CTRL ORIENT TOOL              ##
##  lr_ctrlOrientTool.py          ##
##  Created by Lorena Rother      ##
##  Updated: 24 Sep 2019          ##
####################################

import maya.cmds as mc
import math 
import maya.OpenMaya as om

def warning_msg(msg, arg=None):
    mc.confirmDialog(title='Warning', message=msg, button='ok')

def create_orient_group():
    #turn on track selection order
    if ( not mc.selectPref(trackSelectionOrder=1, q=1)):
        mc.selectPref(trackSelectionOrder=True)
    sel =  mc.ls(orderedSelection=True)

    if(sel):
        ctrl = sel.pop()
        verts = sel
        print("verts: ", verts)
        if(len(verts)==3 or len(verts)==6):
            #create helper plane/s. Find normals 
            helper_plane_01 = mc.polyCreateFacet( p=[mc.pointPosition(verts[0]), mc.pointPosition(verts[1]), mc.pointPosition(verts[2])] )
            plane01_str_normal = mc.polyInfo(fn=1)[0].split()
            mc.delete(helper_plane_01)
            plane01_normal = (float(plane01_str_normal[2]), float(plane01_str_normal[3]), float(plane01_str_normal[4]))
            vectorN = om.MVector(plane01_normal[0], plane01_normal[1], plane01_normal[2])

            if (len(verts)==6):
                helper_plane_02 = mc.polyCreateFacet( p=[mc.pointPosition(verts[3]), mc.pointPosition(verts[4]), mc.pointPosition(verts[5])] )
                plane02_str_normal = mc.polyInfo(fn=1)[0].split()
                mc.delete(helper_plane_02)
                plane02_normal = (float(plane02_str_normal[2]), float(plane02_str_normal[3]), float(plane02_str_normal[4]))
                vectorT = om.MVector(plane02_normal[0], plane02_normal[1], plane02_normal[2])
            else:
                # if only one plane is provided, find which one of the world axes is orthogonal to the normal
                if (vectorN*om.MVector(1,0,0) == 0):
                    vectorT = om.MVector(1,0,0)
                elif (vectorN*om.MVector(0,1,0) == 0):
                    vectorT = om.MVector(0,1,0)
                elif (vectorN*om.MVector(0,0,1) == 0):
                    vectorT = om.MVector(0,0,1)
                else:
                    #if none of the axes are aligned with a world axis, ask for more verts to define a 2nd plane
                    warning_msg("No axes are aligned with a world axis. You'll need to select 6 vertices and then ctrl.")
                    return

            #find 3rd vector
            vectorX = vectorN^vectorT

            #create orient grp with same pivot as ctrl then parent ctrl
            orientGrp = mc.group(n=str(ctrl).replace('_Ctrl', '_')+'orientGrp', em=1)
            constraint = mc.parentConstraint( ctrl, orientGrp)
            mc.delete(constraint)
            mc.parent(ctrl, orientGrp)

            #make rotation matrix from vectors
            #keep position and assign rotation matrix to orientGrp 
            orientGrp_matrix = mc.xform(orientGrp,q=1, m=1)
            mc.xform(orientGrp, m=(vectorX.x, vectorX.y, vectorX.z, 0, vectorN.x, vectorN.y, vectorN.z, 0, vectorT.x, vectorT.y, vectorT.z, 0,orientGrp_matrix[12],orientGrp_matrix[13],orientGrp_matrix[14],orientGrp_matrix[15] ))
            #freeze transforms
            mc.makeIdentity(orientGrp, apply=1, t=1, n=0)
        else:
            warning_msg("Please select 3 or 6 vertices and then ctrl")
            return
    else:
        warning_msg("Please select 3 or 6 vertices and then ctrl")
        return

####################################
##  CTRL ORIENT TOOL              ##
##  lr_ctrlOrientTool.py          ##
##  Created by Lorena Rother      ##
##  Updated: 24 Sep 2019          ##
####################################






