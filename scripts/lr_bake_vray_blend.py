####################################
##  BAKE VRAY BLEND SHADER        ##
##  lr_bake_vray_blend.py         ##
##  Created by Lorena Rother      ##
##  Updated: 5 Jun 2019          ##
####################################

import pymel.core as pm
import maya.mel as mel
import maya.utils as mu
import maya.OpenMayaUI as omui
from PySide2.QtCore import *
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

class Coat:
    #class variables
    project_dir = pm.workspace(q=True, rd=True)
    need_opacity_map = False
    need_bump_map = False
    bump_is_normal = False #bump is height map by default

    def __init__(self, blend_material, coat_number, size):
        self.parent_blend_material = blend_material
        self.coat_number = coat_number
        self.colorQImage =  QtGui.QImage(size, size, QtGui.QImage.Format_RGB32)#stores color map
        self.bumpQImage =  QtGui.QImage(size, size, QtGui.QImage.Format_RGB32)#stores bump map
        self.opacityQImage =  QtGui.QImage(size, size, QtGui.QImage.Format_RGB32)#stores opacity map
        if(coat_number != None):
            #regular coat
            self.material = pm.listConnections(blend_material + ".coat_material_" + str(coat_number))
            self.matteQImage =  QtGui.QImage(size, size, QtGui.QImage.Format_RGB32)#stores matte map
        else:
            #base coat
            self.material = pm.listConnections(blend_material.base_material)
        self.isTransparent = False #keeps track if coat material is transparent
        self.hasBump = False #keeps track if coat material has bump

    def get_material(self):
        return self.material

    def get_colorQImage(self):
        return self.colorQImage

    def set_colorQImage(self, qImage):
        self.colorQImage = qImage

    def get_opacityQImage(self):
        return self.opacityQImage

    def set_opacityQImage(self, qImage):
        self.opacityQImage = qImage

    def get_bumpQImage(self):
        return self.bumpQImage

    def set_bumpQImage(self, qImage):
        self.bumpQImage = qImage

    def get_matteQImage(self):
        return self.matteQImage

    def set_matteQImage(self, qImage):
        self.matteQImage = qImage

    def get_isTransparent(self):
        return self.isTransparent

    def set_isTransparent(self, is_transparent):
        self.isTransparent = is_transparent

    def get_hasBump(self):
        return self.hasBump

    def set_hasBump(self, has_bump):
        self.hasBump = has_bump

    def set_bumpIsNormal(self, bump_is_normal):
        Coat.bump_is_normal = bump_is_normal

    def set_need_opacity_map(self, need_opacity_map):
        Coat.need_opacity_map = need_opacity_map

    def set_need_bump_map(self, need_bump_map):
        Coat.need_bump_map = need_bump_map

#Bake to size given by user input
def bake_size_input():
    #instance and show UI
    size_dialog = SizeInputDialog()
    size_dialog.show()

#Bake to 1k image
def bake_default_size():
    bake_shaders(1024)

def bake_shaders(size):
    #get selected materials, get project directory, start progress bar
    sel =  pm.ls(sl=True)
    main_progress_bar = start_progress()

    #check if anything selected
    if sel:
        #iterate over selected blend materials and bake down textures
        for blend_material in sel:
            Coat.need_opacity_map = False
            Coat.need_bump_map = False
            bake_blend(blend_material, size, main_progress_bar)
        end_progress(main_progress_bar)
    else:
        #if nothing selected end progress bar, show warning
        end_progress(main_progress_bar)
        warning_msg("Select a Vray Blend Material to bake")


####### Helper methods #######################

def get_color_or_inputs(slot_material, coat, size, progress_bar):
    mat_type = pm.objectType(slot_material)
    if mat_type == "lambert":
        get_lambert_inputs(slot_material, coat, size, progress_bar)
        return True
    if mat_type == "VRayMtl":
        get_Vray_inputs(slot_material, coat, size, progress_bar)
        return True
    if mat_type == "VRayCarPaintMtl":
        get_carPaint_inputs(slot_material, coat, size, progress_bar)
        return True
    if mat_type == "VRaySwitchMtl":
        get_switch_inputs(slot_material, coat, size, progress_bar)
        return True
    if mat_type == "VRayMtl2Sided":
        get_2sided_inputs(slot_material, coat, size, progress_bar)
        return True
    if mat_type == "VRayFastSSS2":
        get_SSS_inputs(slot_material, coat)
        return True
    if mat_type == "VRayBlendMtl":
        return None #warn to bake blend material first
    #if slot_material doesn't match any supported type return False (will trigger warning and coat will be skipped)
    else:
        return False

