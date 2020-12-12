import requests

# A BTW WOLNE STRASZNIE DA SIĘ TO JAKOŚ PRZYŚPIESZYĆ UŻYWJAĆ SESIJ ALE TO TODO 


def cord_reader(plot_ids_list):
    
    # Taking list contaings plots ID as strings 
    # example ["260101_5.0037.569"]
    
    # Return dictionary with plots ID as key and 
    # cords of plot as value 
    
    #data check 
   
    if( not isinstance(plot_ids_list,list)): 
        raise Exception("List object is required")
    if( not isinstance(plot_ids_list[0],str)):
        raise Exception("List didnt contains only strings")
        
    list_of_cords= ["empty"]*len(plot_ids_list)
    iterator = 0
    s = requests.Session()
    for i in plot_ids_list:
        # ganerated with https://curl.trillworks.com/ 
     
                    



        cookies = {
        '_ga': 'GA1.2.1313350324.1604560244',
        'PHPSESSID': '7s2fvrerdfo4bec0sdn40lpah7',
        '_gid': 'GA1.2.1787115803.1607782926',
        '_gat_gtag_UA_122392520_1': '1',
            }

        headers = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'Content-type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Origin': 'https://polska.e-mapa.net',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://polska.e-mapa.net/',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            }

        data = {
        'action': 'wsporzedne_granic',
        'id_dzialki': i,
        'srid': '2180'
        }






        response = s.post('https://polska.e-mapa.net/application/modules/dzus/dzus.php', headers=headers, cookies=cookies, data=data)

        out  = response.text
        # OUT in form of string 
        # Spliting and extracting cords 
        out = out.split("'")
        out = out[1:len(out)-1]
        final =[]
        for i in out:
            
            if(i>"-"):
                final.append(i)
        
        list_of_cords[iterator] = final
        iterator = iterator +1
        
        
    
    res = dict(zip(plot_ids_list, list_of_cords))
        
    return res