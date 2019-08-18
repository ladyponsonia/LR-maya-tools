####################################
##  REFERENCE TOOL                ##
##  lr_referenceTool.py           ##
##  Created by Lorena Rother      ##
##  Updated: 22 Aug 2017          ##
####################################

import maya.cmds as mc
from functools import partial

#check if fileReferenceTool is already open
if mc.window('fileReferenceTool', query=True, exists=True):
    mc.deleteUI('fileReferenceTool', window=True)

####FUNCTIONS

class FileRow():
    def __init__(self, id, topLayout,fileRows, arg=None):
        self.id = id
        self.fileField = 'file'+str(id)+'Field'
        self.qtyField = 'file'+str(id)+'QtyField'
        self.nsField = 'file'+str(id)+'NSField'
        self.fLayout = mc.frameLayout(p=topLayout, label='File '+str(id) )

    def displayRow(self, arg=None):
        mc.setParent( self.fLayout )
        mc.rowColumnLayout(numberOfColumns=5, columnWidth=[(1, 40),(2, 85), (3, 450), (4, 100), (5, 30)])
        mc.text(label='Qty:', align='left')
        mc.text(label='Namespace:', align='left')
        mc.text(label='File:', align='left')
        mc.text(label='')
        mc.text(label='')
        mc.textField( self.qtyField , tx= '1')
        NS = chr(64+self.id)
        mc.textField( self.nsField , tx= NS)
        mc.textField( self.fileField , tx='paste file path or browse',  font= 'obliqueLabelFont')
        mc. button(label='browse', command= partial(getFilepath, self.fileField))
        mc. symbolButton(i='smallTrash.xpm', command= partial(delRow, self.id, fileRows))
        mc.setParent( '..' )
        mc.setParent( '..' )


#Choose file and add to textField
def getFilepath(fileNumber, arg=None):
    mayaFileFilter = 'Maya Binary (*.mb);; Maya ASCII (*.ma)'
    filePath = mc.fileDialog2(fileFilter=mayaFileFilter, dialogStyle=2, fm=4, cap= 'Choose files' )
    #check if file selected
    if filePath:
        filesString = ''
        for fileName in filePath:
            filesString = filesString +',' +fileName
        filesString = filesString.lstrip(',')
        #display selected file path in field
        mc.textField(fileNumber, e=1, tx= filesString, font='plainLabelFont')


#add new file row
def addRow( topLayout, fileRows , arg=None):
    rowID = 1
    while True:
        try:
            a = fileRows[rowID]
        except (KeyError, IndexError):
            break
        else: rowID += 1

    newInstance = FileRow(rowID, topLayout, fileRows)
    #add item to dictionary
    fileRows[rowID] = newInstance
    fileRows[rowID].displayRow()
    #print(fileRows)


#delete row
def delRow(rowID, filerows, arg=None):
    #delete layout
    mc.deleteUI(fileRows[rowID].fLayout)
    #delete from dictionary
    del fileRows[rowID]
    #print(fileRows)
    
#create references
def createReferences(fileRows, arg=None):

    for k, o in fileRows.iteritems():
        qtyInput = o.qtyField
        #check qty is integer
        try:
            qty = int(mc.textField(qtyInput, q=1, tx=1 ))
        except ValueError:
            mc.confirmDialog(title='Warning', message='File '+str(k)+' quantity value must be an integer', button='ok') 
            return
        #get namespace
        NSinput = o.nsField
        NS = mc.textField(NSinput, q=1, tx=1 )
        #check if namespace is valid
        validNS = mc.namespace(vn=NS)
        if (validNS == ''):
            mc.confirmDialog(title='Warning', message='File '+str(k)+' namespace contains no legal characters. Please choose a different namespace', button='ok')
            return
        #check if namespace exists
        #if (mc.namespace(ex=NS+str(k))):
            #mc.confirmDialog(title='Warning', message='File '+str(k)+' namespace already exists. Please choose a different namespace', button='ok')
            #return
        #get file paths
        fileInput = o.fileField
        filePathString = mc.textField(fileInput, q=1, tx=1)
        filePathList =  filePathString.split(',')
        j = 1
        for filePath in filePathList:
            #check if file exists
            if (mc.file(filePath, q=1, ex=1)):
                i = 1
                k = j
                #create references
                while (i<qty+1):
                    mc.file( filePath, r=True, namespace= NS+str(k), shd='shadingNetworks' )
                    i = i + 1
                    k = k + 1
                j = k 
            else:
                mc.confirmDialog(title='Warning', message='File "'+str(filePath)+'" not valid', button='ok')

####GUI
win = mc.window('fileReferenceTool', title='File Reference Tool', w=705, h=250, rtf=1)
form = mc.formLayout('form', h=100)
#File fields and browse
topLayout = mc.frameLayout(label = '', w=705)
#dictionary to keep track of rows added and deleted
fileRows = {}
#add first file row
addRow(topLayout, fileRows)
mc.setParent( '..' )
mc.setParent( '..' )
#Create references and add row buttons
bottomLayout = mc.frameLayout('bottomLayout',  label='' )
mc.rowColumnLayout(numberOfColumns=1, columnWidth=(1,705))
mc. button(label='Add file row', command= partial(addRow, topLayout, fileRows))
mc.button(label='Create references', command= partial(createReferences, fileRows))
mc.setParent( '..' )
mc.setParent( '..' )
mc.formLayout(form, e=1, af= (bottomLayout, 'bottom', 0) )

#Show
mc.showWindow(win)


####################################
##  REFERENCE TOOL                ##
##  lr_referenceTool.py           ##
##  Created by Lorena Rother      ##
##  Updated: 22 Aug 2017          ##
####################################