def get_lambert_inputs(slot_material, coat, size, progress_bar):
    #check if color connection exists
    colorMap = pm.listConnections(slot_material.color)
    bumpNode = pm.listConnections(slot_material.normalCamera)
    if(colorMap):
        get_input_connection_by_type(colorMap[0], coat, size, "color", progress_bar)
    else:
        #check if transparent
        if (slot_material.transparency.get() != (0.0, 0.0, 0.0)):
            coat.set_isTransparent(True)
            coat.set_need_opacity_map(True)
        dif_color = pm.colorManagementConvert(tds = slot_material.color.get())
        coat.get_colorQImage().fill(QtGui.QColor(dif_color[0]*255, dif_color[1]*255, dif_color[2]*255))
        print ("color: " + str(dif_color))
    if(bumpNode):
        bumpMap = pm.listConnections(bumpNode[0].bumpValue)
        if (bumpMap):
            coat.set_hasBump(True)
            coat.set_need_bump_map(True)
            get_input_connection_by_type(bumpMap[0], coat, size, "bump", progress_bar)


def get_Vray_inputs(slot_material, coat, size, progress_bar):
    #check if color connection exists
    colorMap = pm.listConnections(slot_material.color)
    bumpMap = pm.listConnections(slot_material.bumpMap)
    if(colorMap):
        #get color from connected input
        get_input_connection_by_type(colorMap[0], coat, size, "color", progress_bar)
    else:
        #check if transparent
        if (slot_material.refractionColor.get() != (0.0, 0.0, 0.0)):
            #if transparent use fog color
            dif_color = pm.colorManagementConvert(tds = slot_material.fogColor.get())
            coat.set_isTransparent(True)
            coat.set_need_opacity_map(True)
        else:
            #if not transparent use diffuse color
            dif_color = pm.colorManagementConvert(tds = slot_material.color.get())
        coat.get_colorQImage().fill(QtGui.QColor(dif_color[0]*255, dif_color[1]*255, dif_color[2]*255))
        print ("color: " + str(dif_color))
    if(bumpMap):
        coat.set_hasBump(True)#coat has bump
        coat.set_need_bump_map(True)#baked material has bump
        if (slot_material.bumpMapType.get()>0):#check if bump is set to use normal map
            coat.set_bumpIsNormal(True)
            print("bumpType: "+str(slot_material.bumpMapType.get()))
        get_input_connection_by_type(bumpMap[0], coat, size, "bump", progress_bar)

def get_carPaint_inputs(slot_material, coat, size, progress_bar):
    dif_color = pm.colorManagementConvert(tds = slot_material.color.get())
    coat.get_colorQImage().fill(QtGui.QColor(dif_color[0]*255, dif_color[1]*255, dif_color[2]*255))
    print ("color: " + str(dif_color))

def get_switch_inputs(slot_material, coat, size, progress_bar):
    #get selected number
    switch_number = slot_material.materialsSwitch.get()
    #get corresponding material and process
    chosen_material = pm.listConnections(slot_material + ".material_" + str(int(switch_number)))
    if (chosen_material):
        print(chosen_material + ":")
        get_color_or_inputs(chosen_material[0], coat, size, progress_bar)

def get_2sided_inputs(slot_material, coat, size, progress_bar):
    front_material = pm.listConnections(slot_material.front_material)
    if (front_material):
        print(front_material + ":")
        get_color_or_inputs(front_material[0], coat, size, progress_bar)

def get_SSS_inputs(slot_material, coat):
    #mat.diffuse.get()
    pass

