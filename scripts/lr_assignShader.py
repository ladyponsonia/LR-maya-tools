####################################
##  IMPORT/ASSIGN SHADER          ##
##  lr_assignShader.py            ##
##  Created by Lorena Rother      ##
##  Updated: 16 Nov 2017          ##
####################################

import maya.cmds as mc

#assign shader to selected objects
def assignShader(mat, sel):
    #get shading group
    sg = mc.listConnections(mat, d=1, et=1, t='shadingEngine')
    #assign to selected
    if (len(sel) > 0 ):
        for obj in sel:
            #print(obj, sg[0])
            mc.sets(obj, e=True, forceElement=sg[0])
        print('assigned '+sg[0]+' to selected objects')

#import shader and return it
def importShader(mat_name, mDir):
    #list materials before import
    existingMaterials = mc.ls( mat=1)
    #import shader
    filePath = mc.file(mDir+ mat_name.lstrip('_') + ".mb", i=1, typ="mayaBinary", iv=1, dns=1,rdn=1, mnc=1, op="v=0", pr=1)
    #list materials after import
    newMaterials = mc.ls( mat=1)
    #return difference between existingMaterials and newMaterials
    return [mat for mat in newMaterials if mat not in existingMaterials]

def getShader(mat, mDir):
    sel = mc.ls(sl=1)
    #add '_' to material names that start with a number
    print('mat:  '+mat)
    try:
        int(mat[0])
        mat = '_'+mat
        print('new mat:  '+mat)
    except ValueError:
        print('mat is not number')
    #check if shader name already in the scene
    if(mc.objExists(mat)):
        #ask if duplicate wanted
        answer = mc.confirmDialog(title='Warning', message= mat+' already exists in the scene. Bring duplicate?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' ) 
        if(answer == 'No'):
            #assign existing shader
            assignShader(mat, sel)
        else:
            #import and assign duplicate
            mat_name = importShader(mat, mDir)
            assignShader(mat_name, sel)
    else:
        #import and assign shader
        mat_name = importShader(mat, mDir)
        assignShader(mat_name, sel)
    sel = []

####################################
##  IMPORT/ASSIGN SHADER          ##
##  lr_assignShader.py            ##
##  Created by Lorena Rother      ##
##  Updated: 16 Nov 2017          ##
####################################
