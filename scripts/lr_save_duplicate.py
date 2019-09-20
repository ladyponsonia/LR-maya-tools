####################################
##  DUPLICATE FILE IN OLD FOLDER  ##
##  lr_save_duplicate.py          ##
##  Created by Lorena Rother      ##
##  Updated: 18 Jul 2019          ##
####################################
import maya.cmds as mc
import os
import time


def save_duplicate():
    time_start= time.time()
    project_folder = mc.workspace( q=1, rd=1 )
    #print("project folder: " + project_folder)
    current_file_absPath = mc.file(q=1, sn=1)
    current_file_name = current_file_absPath.split("/")[-1]

    #save in old folder
    try:
        mc.file( rename= get_old_folder(project_folder) + make_new_name(current_file_name) )
        saved_file = mc.file( save=True, type= get_file_type(current_file_name) )
        print("saved in old folder: " + saved_file)
        #save in scenes folder
        try:
            mc.file( rename= current_file_absPath )
            saved_over = mc.file( save=True, f=1 )
            print("saved over: " + saved_over)
        except Exception as e:
            warning_msg("Error. File was not saved over.")
            print(e)
    except Exception as e:
        warning_msg("Error. File was not saved in old folder.")
        print(e)

    time_end= time.time()
    print("time elapsed: " + str(time_end - time_start) + "s")


##HELPERS
def warning_msg(msg):
    mc.confirmDialog(title='Warning', message=msg, button='ok')

#find old folder
def get_old_folder(project_folder):
    old_folder = ""
    if (os.path.isdir(project_folder + "_Old")):
        old_folder = project_folder +"_Old/"
    else:
        sku_root = project_folder.replace("/2_scenes/", "/")
        #print("sku root:" + sku_root)
        if (os.path.isdir(sku_root +"_Old")):
            old_folder = sku_root +"_Old/"
        else:
            warning_msg("Project structure not supported.")
            return -1
    #print("old folder: " + old_folder)
    return old_folder

#generate name with timestamp
def make_new_name(current_file_name):
    new_number = str(time.time()).replace(".","")
    split_name = current_file_name.rsplit(".", 1)
    new_file_name = split_name[0] + "_" + new_number + "." + split_name[1]
    return new_file_name

#get file type
def get_file_type(file_name):
    extension = file_name.split(".")[-1]
    if (extension == "mb"):
        return "mayaBinary"
    if (extension == "ma"):
        return "mayaAscii"
    else:
        return -1
####################################
##  DUPLICATE FILE IN OLD FOLDER  ##
##  lr_save_duplicate.py          ##
##  Created by Lorena Rother      ##
##  Updated: 18 Jul 2019          ##
####################################

