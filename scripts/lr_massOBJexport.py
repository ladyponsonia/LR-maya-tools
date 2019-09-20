######################################################
## Mass OBJ exporter script (python)                ##
##--------------------------------------------------##
## Script Written by Lucas morgan.                  ##
##--------------------------------------------------##
## Email: lucasm@enviral-design.com                 ##
##--------------------------------------------------##
## Website: www.enviral-design.com                  ##
######################################################
##Modified by Lorena Rother
##Jun 11 2019
####----------------------------------------------####

import maya.cmds as mc
import maya.mel as mel
import lr_runOBJbatch as lrobj
import maya.utils as mu

#deletes old window and preference, if it still exists
if(mc.window('uiWindow_objLoopExport', q=1, ex=1)):
	mc.deleteUI('uiWindow_objLoopExport')
if(mc.windowPref('uiWindow_objLoopExport', q=1, ex=1)):
	mc.windowPref('uiWindow_objLoopExport', r=1)
	
def dirPath(filePath, fileType):
	mc.textFieldButtonGrp('Dir', edit=True, text=str(filePath))
	return 1

def startExport(path):
	curentObjectSelection = mc.ls(sl=1,fl=1)
	filePath = getFilePath()
	for item in curentObjectSelection:
		finalExportPath = "%s/%s.obj"%(filePath, item)
		try:
			mc.select(item)
			mel.eval('file -force -typ "mayaBinary" -pr -es "%s";'%(finalExportPath))
			#print finalExportPath
		except:
			print "Ignoring object named: '%s'. Export failed "%(item)
	print "Exporting Complete!"

def browseIt():
	mc.fileBrowserDialog( m=4, fc=dirPath, ft='directory', an='Choose Directory')
	return
	
def convertToOBJ(*args):
    filePath = getFilePath()
    lrobj.massOBJexport(filePath)

def getFilePath():
    filePathStr = mc.textFieldButtonGrp('Dir', query = True, text = True)
    filePath = filePathStr.replace("\\", "/")
    return filePath

def makeGui():
	uiWindow_objLoopExport = mc.window('uiWindow_objLoopExport', title="Mass OBJ exporter", iconName='uiWindow_objLoopExport', widthHeight=(330, 160) )
	mc.columnLayout('uiColWrapper', w = 375, adjustableColumn=False, parent = 'uiWindow_objLoopExport' )
	mc.text( label='Settings', align='left', parent = 'uiColWrapper')
	mc.textFieldButtonGrp('Dir', label='Directory Path', cw3 = [80,190,50], text='(browse for directory)', buttonLabel='browse', buttonCommand=browseIt, parent = 'uiColWrapper')
	mc.button('startExport', label = "Export .mb", parent = 'uiColWrapper', width = 322, command = startExport)
	mc.button('convertToOBJ', label = "Convert to OBJ", parent = 'uiColWrapper', width = 322, command = convertToOBJ)
	mc.showWindow( uiWindow_objLoopExport )


makeGui()