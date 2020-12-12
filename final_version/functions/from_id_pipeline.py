from import_plot_cord import cord_reader
from PUWG_1992_converter import converter
import math
from fileOrganizer import filelOrg
import os 
from image_download import download_data
from cut_plot import cut_plot
import shutil

def get_photo_from_id(id):
    id = str(id)

    cord_PUGW=cord_reader([id])
    cord_PUGW = cord_PUGW.get(id)

    x_cords=[] 
    y_cords =[]

    for i in cord_PUGW:
        cord_str= i.split(" ") 
        x_temp = cord_str[0]
        y_temp = cord_str[1]

        x,y = converter(x_temp,y_temp)
        
        x_cords.append(float(x))
        y_cords.append(float(y))

    x_min = min(x_cords)
    x_max = max(x_cords)
    y_min = min(y_cords)
    y_max = max(y_cords)

    x_to_download = (x_min+x_max)/2
    y_to_download = (y_min+y_max)/2

    
    download_data(str(y_to_download),str(x_to_download),date_from="2020-05-01",date_to="2020-05-31",cloud_value=50,folder_name="FOTO",records_per_image="1")
    # sciezka do poprawy 
    
    photo_folder_path ='download/'+os.listdir('download')[0]

    try:
        filelOrg(photo_folder_path)
    except:
        pass
    print('dupa')

    path_to_photos = os.listdir("../../"+photo_folder_path+"/"+os.listdir()[0])

    for i in path_to_photos:
        if "TCI" in i:
            image_path = "../../"+photo_folder_path+"/"+os.listdir()[0]+"/"+i
        if "MTD" in i: 
            XML_path =  "../../"+photo_folder_path+"/"+os.listdir()[0]+"/"+i

    print("dupa")

    cut_plot(image_path,XML_path,'../../cuted_photo.jpg',x_min,y_min,x_max,y_max)
    
    shutil.rmtree("../../download")

    return

#from_id_photo("120906_2.0003.2761/2")