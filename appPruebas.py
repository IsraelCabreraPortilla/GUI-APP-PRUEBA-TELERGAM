from flask import Flask, render_template, request,flash
import pandas as pd
import requests
from urllib.request import urlopen
import os
from datetime import datetime
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import time

UPLOAD_FOLDER = "./static"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# TOKEN Quant Intern 1
token1 = "5363622455:AAEoFyCSHrhOZhQzxSGD6MxOWKw9h9aoQqY"

ids = []
array = []
lista_enviados = np.array([])
ids = np.array([])
lista_con_info = []
cont = 1

# function for sending just a message
def envio_msj(id_chat, msg):
    global lista_enviados,ids,lista_con_info,cont
    r = requests.post(f'https://api.telegram.org/bot{token1}/sendMessage',
                      data={'chat_id': id_chat, 'text': msg})
    if(r.json()['ok']):
        lista_enviados = np.append(lista_enviados, r.json()['result']['chat']['title'])
        ids = np.append(ids, r.json()['result']['chat']['id'])
        lista_con_info.append(f"\nSe mandó a {str(lista_enviados[-1])}, ya van {str(cont)}.")
        cont += 1
        #print(lista_enviados)
        
 


# function for sending an image
def envio_msjIMG(id_chat, msg, imagen):
    r = requests.post(f'https://api.telegram.org/bot{token1}/sendPhoto',
                      files={'photo': (imagen, open(
                          imagen, 'rb'))},
                      data={'chat_id': id_chat, 'caption': msg})
    time.sleep(0.001)
   

@app.route('/', methods=["get", "post"])
def upload_file():
    
    # defining the scope of the application
    scope_app =['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'] 

        #credentials to the account
    cred = ServiceAccountCredentials.from_json_keyfile_name('project-osl-chats-telegram-ecd6438b399d.json',scope_app) 
        # authorize the clientsheet 
    client = gspread.authorize(cred)
        # get the sample of the Spreadsheet
        #sheet = client.open('Telegram_Chats')
    sheet_pruebas = client.open('Client_List')

        # get the first sheet of the Spreadsheet
        #sheet_instance = sheet.get_worksheet(0)
    sheet_instancepruebas = sheet_pruebas.get_worksheet(0)
        # get all the records of the data
        #records_oficial = sheet_instance.get_all_records()
    records_pruebas = sheet_instancepruebas.get_all_records()
    data = records_pruebas
    print(len(data))
        
    my_list = []

    if request.method == 'POST':
        
        try:
            cont = 1
            category = request.form.get("category")
            typeofmessage = request.form.get("typeofmessage")
            message = request.form.get("message")
            region = request.form.get("region")
            now = datetime.now()
            fecha_envio = now.date()
            hora_envio = now.time()
            print(category, typeofmessage, message)
            # bd.insertar_MensajeBot(typeofmessage,fecha_envio,hora_envio,message,coin,responser)
            # el mensaje va con IMAGEN
            if request.files['file1']:
                file1 = request.files['file1']
                path = os.path.join(
                    app.config['UPLOAD_FOLDER'], file1.filename)
                file1.save(path)
                nameimg = path
                # preguntemos si el mensaje es dirigido a todos los de la region
                if(region == "All" and category=="All"):
                    for i in range(len(data)):
                        envio_msjIMG(data[i]['ID_Chat'], message, nameimg)
                if(region =="All" and category!="All"):
                    for i in range(len(data)):
                        if(category == data[i]['Category']):
                            envio_msjIMG(data[i]['ID_Chat'],message,nameimg)
                if(region!="All" and category=="All"):
                    for i in range(len(data)):
                        if(region == data[i]['Site']):
                            envio_msjIMG(data[i]['ID_Chat'],message,nameimg)
                if(region!="All" and category!="All"):
                    for i in range(len(data)):
                        if(region == data[i]['Site'] and category == data[i]['Category']):
                            envio_msjIMG(data[i]['ID_Chat'],message,nameimg)
                

            # el mensaje va SIN IMAGEN
            else:
                # es mensaje dirigido a todos
                if(region == "All" and category=="All"):
                    for i in range(len(data)):
                        envio_msj(data[i]['ID_Chat'], message)
                        print(i)
                if(region =="All" and category!="All"):
                    for i in range(len(data)):
                        if(category == data[i]['Category']):
                            envio_msj(data[i]['ID_Chat'],message)
                if(region!="All" and category=="All"):
                    for i in range(len(data)):
                        if(region == data[i]['Site']):
                            envio_msj(data[i]['ID_Chat'],message)
                if(region!="All" and category!="All"):
                    for i in range(len(data)):
                        if(region == data[i]['Site'] and category == data[i]['Category']):
                            envio_msj(data[i]['ID_Chat'],message)
        
            

   

        except Exception as e: 
            lista_con_info.append(e)

    return render_template('index.html', lista_con_info = lista_con_info)

if __name__ == '__main__':
    app.run(debug=True, port=5000)