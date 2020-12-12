import shutil
import os
import glob

MAIN_FOLDER_PATH = 'C:/Users/01121832/Documents/test' # MUST BE CHANGED directory of all data directories
META_DATA_PATTERN = '/**/*TL.xml'
IMG_DATA_PATTERN = '/**/*TCI.jp2'

os.chdir(MAIN_FOLDER_PATH) # set current working directory
foldersList = os.listdir('.') # for loop

for folder in foldersList:
    new_folder_path = './' + folder + '_extracted'
    os.mkdir(new_folder_path)
    
    meta_path = glob.glob('./' + folder + META_DATA_PATTERN, recursive = True)[0]
    shutil.move(meta_path, new_folder_path)
    
    img_path = glob.glob('./' + folder + IMG_DATA_PATTERN, recursive = True)[0]
    shutil.move(img_path, new_folder_path)
    
    shutil.rmtree('./' + folder)