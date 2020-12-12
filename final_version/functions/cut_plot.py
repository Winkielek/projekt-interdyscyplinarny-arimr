import os
import rasterio
from rasterio import plot
import matplotlib.pyplot as plt
from osgeo import gdal
import xml.etree.ElementTree as ET


def cut_plot(photo_path,XML_path, output_path, xmin, ymin, xmax, ymax):
    """
    photo_dir_path: sciezka do katalogu surowa_paczka.SAFE
    output_path: sciezka pliku wycietego zdjecia np.: zdjecie.png
    xmin, ymin, xmax, ymax: wspolrzedne prostokata do wyciecia
    """
    
    
    
    #XML part
    root = ET.parse(XML_path).getroot()
    epsg_info = list(list(root)[1])[0].find("HORIZONTAL_CS_CODE").text[5:]
    
    
    # photos_paths = os.listdir(photo_dir_path + "/GRANULE/" + target_dir + "/IMG_DATA/R10m")
    #for f in photos_paths:
       # if(f.find("TCI") != -1):
         #   photo_path = photo_dir_path + "/GRANULE/" + target_dir + "/IMG_DATA/R10m/" + f
          #  break
    
    #JP2 to TIFF
    gdal.Translate("temp_tiff.tiff", photo_path)
    
    #Wycinanie opcje
    opt = gdal.WarpOptions(srcSRS = 'epsg:'+epsg_info, dstSRS = 'epsg:4326', 
                       outputBounds = (xmin, ymin, xmax, ymax), format = "Gtiff")
    
    #Wycinanie
    res = gdal.Warp('usunac.tiff', 'temp_tiff.tiff', options = opt)
    
    #Wyciete do png
    gdal.Translate(output_path, res)
    
    #Usuwanie temp_tiff
    os.remove("temp_tiff.tiff")
    os.remove("usunac.tiff")
    os.remove(output_path + ".aux.xml")
    
    del res
    
    return