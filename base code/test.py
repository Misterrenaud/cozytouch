import os
import shelve
import time

import requests

url_cozytouchlog=u'https://ha110-1.overkiz.com/enduser-mobile-web/enduserAPI'
url_cozytouch=u'https://ha110-1.overkiz.com/enduser-mobile-web/externalAPI/json/'
url_atlantic=u'https://apis.groupe-atlantic.com'
current_path=os.path.dirname(os.path.abspath(__file__)) # repertoire actuel
cozytouch_save = current_path+'/cozytouch_save'

def var_save(var, var_str):
    """Fonction de sauvegarde
    var: valeur à sauvegarder, var_str: nom objet en mémoire
    """
    d = shelve.open(cozytouch_save)
    if var_str in d :
        d[var_str] = var

    else :
        d[var_str] = 0 # init variable
        d[var_str] = var
        d.close()

def var_restore(var_str,format_str =False ):
    '''Fonction de restauration
    var_str: nom objet en mémoire
    '''
    d = shelve.open(cozytouch_save)
    if not (var_str) in d :
        if  format_str:
            value = 'init' # init variable
        else :
            value = 0 # init variable
    else :
        value = d[var_str]
    d.close()
    return value

def cozytouch_login(login,password):


    headers={
    'Content-Type':'application/x-www-form-urlencoded',
    'Authorization':'Basic Q3RfMUpWeVRtSUxYOEllZkE3YVVOQmpGblpVYToyRWNORHpfZHkzNDJVSnFvMlo3cFNKTnZVdjBh'
        }
    data={
        'grant_type':'password',
        'username':'GA-PRIVATEPERSON/' + login,
        'password':password
        }

    url=url_atlantic+'/token'
    req = requests.post(url,data=data,headers=headers)

    atlantic_token=req.json()['access_token']

    headers={
    'Authorization':'Bearer '+atlantic_token+''
        }
    reqjwt=requests.get(url_atlantic+'/magellan/accounts/jwt',headers=headers)

    jwt=reqjwt.content.decode().replace('"','')
    data={
        'jwt':jwt
        }
    jsession=requests.post(url_cozytouchlog+'/login',data=data)

    print(' POST-> '+url_cozytouchlog+"/login | userId=****&userPassword=**** : "+str(jsession.status_code))

    if jsession.status_code==200 : # Réponse HTTP 200 : OK
        print("Authentification serveur cozytouch OK")
        cookies =dict(JSESSIONID=(jsession.cookies['JSESSIONID'])) # Récupération cookie ID de session
        var_save(cookies,'cookies') #Sauvegarde cookie
        return True

    print("!!!! Echec authentification serveur cozytouch")
    print(req.status_code,req.reason)
    return False

def cozytouch_GET(json):
    ''' Fonction d'interrogation HTTP GET avec l'url par défaut
    json: nom de fonction JSON à transmettre au serveur
    '''
    headers = {
    'cache-control': "no-cache",
    'Host' : "ha110-1.overkiz.com",
    'Connection':"Keep-Alive",
    }
    myurl=url_cozytouch+json
    cookies=var_restore('cookies')
    req = requests.get(myurl,headers=headers,cookies=cookies)
    print(u'  '.join((u'GET-> ',myurl,' : ',str(req.status_code))).encode('utf-8'))

    if req.status_code==200 : # Réponse HTTP 200 : OK
            data=req.json()
            return data

    print(req.status_code,req.reason) # Appel fonction sur erreur HTTP
    time.sleep(1) # Tempo entre requetes
    return None

def cozytouch_POST(url_device,name,parametre):
    # Fonction d'envoi requete POST vers serveur cozytouch

    # conversion entier ou flottant => unicode
    if isinstance (parametre,int) or isinstance (parametre,float):
        parametre = str(parametre).decode("utf-8")
    # si unicode, on teste si c'est un objet JSON '{}' dans ce cas on ne met pas de double quotes, sinon on applique par défaut
    elif isinstance (parametre,str) or isinstance (parametre,bytes)  and parametre.find('{') == -1 :
        parametre = f'"{parametre}"'

    # Headers HTTP
    headers= {
    'content-type': "application/json",
    'cache-control': "no-cache"
    }
    myurl=url_cozytouch+u'../../enduserAPI/exec/apply'
    payload =u'{\"actions\": [{ \"deviceURL\": \"'+url_device+u'\" ,\n\"commands\": [{ \"name\": \"'+name+u'\",\n\"parameters\":['+parametre+u']}]}]}'
    cookies=var_restore('cookies')
    req = requests.post(myurl, data=payload, headers=headers,cookies=cookies)
    print(' POST-> '+myurl+" | "+payload+" : "+str(req.status_code))

    if req.status_code!=200 : # Réponse HTTP 200 : OK
        print(req.status_code,req.reason)
    return req.status_code

