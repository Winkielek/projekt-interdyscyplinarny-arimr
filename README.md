# Projekt interdyscyplinarny - kryptonim "rzepak"




- CREODIAS_client: skrypty od QED
- /data: folder z danymi (zdjęciami) wyciętych działek do zbioru uczącego
- building_dataset.py: funkcja do zbudowania zbioru uczącego lokalnie:
    
    - działa powielając zdjęcia z folderu /data
    - tworzy folder /dataset z podfolderami /train /valid + /rzepak /nierzepak, czyli struktura przyjmowana przez model
    - sampling podziału train/valid reprodukowalny z użyciem random_state
    - [issue](https://github.com/Winkielek/projekt_interdyscyplinarny_arimr/issues/3#issue-759278752) reprodukowalność powielania zdjęć, aktualnie rozwiązane seed-em na początku skryptu   
    
- Ładowanie sieci:
```
from tensorflow import keras
model = keras.models.load_model('trained_NN')
```

ABY DZIAŁAŁO NALEŻY POBRAĆ FOLDER KEYS I WRZUCIĆ DO CREODIAS CLIENT 
Tutaj mozna je pobrać:
https://cdn.discordapp.com/attachments/782536177353228299/787757906627002468/CREODIAS_client_2.zip
- Odpalenie Dockera:
Aby go odpalić należy najpierw pobrać samego Dockera. Nas interesuje Docker Enigne(https://docs.docker.com/engine/install/ubuntu/), 
a także Docker-Compose(https://docs.docker.com/compose/install/)
Wchodzimy do foldera /Docker. Następnie klepiemy komendę:
```
sudo docker-compose build
```
Jak się zbuduje to piszemy:

```
sudo docker-compose up
```
i klikamy w linka od apki dashowej.

- nowy kod (funkcje etc.) powinien być docelowo updejtowany do folderu /Docker i prawidłowo funkcjonować w środowisku dockerowym

Po odpaleniu apki komenda
```
sudo docker exec -it rzepak bash
```
odpala terminal bashowy w którym można sobie odpalić co dusza zapragnie.

Do apki został dodany pseudo cache, ale jest za duży na wrzucenie na gita, jeśli chcemy cache to pobieramy folder:

- [cache_data](https://drive.google.com/drive/folders/1NGIl9nzcuq5v7NMqpAONEwTcmPLIckpY?usp=sharing)

umieszczamy go w folderze Docker (jak ktoś nie zrobi sobie też powinno działać).