#load qImage with texture from file, ramp or color constant
def get_input_connection_by_type(connection, coat, size, map_type, progress_bar):
    #find which QImage is needed depending on map_type
    qImage = None
    if (map_type == "color"):
        qImage = coat.get_colorQImage()
        result = get_input(connection, qImage, size, progress_bar)
        coat.set_colorQImage(result[0])
        print ("color: " + result[1])
    if (map_type == "bump"):
        qImage = coat.get_bumpQImage()
        result = get_input(connection, qImage, size, progress_bar)
        coat.set_bumpQImage(result[0])
        print ("bump: " + result[1])
    if (map_type == "matte"):
        qImage = coat.get_matteQImage()
        result = get_input(connection, qImage, size, progress_bar)
        coat.set_matteQImage(result[0])
        print ("matte: " + result[1])
        
def get_input(connection, qImage, size, progress_bar):
    #load qImage handling different input types
    connection_type = pm.objectType(connection)
    if connection_type == "file":
        #get file path
        texture_file = connection.fileTextureName.get()
        qImage.load(texture_file)
        #scale to size
        qImage = mu.executeInMainThreadWithResult( scale_down, qImage, size)
        #get repeat UV values from 2DPlacement node
        repeatU = connection.repeatU.get()
        repeatV = connection.repeatV.get()
        print (repeatU, size,repeatV)
        print ("Scale started...")
        #scale QImage to be repeated according to repeat UV values
        qImage = mu.executeInMainThreadWithResult( scale_tile, qImage, repeatU, repeatV)
        #qImage.save(Coat.project_dir + "/sourceimages/test.png", "PNG",-1)
        update_progress(progress_bar)
        print ("Scale end")
        return [qImage, texture_file]
    if connection_type == "ramp":
        #make ramp
        make_ramp(connection, qImage)
        #get repeat UV values from 2DPlacement node
        repeatU = connection.repeatU.get()
        repeatV = connection.repeatV.get()
        print ("Scale started...")
        #scale QImage to be repeated according to repeat UV values
        qImage = mu.executeInMainThreadWithResult( scale_tile, qImage, repeatU, repeatV)
        update_progress(progress_bar)
        print ("Scale end")
        return [qImage, connection]
    if connection_type == "colorConstant":
        #get color
        color = connection.inColor.get()
        qImage.fill(QtGui.QColor(color[0]*255, color[1]*255, color[2]*255))
        return [qImage, str(color)]


