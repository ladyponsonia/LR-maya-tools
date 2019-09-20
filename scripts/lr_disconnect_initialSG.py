import maya.cmds as mc

#get Lambert1
mc.select("initialShadingGroup")
sel = mc.ls(sl=1)
#get initialShadingGroup
init_SG = mc.listConnections(sel, type='shadingEngine')
#find nodes connected to initialShadingGroup and remove duplicates
dag_set_members =  list(set(mc.sets(init_SG, query=1)))
#split nodes into transforms list and shape list(for components that have Lambert1 assigned)
dag_set_transforms = []
dag_set_shapes = []
for member in dag_set_members: 
    if (':' in member):
        member_main = member.split('.')[0]
        member_shape = mc.listRelatives(member_main, s=1)[0]
        dag_set_shapes.append(member_shape)
    else:
        dag_set_transforms.append(member)
#break connection for transforms
i=0
while(i<len(dag_set_transforms)):
    print(dag_set_transforms[i])
    dag_connection = mc.listConnections(str(dag_set_transforms[i]) +'.instObjGroups[0]', d=1, p=1)
    print(dag_connection)
    try:
        mc.disconnectAttr(str(dag_set_transforms[i]) +'.instObjGroups[0]', dag_connection[0])
    except RuntimeError as e:
        print(e)
    i+=1
#break connection for shapes
i=0
while(i<len(dag_set_shapes)):
    print(dag_set_shapes[i])
    dag_connection = mc.listConnections(str(dag_set_shapes[i]) +'.instObjGroups.objectGroups[0]', d=1, p=1)
    print(dag_connection)
    try:
        mc.disconnectAttr(str(dag_set_shapes[i]) +'.instObjGroups.objectGroups[0]', dag_connection[0])
    except RuntimeError as e:
        print(e)
    i+=1