def decouverte_devices():

    ''' Fonction de découverte des devices Cozytouch
    Scanne les devices présents dans l'api cozytouch et gère les ajouts à Domoticz
    '''
    print("**** Decouverte devices ****")

    # Renvoi toutes les données du cozytouch
    data = cozytouch_GET('getSetup')

    if debug==2:
	    f1=open('./dump_cozytouch.txt', 'w+')
	    f1.write((json.dumps(data, indent=4, separators=(',', ': '))))
	    f1.close()


    # Lecture données Gateway Cozytouch (pour info)
    select=(data[u'setup'][u'gateways'][0])
    if select[u'alive']:
        cozytouch_gateway_etat="on"
    else:
        cozytouch_gateway_etat="off"
    if debug:
        print("\nGateway Cozytouch : etat "+cozytouch_gateway_etat+" / connexion : "+select[u'connectivity'][u'status']+" / version : "+str(select[u'connectivity'][u'protocolVersion']))

    # Restauration de la liste des devices
    save_devices = var_restore('save_devices')
    # Restauration de l'idx hardware cozytouch dans domoticz
    save_idx = var_restore('save_idx')

    '''
    Cas de la liste vide, au premier démarrage du script par ex.
    On passe en revue les devices de l'API Cozytouch et on l'ajoute à une liste
    si sa classe est connu dans le dictionnaire Cozytouch
    '''
    if not save_devices : # si la liste est vide on passe à la création des devices
        print("**** Demarrage procedure d'ajout devices Cozytouch **** ")
        liste=[]    # on crée une liste vide
        domoticz_write_log(u'Cozytouch : Recherche des devices connectes ... ')
        # Initialisation variables
        x = 0
        p = 0
        oid = 0

        # On boucle sur chaque device trouvé :
        for a in data[u'setup'][u'devices']:
            url = a[u'deviceURL']
            name = a[u'controllableName']
            oid = a[u'placeOID']

            if name == dict_cozytouch_devtypes.get(u'radiateur'): # on vérifie si le nom du device est connu
               label = read_label_from_cozytouch(data,x,oid)
               liste= ajout_radiateur(save_idx,liste,url,x,label)   # ajout du device à la liste
               p+=1 # incrément position dans dictionnaire des devices

            elif name == dict_cozytouch_devtypes.get(u'chauffe eau'):
                liste = ajout_chauffe_eau (save_idx,liste,url,x,(data[u'setup'][u'rootPlace'][u'label'])) # label rootplace
                p+=1

            elif name == dict_cozytouch_devtypes.get(u'module fil pilote'):
                liste= ajout_module_fil_pilote (save_idx,liste,url,x,read_label_from_cozytouch(data,x,oid))
                p+=1

            elif name == dict_cozytouch_devtypes.get(u'PAC main control'):
                liste= ajout_PAC_main_control (save_idx,liste,url,x,read_label_from_cozytouch(data,x))
                p+=1

            elif name == dict_cozytouch_devtypes.get(u'PAC zone control'):
                liste= ajout_PAC_zone_control (save_idx,liste,url,x,read_label_from_cozytouch(data,x))
                p+=1

            elif name == dict_cozytouch_devtypes.get(u'DHWP_THERM_V3_IO') or name == dict_cozytouch_devtypes.get(u'DHWP_THERM_IO') or name == dict_cozytouch_devtypes.get(u'DHWP_THERM_V2_MURAL_IO') or name == dict_cozytouch_devtypes.get(u'DHWP_THERM_V4_CETHI_IO'):
                liste= Add_DHWP_THERM (save_idx,liste,url,x,(data[u'setup'][u'rootPlace'][u'label']),name) # label sur rootplace
                p+=1

            elif name == dict_cozytouch_devtypes.get(u'bridge cozytouch'):
                label = u'localisation inconnue'
                liste= ajout_bridge_cozytouch (save_idx,liste,url,x,label)
                p+=1

            elif name == dict_cozytouch_devtypes.get(u'PAC_HeatPump'):
                liste= ajout_PAC_HeatPump (save_idx,liste,url,x,read_label_from_cozytouch(data,x))
                p+=1

            elif name == dict_cozytouch_devtypes.get(u'PAC OutsideTemp'):
                liste= ajout_PAC_Outside_Temp (save_idx,liste,url,x,read_label_from_cozytouch(data,x))
                p+=1

            elif name == dict_cozytouch_devtypes.get(u'PAC InsideTemp'):
                liste= ajout_PAC_Inside_Temp (save_idx,liste,url,x,read_label_from_cozytouch(data,x))
                p+=1

            elif name == dict_cozytouch_devtypes.get(u'PAC Electrical Energy Consumption'):
                liste= ajout_PAC_Electrical_Energy (save_idx,liste,url,x,read_label_from_cozytouch(data,x))
                p+=1

            elif name == dict_cozytouch_devtypes.get(u'PAC zone component'):
                liste= ajout_PAC_zone_component (save_idx,liste,url,x,read_label_from_cozytouch(data,x))
                p+=1

            else :
                domoticz_write_log(u'Cozytouch : Device avec classe '+name+u' inconnu')


            x+=1 # incrément device dans data json cozytouch

        # Fin de la boucle :
        # Sauvegarde des devices ajoutés
        var_save(liste,'save_devices')

    '''
    Cas de liste non vide
    On passe en revue les devices l'API Cozytouch
    si sa classe est connue dans le dictionnaire Cozytouch on met à jour les données
    '''
    if save_devices != 0 : # si la liste contient des devices
        print("\n**** Demarrage mise a jour devices ****")
        # Initialisation variables
        liste_inconnu = []
        x = 0
        p = 0
        # On boucle sur chaque device trouvé :
        for a in data[u'setup'][u'devices']:
            url = a[u'deviceURL']
            name = a[u'controllableName']

            # On boucle sur les éléments du dictionnaire de devices
            for element in save_devices :
                if element.has_key(u'url') : # si la clé url est présente dans le dictionnaire
                    if element.get(u'url') == url :  # si l'url du device est stocké dans le dictionnaire
                        maj_device(data,name,p,x) # mise à jour du device
                        p+=1 # incrément position dans le dictionnaire

                        for inconnu in liste_inconnu :
                            if inconnu == url :
                                liste_inconnu.remove(url) # on retire l'url inconnu à la liste
                        break

                    else : # sinon on reboucle
                        liste_inconnu.append(url)

                else : # sinon on reboucle
                    continue

            x+=1 # incrément position du device dans les datas json cozytouch



if __name__ == "__main__":
    cozytouch_login("victoria.tonarelli@gmail.com", "Gris2vert!")
    decouverte_devices()