#Bake layers
def bake_blend(blend_material, size, progress_bar):
    #check material is Vray Blend
    if (pm.objectType(blend_material)== "VRayBlendMtl"):
        print ("--- " + blend_material + " ---")
        #instance base material Coat
        base_coat = Coat(blend_material, None, size)
        #get base color or file and store in baseQImage
        base_material = base_coat.get_material()
        continue_bake = True # false if coat was blend to exit bake_blend
        if base_material:
            print ("base material: " + base_material[0])
            #get_color_or_inputs returns False if material type is not supported
            is_supported = get_color_or_inputs(base_material[0], base_coat, size, progress_bar)
            if(is_supported == False):
                #warn and exit if base material not supported
                warning_msg("Base material type not supported( " + base_material[0] + " ).\nAborting bake for " + blend_material)
                return
            if(is_supported == None):#slot_material is a blend
                #warn and exit if base material not supported
                warning_msg("Blend inside Blend not supported.\nBake " + base_material[0] + " first, then try again.\nAborting bake for " + blend_material)
                return #exit current bake_blend

            #assign base maps to result QImages
            res_colorQImage = base_coat.get_colorQImage()#stores result color map
            res_bumpQImage = base_coat.get_bumpQImage()#stores result bump map
            res_opacityQImage = base_coat.get_opacityQImage()#stores result opacity map
            #check for transparency and bump
            is_base_transparent = base_coat.get_isTransparent()
            base_has_bump = base_coat.get_hasBump()
            if(is_base_transparent):
                #if base transparent initialize opacity map as 50% gray 
                res_opacityQImage.fill(QtGui.QColor(128, 128, 128))
            else:
                #if base not transparent initialize opacity map as white 
                res_opacityQImage.fill(QtGui.QColor(255, 255, 255))
            if(not base_has_bump):
                #if base doesn't have bump map, initialize bump map as 50% gray, or normal map as neutral blue
                if (Coat.bump_is_normal):
                    res_bumpQImage.fill(QtGui.QColor(128, 128, 255))
                else:
                    res_bumpQImage.fill(QtGui.QColor(128, 128, 128))

            #iterate over coat layers while there's a shader in the coat slot
            i=0
            while ( i<9 and pm.listConnections(blend_material + ".coat_material_" + str(i))):
                coat_material = pm.listConnections(blend_material + ".coat_material_" + str(i))
                #if tagged "_SKIP", skip coat layer
                if (coat_material[0].find("_SKIP") >= 0):
                    print("coat " + str(i) + ": " + coat_material[0] + " -- SKIPPED -- ") 
                    i += 1
                    continue
                #add coat to baked textures
                continue_bake = add_coat(blend_material, i, size, res_colorQImage,res_bumpQImage, res_opacityQImage, progress_bar)
                if (continue_bake):
                    i += 1
                else:
                    #warn and exit if base material not supported
                    warning_msg("Blend inside Blend not supported.\nBake " + coat_material[0] + " first, then try again.\nAborting bake for " + blend_material)
                    break #exit if coat was blend material inside blend material

        else:
            #if base material doesn't exist warn and exit 
            warning_msg("No base material available.\nAborting script")
            return

        if (continue_bake):
            #after all coats are baked save new images to sourceimages
            #save baked color map
            base_color_path = Coat.project_dir + "/sourceimages/" + blend_material + "_bakedColor.png"
            res_colorQImage.save(base_color_path, "PNG",-1)
            #save baked bump map 
            if (Coat.need_bump_map):
                base_bump_path = Coat.project_dir + "/sourceimages/" + blend_material + "_bakedBump.png"
                res_bumpQImage.save(base_bump_path, "PNG",-1)
            #save baked opacity map 
            if (Coat.need_opacity_map):
                transparency_file_path = Coat.project_dir + "/sourceimages/" + blend_material + "_bakedOpacity.png"
                res_opacityQImage.save(transparency_file_path, "PNG",-1)

            #create new lambert shader and shading group
            new_lambert_shader  = pm.shadingNode('lambert', name= blend_material+"_Lambert", asShader=1)
            pm.sets(name= blend_material+"_LambertSG", renderable=1, noSurfaceShader=1, empty=1)
            pm.connectAttr(new_lambert_shader + ".outColor", blend_material + "_LambertSG.surfaceShader", f=1)
            #create color file node, connect to lambert and assign color map
            color_file_node = pm.shadingNode( 'file',  name= blend_material + "_colorFile",asTexture=True)
            pm.connectAttr(color_file_node + ".outColor", new_lambert_shader + ".color", f=1)
            pm.setAttr( color_file_node +".fileTextureName", base_color_path)
            #create bump node and bump file node, connect to lambert and assign bump map
            if (Coat.need_bump_map):
                bump_node = pm.shadingNode( 'bump2d',  name= blend_material +"_bumpFile",asUtility=True)
                bump_file_node = pm.shadingNode( 'file',  name= blend_material +"_bumpNode",asTexture=True)
                pm.connectAttr(bump_file_node + ".outAlpha", bump_node + ".bumpValue", f=1)
                pm.connectAttr(bump_node + ".outNormal", new_lambert_shader + ".normalCamera", f=1)
                pm.setAttr( bump_file_node +".fileTextureName", base_bump_path)
            #create transparency file node, connect to lambert and assign opacity map
            if (Coat.need_opacity_map):
                transp_color_file_node = pm.shadingNode( 'file',  name= blend_material+"_transparencyFile",asTexture=True)
                pm.connectAttr(transp_color_file_node + ".outTransparency", new_lambert_shader + ".transparency", f=1)
                pm.setAttr( transp_color_file_node +".fileTextureName", transparency_file_path)

            #Assign Lambert shader to objects with selected material
            lambert_shader_SG = pm.listConnections(new_lambert_shader, type='shadingEngine')
            mat_SG = pm.listConnections(blend_material, type='shadingEngine')
            if (mat_SG and len(mat_SG) > 0):
                shader_objects = pm.sets(mat_SG[0], query=1)
            if shader_objects and len(shader_objects) > 0:
                for shObj in shader_objects:
                    pm.sets(lambert_shader_SG[0], e=1, forceElement=shObj)

            #Delete blend shader
            pm.delete(blend_material)
            if (mat_SG and len(mat_SG) > 0):
                pm.delete(mat_SG[0])

            #return new Lambert shader
            return new_lambert_shader
        else:
            return #exit bake_blend if coat was blend material inside blend material
    else:
        #Warn selection is not a blend material
        warning_msg( blend_material + " is not a Vray Blend Material")


