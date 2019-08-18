####################################
##  RIG ROPE                      ##
##  lr_rigRope.py                 ##
##  Created by Lorena Rother      ##
##  Updated: 25 Oct 2018          ##
####################################

import maya.cmds as mc
from functools import partial

#check if UI is already open
if mc.window('rigRopeWindow', query=True, exists=True):
    mc.deleteUI('rigRopeWindow', window=True)


def rigRope(arg=None):
    #input
    num_joints =  int(mc.textField(num_joints_input, q=True, tx=True))
    num_ctrls = int(mc.textField(num_ctrls_input, q=True, tx=True))
    is_stretchy = mc.checkBox(is_stretchy_input, q=1, v=1)
    #save selection
    cyl = mc.ls(sl=1)[0]
    #deselect
    mc.select(d=1)
    #get start end values for joint
    bbox = mc.exactWorldBoundingBox(cyl)
    cyl_pivot = mc.xform(cyl, q=1, t=1)
    cyl_start = cyl_pivot[0], bbox[1], cyl_pivot[2]
    cyl_end =  cyl_pivot[0], bbox[4], cyl_pivot[2]
    #create and orient joint
    joint_start = mc.joint(p= cyl_start)
    joint_end = mc.joint(p= cyl_end)
    mc.joint( joint_start, e=True, zso=True, oj='xyz' )
    mc.joint( joint_end, e=True, zso=True, oj='xyz' )
    #mc.setAttr(joint_start + ".visibility", 0)#hide joint
    #split joint
    space = (cyl_end[1] - cyl_start[1])/num_joints
    prev_joint = joint_start
    for i in range(num_joints-1):
        new_joint = mc.insertJoint(prev_joint)
        mc.move( space, new_joint, y=1, r=1)
        prev_joint = new_joint
    mc.move(cyl_end[0], cyl_end[1], cyl_end[2], joint_end, a=1, ws=1)
    #set spline ik
    ik_handle = mc.ikHandle( sj= joint_start, ee= joint_end, sol= 'ikSplineSolver', ccv=1, roc=1, scv=1 )[0]
    #get curve
    ik_curve_shape = mc.ikHandle(q=1, c=1)
    ik_curve = mc.listRelatives(ik_curve_shape, p=1)[0]
    mc.setAttr(ik_handle + ".visibility", 0)#hide ik handle
    mc.setAttr(ik_curve + ".visibility", 0)#hide ik curve

    #stretchy joints
    if (is_stretchy):
        #create curve info node and add attr
        curve_info_node = mc.arclen(ik_curve, ch=1)
        mc.addAttr(curve_info_node, longName='normalizedScale', attributeType='float')
        print(curve_info_node)
        curve_length = mc.getAttr(curve_info_node + '.arcLength')
        #create multiply/divide node
        divide_node = mc.createNode('multiplyDivide', n=ik_curve + '_normalizedScale')
        mc.setAttr (divide_node +".operation", 2)
        #make connections
        mc.connectAttr (curve_info_node + ".arcLength", divide_node + ".input1X")
        mc.setAttr (divide_node + ".input2X", curve_length)
        mc.connectAttr (divide_node + ".outputX", curve_info_node + ".normalizedScale")
        #connect to joints scaleY
        chain_joints = mc.ikHandle( ik_handle, q=1, jl=1)
        for jnt in chain_joints:
            mc.connectAttr(curve_info_node + ".normalizedScale", jnt + ".scaleY")

    #bind cylinder to joints
    mc.bindSkin(cyl, joint_start)
    #create floating joints and ctrls
    circle_ctrl = mc.circle( nr= (0, 1, 0), c= cyl_start, r = 0.5)
    mc.xform(circle_ctrl, cp=1)
    #base
    base_ctrl = mc.duplicate(circle_ctrl, n= 'base_jnt_Ctrl')
    mc.select(d=1)
    base_joint = mc.joint(p= cyl_start, n = 'base_joint')
    mc.parent( base_joint, base_ctrl)
    mc.setAttr(base_joint + ".visibility", 0)#hide joint

    #tip
    tip_ctrl = mc.duplicate(circle_ctrl, n= 'tip_jnt_Ctrl')
    mc.move( cyl_end[1]-cyl_start[1], tip_ctrl, y=1, r=1)
    mc.select(d=1)
    tip_joint = mc.joint(p= cyl_end, n= 'tip_joint')
    mc.parent( tip_joint, tip_ctrl)
    mc.setAttr(tip_joint + ".visibility", 0)#hide joint

    #mid
    space = (cyl_end[1] - cyl_start[1])/(num_ctrls -1)
    mid_joints = []
    parent_ctrl = base_ctrl
    for i in range(num_ctrls - 2):
        mid_ctrl = mc.duplicate(circle_ctrl, n= 'mid_joint' + str(i+1) +'_Ctrl')
        mc.select(d=1) 
        mid_joint = mc.joint(p= cyl_start, n = 'mid_joint' + str(i+1))
        mc.move(space*(i+1), mid_joint, y= 1, r=1)
        mc.move(space*(i+1), mid_ctrl, y= 1, r=1)
        mc.parent( mid_joint, mid_ctrl)
        mc.parent( mid_ctrl, parent_ctrl)
        mc.setAttr(mid_joint + ".visibility", 0)#hide joint
        mid_joints.append(mid_joint)
        parent_ctrl = mid_ctrl
    mc.parent( tip_ctrl, parent_ctrl)
    mc.delete(circle_ctrl)

    #bind curve to floating joints
    curve_skin_cluster = mc.skinCluster(ik_curve, base_joint, tip_joint)
    for jnt in mid_joints:
        mc.skinCluster(curve_skin_cluster, e=1, ai= jnt)
    #create master ctrl
    #double circle
    large_circle = mc.circle( nr= (0, 1, 0), c= cyl_start, n= 'Rope_MASTER_Ctrl')
    small_circle = mc.circle( nr= (0, 1, 0), c= cyl_start, r = 0.85, n= 'smallCircle')
    circle_shape = mc.listRelatives(small_circle, s=1)
    mc.parent(circle_shape, large_circle, add=1, s=1)
    mc.xform(large_circle, cp=1)
    mc.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
    mc.delete( small_circle )
    mc.parent( base_ctrl, large_circle)

    #group joint chain and parent constrain
    jnt_chain_grp = mc.group(joint_start, n= 'jointChain_grp', w=1)
    mc.parentConstraint(large_circle, jnt_chain_grp)

    #group everything
    mc.group(cyl, ik_curve, ik_handle, large_circle, jnt_chain_grp, n='rope_##',  r=1)


######## GUI ########
mc.window('rigRopeWindow', title='Rig rope')
mc.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 200), (2, 100)])
mc.text(label='Number of joints: ')
num_joints_input = mc.textField(tx='20')
mc.text(label='Number of controls: ')
num_ctrls_input = mc.textField(tx='5')
is_stretchy_input = mc.checkBox( label='Stretchy?', align = 'right')
mc. button(label='Rig', command=partial(rigRope))

#Show
mc.showWindow('rigRopeWindow')

####################################
##  RIG ROPE                      ##
##  lr_rigRope.py                 ##
##  Created by Lorena Rother      ##
##  Updated: 25 Oct 2018          ##
####################################