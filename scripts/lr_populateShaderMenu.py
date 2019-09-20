####################################
##  POPULATE SHADER MENU          ##
##  lr_populateShaderMenu.py      ##
##  Created by Lorena Rother      ##
##  Updated: 16 Nov 2017          ##
####################################

import maya.cmds as mc
import os
import lr_assignShader as ash
from functools import partial

#check if window is already open
if mc.window('shaderLibraryInput', query=True, exists=True):
    mc.deleteUI('shaderLibraryInput', window=True)

def getButtonMenu(buttonMenu, arg=None):
    #query active shelf and button names
    mShelf = mc.shelfTabLayout('ShelfLayout',q=1, st=1)
    buttons = mc.shelfLayout(mShelf, q=1,ca=1)
    buttonNames = {}
    if buttons:
        for bttn in buttons:
            name= mc.shelfButton(bttn, q=1, l=1)
            buttonNames[name] = bttn
    return mShelf, buttonNames

def updateButtonMenu(buttonMenu, arg=None):
    #get active shelf and button names
    mShelf, buttonNames = getButtonMenu(buttonMenu)
    #clear optionMenu
    menuItems = mc.optionMenuGrp(buttonMenu, q=1, ils=1)
    if menuItems:
        for item in menuItems:
            mc.deleteUI(item, mi=1)
    #populate optionMenu
    mc.menuItem(p=buttonMenu+'|OptionMenu', label='new button')
    for bttn in sorted(buttonNames.keys(), key=lambda x: x.encode('ascii').lower()):
        mc.menuItem(p=buttonMenu+'|OptionMenu', label=bttn)
    return mShelf, buttonNames

def getFolderpath(folderField,arg=None):
    folderPath = mc.fileDialog2(dialogStyle=2, fm=3, cap= 'Choose folder' )
    if folderPath:
        #display selected file path in field
        mc.textField(folderField, e=1, tx= folderPath[0], font='plainLabelFont')

def populatePopupMenu(mPopup, shaderList, mDir,arg=None):
    for item in sorted(shaderList):
        #if material file add menu item
        print('shader: ',item)
        if  isinstance(item, basestring):
            print('shaderIsInstance: ',item)
            com ='import lr_assignShader as ash \nash.getShader("'+item+'","'+ mDir+'/")'
            mi = mc.menuItem(p=mPopup, l=str(item), stp='python', c= com)
        #if folder add submenu, then menu items
        else:
            print('folder: ', item)
            smi = mc.menuItem(p=mPopup, l=str(item[0]), sm=1)
            for sItem in item[1:]:
                print('subShader: ', sItem)
                com ='import lr_assignShader as ash \nash.getShader("'+sItem+'","'+ mDir+'/")'
                mi = mc.menuItem(p=smi, l=str(sItem),  stp='python', c= com)
            mc.setParent( '..' )

def create_shader_library(buttonMenu, arg=None):
    #get shelf and button names
    mShelf, buttonNames = getButtonMenu(buttonMenu)
    #find files in folder
    mDir = mc.textField(folderField,q=1,tx=1)
    shaderList = []
    if os.path.isdir(mDir):
        for mFile in os.listdir(mDir):
            #if maya file add to shaderList
            if mFile.endswith('.mb'):
                shaderList.append(mFile.strip('.mb'))
            #if folder
            if os.path.isdir(mDir +'/'+ mFile):
                #create sublist
                subList = []
                #create submanu title
                subList.append('__'+ mFile)
                #read files from folder
                subFiles = os.listdir(mDir +'/'+ mFile)
                for sFile in subFiles:
                    if sFile.endswith('.mb'):
                        subList.append(sFile.strip('.mb'))
                shaderList.append(subList)
        print(shaderList)
    else:
        mc.confirmDialog(title='Warning', message='invalid directory', button='ok')
    #check if update or new library
    bttnValue = mc.optionMenuGrp(buttonMenu, q=1, v=1)
    if bttnValue == 'new button':
        print('new button')
        #Create shelf buttton and popupMenu
        mButtonName = mc.textField(newButtonName, q=1, tx=1)
        mButton = mc.shelfButton( p=mShelf, l=mButtonName , annotation='shader library', image1='commandButton.xpm', stp='python',mip=1, c='print("pop up")')
        mPopup = mc.popupMenu(p=mButton, button=1, mm=1)
        populatePopupMenu(mPopup, shaderList, mDir)
    else:
        print('update')
        #find button's popup items
        selectedButton = mc.optionMenuGrp(buttonMenu, q=1, v=1)
        selectedButtonFullName = mShelf+'|'+buttonNames[selectedButton]
        selectedButtonPopupMenus = mc.shelfButton(selectedButtonFullName, q=1,pma=1)
        #clear popup menu
        mc.popupMenu(selectedButtonPopupMenus[-1], e=1, dai=1)
        #repopulate popup
        populatePopupMenu(selectedButtonPopupMenus[-1], shaderList, mDir)


# change newButtonName to plain font
def plainFont(arg=None):
    mc.textField(newButtonName, e=1, font='plainLabelFont')

#####UI
win = mc.window('shaderLibraryInput', title='Create shader library from dir', rtf=1)
mc.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 150), (2, 550), (3,100)])
mc.text(label='Choose folder:')
folderField = mc.textField( tx='paste folder path or browse',  font= 'obliqueLabelFont')
mc. button(label='browse', command= partial(getFolderpath, folderField))
mc.text(label='Update button:')
buttonMenu = mc.optionMenuGrp(adj=1)
updateButtonMenu(buttonMenu)
mc. button(label='Refresh list', command= partial(updateButtonMenu, buttonMenu))
mc.text(label='New button name:')
newButtonName = mc.textField(tx='name new button', font= 'obliqueLabelFont', rfc=partial(plainFont))
mc.text(label='')
mc.text(label='')
mc. button(label='Create/Update shader library', command= partial(create_shader_library, buttonMenu))
mc.showWindow(win)
mc.window(win, e=1, w=800, h=100)

####################################
##  POPULATE SHADER MENU          ##
##  lr_populateShaderMenu.py      ##
##  Created by Lorena Rother      ##
##  Updated: 16 Nov 2017          ##
####################################
