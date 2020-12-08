from augmentation import alter
import os
import random
import numpy as np
from sklearn.model_selection import train_test_split

def build_dataset(test_sample_fraction: float = 0.2, amount_rzepak: int = 6, amount_nierzepak: int = 4):
    """
    test_sample_fraction: frakcja obserwacji przydzielonych do zbioru testowego
    amount_rzepak: ile powielen kazdego ze zdjec rzepaku
    amount_nierzepak: ile powielen kazdego ze zdjec nierzepaku 
    Wystarczy wywolac funkcje i zbior zostanie wygenerowany, 
    pod warunkiem, ze clone repa jest aktualny tzn. istnieje folder /data
    i zainstalowane sa importowane biblioteki
    """
    
    #utworzenie wektora ze sciezkami do wycietych jpg
    rzepak_pictures = os.listdir("./data/rzepak/")
    nierzepak_pictures = os.listdir("./data/nierzepak/")

    if(os.path.exists("./dataset/") == False):
        os.mkdir("./dataset/")
        os.mkdir("./dataset/train/")
        os.mkdir("./dataset/valid/")

    #train-valid sets splitting    
    rzepak_train_id, rzepak_valid_id = train_test_split(range(len(rzepak_pictures)), test_size = test_sample_fraction, random_state = 123)
    nierzepak_train_id, nierzepak_valid_id = train_test_split(range(len(nierzepak_pictures)), test_size = test_sample_fraction, random_state = 123)


    #powielenie zdjec rzepaku
    for i in rzepak_train_id:
        alter("./data/rzepak/" + rzepak_pictures[i], "./dataset/train/", amount_rzepak, prefix = "rzepak")
    for i in rzepak_valid_id:
        alter("./data/rzepak/" + rzepak_pictures[i], "./dataset/valid/", amount_rzepak, prefix = "rzepak")
    
    #powielenie zdjec nierzepaku
    for i in nierzepak_train_id:
        alter("./data/nierzepak/" + nierzepak_pictures[i], "./dataset/train/", amount_nierzepak, prefix = "nierzepak")
    for i in nierzepak_valid_id:
        alter("./data/nierzepak/" + nierzepak_pictures[i], "./dataset/valid/", amount_nierzepak, prefix = "nierzepak")
    
    return

#RUN FUNCTION - budowanie zbioru uczacego
#build_dataset()