#Process coat (mask coat textures with coat matte and comp into corresponding baked image [color, opacity, bump])
def add_coat(blend_material, coat_number, size, res_colorQImage, res_bumpQImage, res_opacityQImage, progress_bar):
    #initialize coat 
    current_coat = Coat(blend_material, coat_number, size)
    coat_material = current_coat.get_material()
    print ("coat " + str(coat_number) + " --------------")
    print ("name: " + coat_material[0])
    #get color or file and store in coat colorQImage
    if coat_material:
        is_supported = get_color_or_inputs(coat_material[0], current_coat, size, progress_bar)
        #warn and skip layer if material type is not supported
        if (is_supported == False):
            warning_msg("Material type on coat " + str(coat_number)+ " (" + coat_material[0] + ") is not supported.\nSkipping layer")
            return True
        if(is_supported == None):#slot_material is blend
            return False #exit current add_coat 
        else:
            #get matte
            matte = pm.listConnections(blend_material + '.blend_amount_' + str(coat_number))
            if (matte):
                get_input_connection_by_type( matte[0], current_coat, size, "matte", progress_bar)
                #check transparency and bump
                is_coat_transparent = current_coat.get_isTransparent()
                coat_has_bump = current_coat.get_hasBump()
                #fill opacity map
                if(is_coat_transparent):
                    #if transparent fill with 50% gray
                    current_coat.get_opacityQImage().fill(QtGui.QColor(128, 128, 128))
                else:
                    #if not transparent fill with white
                    current_coat.get_opacityQImage().fill(QtGui.QColor(255, 255, 255))
                if(not coat_has_bump):
                    #if coat doesn't have bump, fill with 50% gray fo height map or neutral blue for normal map
                    if (Coat.bump_is_normal):
                        current_coat.get_bumpQImage().fill(QtGui.QColor(128, 128, 255))
                    else:
                        current_coat.get_bumpQImage().fill(QtGui.QColor(128, 128, 128))

                matteQImage = current_coat.get_matteQImage()
                '''#repeat matte tile if matte repeat uv is not the same as color tile
                if(matteTile.width(),current_coat.get_colorQImage().width()):
                    matteQImage =  QtGui.QImage(size, size, QtGui.QImage.Format_RGB32)
                    mu.executeInMainThreadWithResult( comp_coat_base, matteTile, matteQImage)
                else:
                    matteQImage = current_coat.get_matteQImage()'''
                
                #matteQImage.save(Coat.project_dir + "/sourceimages/" + blend_material + "_matte_"+str(coat_number)+".png", "PNG",-1)
                #mask coat color, bump and opacity with coat matte
                print ("set matte on coat...")
                mu.executeInMainThreadWithResult(set_alpha, current_coat.get_colorQImage(),matteQImage)
                mu.executeInMainThreadWithResult(set_alpha, current_coat.get_bumpQImage(),matteQImage)
                mu.executeInMainThreadWithResult(set_alpha, current_coat.get_opacityQImage(),matteQImage)
                #composite coat over base image
                update_progress(progress_bar)
                mu.executeInMainThreadWithResult( comp_coat_base, current_coat.get_colorQImage(), res_colorQImage)
                mu.executeInMainThreadWithResult( comp_coat_base, current_coat.get_bumpQImage(), res_bumpQImage)
                mu.executeInMainThreadWithResult( comp_coat_base, current_coat.get_opacityQImage(), res_opacityQImage)
                update_progress(progress_bar)
                return True
            else:
                #if coat doesn't have matte warn and don't add to texture
                warning_msg("Coat " + str(coat_number)+ " (" + current_coat + ") has no matte.\nSkipping layer")
                print ("matte: Has no matte")
                return True


