import maya.cmds as mc

sel = mc.ls(sl=1)
if (sel):
    shape_nodes = mc.listRelatives(mc.ls(sl=1), s=1)
else: 
    mc.error("No objects selected.")
if(shape_nodes):
    shape_nodes_attrs = mc.listAttr(shape_nodes, k=1)
    keyed_attr_count = 0
    attrs_wanted = ['lightColor', 'intensityMult', 'diffuseContrib', 'specularContrib', 'focalLength']
    print("Attributes keyed:")
    if(shape_nodes_attrs):
        for attr in attrs_wanted:
            if (attr in shape_nodes_attrs):
                mc.setKeyframe(shape_nodes, at=attr)
                keyed_attr_count +=1
                print(attr)
    else: 
        mc.error("This object's shape doesn't have any keyable attributes.")
    if (keyed_attr_count == 0):
        mc.error("This object's shape doesn't have any of the chosen attributes to key.")
else:
    mc.error("This object doesn't have a shape node.")
