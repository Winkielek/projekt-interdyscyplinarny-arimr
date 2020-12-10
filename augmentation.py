from tensorflow.keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img

def alter(photo_path,output_directory,amount,prefix):
    ''' 
    Podajemy kolejno ścieżkę do konkretnego zdjęcia, folder do którego zmienione zdjęcia będą ładowane oraz ilość zdjęć,
    które chcemy uzyskać. Należy uprzednio utworzyć folder, do którego zdjęcia mają być wrzucane.
    '''
    datagen = ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest')

    img = load_img(photo_path) 
    x = img_to_array(img)  
    x = x.reshape((1,) + x.shape)  

    imageGen = datagen.flow(x, batch_size=1, save_to_dir=output_directory, save_prefix=prefix, save_format='jpg') #added seed for reproducibility [pf]
    
    i = 0
    for x in imageGen:
        i += 1
        if i == amount:
            break
