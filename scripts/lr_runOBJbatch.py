import maya.cmds as mc
import subprocess

# replace mayaPath with the path on your system to mayapy.exe
mayaPath = 'C:\\Program Files\\Autodesk\\Maya2018\\bin\\mayapy.exe'
# replace scriptPath with the path to the script you just saved
scriptPath = 'V:\\Maya_preferences\\Maya\\2018\\scripts\\lr_sta_batchOBJ.py'
def massOBJexport(dir):
    maya = subprocess.Popen(mayaPath+' '+scriptPath+' '+dir,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out,err = maya.communicate()
    exitcode = maya.returncode
    if str(exitcode) != '0':
        print(err)
        print 'ERROR-ERROR-ERROR-ERROR-ERROR-ERROR-ERROR-ERROR-ERROR-ERROR-'
    else:
        print 'obj saved to %s' % (out)