import numpy as np
import tensorflow.keras.preprocessing.image as image
from tensorflow import keras


def predict_with_loaded_model(photo_path, model_path="trained_NN"):
    model = keras.models.load_model(model_path)
    img = image.load_img(photo_path, target_size=(200, 200))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    images = np.vstack([x])
    classes = model.predict(images, batch_size=10)
    return classes[0][0]
