import maya.cmds as mc
import shutil
import os

def copy_set_HDR():
    #get project path
    project_dir = mc.workspace( q=1, rd=1 )
    print(project_dir)
    #get dome light
    lights = mc.ls(type=mc.listNodeTypes('light'))
    print(lights)
    #get domeTex node
    textureNodes = mc.listConnections(lights[0], type='file')
    print(textureNodes)
    #get HDR file
    texture_file = mc.getAttr(textureNodes[0]+'.fileTextureName')
    print(texture_file)
    file_name = texture_file.split('/')[-1]
    print(file_name)
    #copy file texture to project's sourceimages folder and set path or just set path if file already exists
    if (os.path.isfile( project_dir + '/sourceimages/' + file_name)):
        mc.setAttr(textureNodes[0]+'.fileTextureName', 'sourceimages/' + file_name, type='string')
    else:
        shutil.copy(texture_file, project_dir + '/sourceimages/' + file_name)
        mc.setAttr(textureNodes[0]+'.fileTextureName', 'sourceimages/' + file_name, type='string')