#get info from maya ramp and recreate Qt gradient to fill qImage
def make_ramp(connection, qImage):
    #get ramp values
    #type
    ramp_type = pm.getAttr(connection + ".type")
    #number of colors
    ramp_entry_size = pm.getAttr(connection + ".colorEntryList", s=1)
    #create new gradient
    #V ramp
    if ramp_type == 0:
        gradient = QtGui.QLinearGradient(QPointF(0, 0), QPointF(0, qImage.width()))
    #U ramp
    if ramp_type == 1:
        gradient = QtGui.QLinearGradient(QPointF(0, 0), QPointF(qImage.width(), 0))
    #Diagonal ramp
    if ramp_type == 2:
        gradient = QtGui.QLinearGradient(QPointF(0, 0), QPointF(qImage.width(), qImage.width()))
    #Circular ramp
    if ramp_type == 4:
        gradient = QtGui.QRadialGradient(qImage.width()/2, qImage.width()/2,qImage.width())
    #add colors to gradient
    for i in range(ramp_entry_size):
        color_position = pm.getAttr(connection + ".colorEntryList[" + str(i+1) + "].position")
        color = pm.getAttr( connection + ".colorEntryList[" + str(i+1) + "].color")
        gradient.setColorAt(color_position, QtGui.QColor(color[0]*255, color[1]*255, color[2]*255))
    #paint gradient on qImage
    painter = QtGui.QPainter(qImage)
    painter.begin(qImage)
    painter.fillRect(qImage.rect(), gradient)
    painter.end()
    
def scale_down(image, size):
    return image.scaled(size,size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

def scale_tile(image, repeatU, repeatV):
    return image.scaled(image.width()/repeatU,image.height()/repeatV, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

def set_alpha(coat, matte):
    coat.setAlphaChannel(matte)

def comp_coat_base(coat, base):
    # initialize painter and brush
    print ("QPainter started...")
    painter = QtGui.QPainter(base)
    brush = QtGui.QBrush()
    #set coat as brush texture
    brush.setTextureImage(coat)
    #fill base with coat tiles
    painter.begin(base)
    painter.fillRect(base.rect(),brush)
    painter.end()#end painter to release resources
    print ("painter complete")

#Progress Bar
def start_progress():
    main_progress_bar = mel.eval('$tmp = $gMainProgressBar');
    pm.progressBar( main_progress_bar,edit=1, beginProgress=1,isInterruptable=1,status='"processing textures ..."', maxValue=5000 )
    for j in range(1000):
        if pm.progressBar(main_progress_bar, query=True, isCancelled=True ) :
            break
        pm.progressBar(main_progress_bar, edit=True, step=1)
    return main_progress_bar

def update_progress(progress_bar):
    for j in range(500):
        if pm.progressBar(progress_bar, query=True, isCancelled=True ) :
            break
        pm.progressBar(progress_bar, edit=True, step=1)

def end_progress(progress_bar):
    pm.progressBar(progress_bar, edit=True, endProgress=True)

#Logs and UI
def print_if_not_empty(*args):
    my_string=""
    for arg in args:
        if(arg):
            my_string = my_string + str(arg) +" "
    print(my_string)

def warning_msg(msg, arg=None):
    pm.confirmDialog(title='Warning', message=msg, button='ok')

#returns maya main window as QWidget
def get_maya_main_win():
    main_window_pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_pointer), QtWidgets.QWidget)

#size input UI
class SizeInputDialog(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_main_win()):
        super(SizeInputDialog, self).__init__(parent)
        
        self.setWindowTitle("Output size")
        self.setMinimumWidth(200)
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint) #hide question mark

        self.create_widgets()
        self.create_layouts()

    def create_widgets(self):
        self.label = QtWidgets.QLabel("Enter desired texture output size:")
        self.lineEdit = QtWidgets.QLineEdit("1024")
        self.okButton = QtWidgets.QPushButton("OK")

    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.lineEdit)
        main_layout.addWidget(self.okButton)

####################################
##  BAKE VRAY BLEND SHADER        ##
##  lr_bake_vray_blend.py         ##
##  Created by Lorena Rother      ##
##  Updated: 5 Jun 2019          ##
####################################