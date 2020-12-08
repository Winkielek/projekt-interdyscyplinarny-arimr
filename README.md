# Projekt interdyscyplinarny kryptonim "rzepak"

- CREODIAS_client: skrypty od QED
- /data: folder z danymi (zdjęciami) wyciętych działek do zbioru uczącego
- building_dataset.py: funkcja do zbudowania zbioru uczącego lokalnie:
    
    - działa powielając zdjęcia z folderu /data
    - tworzy folder /dataset z podfolderami /train /valid, czyli struktura przyjmowana przez model
    - sampling podziału train/valid reprodukowalny z użyciem random_state
    - [issue](https://github.com/Winkielek/projekt_interdyscyplinarny_arimr/issues/3#issue-759278752) reprodukowalność powielania zdjęć
    
 
