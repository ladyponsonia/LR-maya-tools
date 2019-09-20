import maya.standalone as std
import sys
import maya.cmds as mc
import maya.mel as mel
import os

def batch_obj():
    # Start Maya in batch mode
    std.initialize(name='python')
    #load obj plugin
    mc.loadPlugin("objExport")

    fileList = []
    dir = str(sys.argv[1])

    for mFile in os.listdir(dir):
        if mFile.endswith('.mb'):
            fileList.append(dir + "\\" + mFile)

    for item in fileList:
        # Open the file with the file command
        mc.file(item, force=True, open=True)
        mc.select(all=1)
        #export obj
        finalExportPath = "%s.obj"%(item[:-3])
        try:
            mc.file(finalExportPath, pr = 1, typ = "OBJexport", es = 1, op="groups=1;ptgroups=0;materials=1;smoothing=1;normals=1")
            print finalExportPath
            sys.stdout.write(finalExportPath)
        except Exception, e:
            sys.stderr.write(str(e))
            sys.exit(-1)
            print "Ignoring object named: '%s'. Export failed, probably not a polygonal object. "%(item)
    print "Exporting Complete!"

    # Starting Maya 2016, we have to call uninitialize to properly shutdown
    if float(mc.about(v=True)) >= 2016.0:
        std.uninitialize()

#mDir = "C:\\Users\\rotherlo\\Desktop\\OBJtest"
if __name__ == "__main__":
    batch_obj()

#in the cmd line run:
#mayapy V:\Maya_preferences\Maya\2018\scripts\lr_st_batchOBJ.py "C:\Users\rotherlo\Desktop\OBJtest"
#https://www.toadstorm.com/blog/?p=136