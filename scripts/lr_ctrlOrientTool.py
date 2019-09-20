import maya.cmds as mc
import math 
import maya.OpenMaya as om

def warning_msg(msg, arg=None):
    mc.confirmDialog(title='Warning', message=msg, button='ok')

sel =  mc.ls(sl=True, fl=1)
if(sel):
    ctrl = sel.pop()
    if(len(verts)==3 or len(verts)==6):
        verts = sel
        #create orient grp with same pivot as ctrl then parent ctrl
        orientGrp = mc.group(n=str(ctrl).replace('_Ctrl', '_')+'orientGrp', em=1)
        constraint = mc.parentConstraint( ctrl, orientGrp)
        mc.delete(constraint)
        mc.parent(ctrl, orientGrp)

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
            if (vectorN*om.MVector(0,1,0) == 0):
                vectorT = om.MVector(0,1,0)
            if (vectorN*om.MVector(0,0,1) == 0):
                vectorT = om.MVector(0,0,1)
            print(vectorT.x, vectorT.y, vectorT.z)

        vectorX = vectorN^vectorT

        #make rotation matrix from vectors
        #keep position and assign rotation matrix to orientGrp 
        orientGrp_matrix = mc.xform(orientGrp,q=1, m=1)
        mc.xform(orientGrp, m=(vectorX.x, vectorX.y, vectorX.z, 0, vectorN.x, vectorN.y, vectorN.z, 0, vectorT.x, vectorT.y, vectorT.z, 0,orientGrp_matrix[12],orientGrp_matrix[13],orientGrp_matrix[14],orientGrp_matrix[15] ))
        #freeze transforms
        mc.makeIdentity(orientGrp, apply=1, t=1, n=0)
    else:
        warning_msg("Please select 3 or 6 vertices and then ctrl")
else:
    warning_msg("Please select 3 or 6 vertices and then ctrl")





