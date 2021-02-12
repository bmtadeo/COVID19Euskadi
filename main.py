# -*- coding: utf-8 -*-
from __future__ import division
import requests
import telebot
import json
import datetime
import numpy as np
import matplotlib.pyplot as plt
from emoji import emojize

token = 'TOKEN'
bot = telebot.TeleBot(token)

urlIncidenciaEuskadi = 'https://www.geo.euskadi.eus/geoeuskadi/rest/services/COVID19/COVID19_v2/MapServer/2/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&resultOffset=0&resultRecordCount=1000'
urlIncidenciaProvincias = 'https://www.geo.euskadi.eus/geoeuskadi/rest/services/COVID19/COVID19_v2/MapServer/6/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=POSITIBOAK_POSITIVOS%20desc&resultOffset=0&resultRecordCount=300'
urlPositivosCiudades = 'https://www.geo.euskadi.eus/geoeuskadi/rest/services/COVID19/COVID19_v2/MapServer/4/query?f=json&where=NUEVOS_POS%20%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=NUEVOS_POS%20desc&outSR=102100&resultOffset=0&resultRecordCount=300'
urlDatosDiariosGeneral = 'https://www.geo.euskadi.eus/geoeuskadi/rest/services/COVID19/COVID19_v2/MapServer/1/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outSR=102100&resultOffset=0&resultRecordCount=50'
urlOtrosDatos = 'https://opendata.euskadi.eus/contenidos/ds_informes_estudios/covid_19_2020/opendata/generated/covid19-epidemic-status.json'

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Hola bienvendio al bot. Los datos solo se actualizan entre semana\n")
    tiempo = datetime.datetime.now()
    print('INFO ' + str(tiempo)+': Mensaje /start enviado correctamente.')

@bot.message_handler(commands=['help'])
def comandos(message):
    # Preparamos el texto que queremos enviar
    bot_msg = "*Comandos disponibles:*\n" \
              "- /start: Explica para que funciona el bot\n" \
              "- /help: Muestra los comandos disponibles\n" \
              "- /grafica: Gráfica evolutiva de los datos de Euskadi\n" \
              "- /datoseuskadi: Muestra los datos de Euskadi\n" \
              "- /datosprovincias: Muestra los datos de Euskadi\n" \
              "- /datosmunicipio: Muestra los datos de un municipio de Euskadi. Ej: /datosmunicipios Bilbao, /datosmunicipios Vitoria-Gasteiz\n" \
              "- /datoscapitales: Muestra los datos de las capitales de provincia\n"
    chat_id = message.chat.id
    tiempo = datetime.datetime.now()
    bot.send_message(chat_id, bot_msg,parse_mode= 'Markdown')
    print('INFO ' + str(tiempo) +': Mensaje /help enviado correctamente.')

@bot.message_handler(commands=['datoseuskadi'])
def datoseuskadi(message):
    #1. Responses
    responseIncidenciaEuskadi = requests.get(urlIncidenciaEuskadi)
    responseOtrosDatos = requests.get(urlOtrosDatos)
    responseDatosDiariosGeneral = requests.get(urlDatosDiariosGeneral)
    # 2. JSON convert
    JSONIncidenciaEuskadi = json.loads(responseIncidenciaEuskadi.content)
    JSONDatosDiariosGeneral = json.loads(responseDatosDiariosGeneral.content)
    JSONOtrosDatos = json.loads(responseOtrosDatos.content)
    # 3. Obtener datos del JSON y manejarlos
    datosDiarios = JSONDatosDiariosGeneral["features"][-1]["attributes"]
    datosIncidenciaEuskadi = JSONIncidenciaEuskadi["features"][-1]["attributes"]
    todosDatos = JSONOtrosDatos["byDate"]
    testTotales = JSONOtrosDatos["byDate"][-1]["pcrTestCount"] - JSONOtrosDatos["byDate"][-2]["pcrTestCount"]
    positivos = datosIncidenciaEuskadi["KASUAK_CASOS"]
    tasaPositividad = float(positivos / testTotales * 100)

    if datosIncidenciaEuskadi["TASA14DIAS"]> 500:
        mensajeEusk = str(round(datosIncidenciaEuskadi["TASA14DIAS"],2)) + emojize(":red_circle:")
    elif datosIncidenciaEuskadi["TASA14DIAS"] < 500:
        mensajeEusk = str(round(datosIncidenciaEuskadi["TASA14DIAS"],2))

    #4. Crear mensaje
    bot_msg = "*Datos COVID-19 Euskadi: " + str(datosDiarios["DATA___FECHA"]) +"*\n" \
                "Test totales: "+ emojize(":test_tube:")+": " + str(testTotales) +" \n" \
                "Positivos " + emojize(":plus:") + ": "+ str(datosIncidenciaEuskadi["KASUAK_CASOS"]) + " \n" \
                "Tasa positividad: " + str(round(tasaPositividad,2)) +'%' + "\n" \
                "Planta " + emojize(":hospital:")+": " + str(todosDatos[-1]["hospitalAdmissionsWithPCRCount"]) +" (Nuevos: " + str(todosDatos[-1]["hospitalAdmissionsWithPCRCount"]-todosDatos[-2]["hospitalAdmissionsWithPCRCount"]) +")\n" \
                "UCI " + emojize(":police_car_light:") + ": "+str(todosDatos[-1]["icuPeopleCount"]) + " (Nuevos: " + str(todosDatos[-1]["icuPeopleCount"]-todosDatos[-2]["icuPeopleCount"]) +")\n"\
                "IA14 Euskadi: " + mensajeEusk+" \n" \
                "Rt" + emojize(":microbe:") +": " + str(todosDatos[-1]["r0"]) + "\n"
    chat_id = message.chat.id
    bot.send_message(chat_id, bot_msg,parse_mode= 'Markdown')
    tiempo = datetime.datetime.now()
    print('INFO ' + str(tiempo) + ': Mensaje /datoseuskadi enviado correctamente.')

@bot.message_handler(commands=['datosprovincias'])
def datosprovincias(message):
    # 1. Responses
    responsePositivosCiudades = requests.get(urlPositivosCiudades)
    responseDatosDiariosGeneral = requests.get(urlDatosDiariosGeneral)
    # 2. JSON convert
    JSONPositivosCiudades = json.loads(responsePositivosCiudades.content)
    JSONDatosDiariosGeneral = json.loads(responseDatosDiariosGeneral.content)
    # 3. Obtener datos del JSON y manejarlos
    calculoPositivosProvincias = JSONPositivosCiudades["features"]
    datosDiarios = JSONDatosDiariosGeneral["features"][-1]["attributes"]
    contBizkaia = 0
    contGip = 0
    contArab = 0
    ia = 0
    for i in calculoPositivosProvincias:
        if i["attributes"]["TERRITORIO"] == "BIZKAIA":
            contBizkaia = contBizkaia + i["attributes"]["NUEVOS_POS"]
        elif i["attributes"]["TERRITORIO"] != "BIZKAIA" and i["attributes"]["TERRITORIO"] != "GIPUZKOA":
            contArab = contArab + i["attributes"]["NUEVOS_POS"]
        elif i["attributes"]["TERRITORIO"] == "GIPUZKOA":
            contGip = contGip + i["attributes"]["NUEVOS_POS"]
    # 4. Crear mensaje
    bot_msg = "*Datos COVID-19 Provincias: " + str(datosDiarios["DATA___FECHA"])+ "*\n" \
               ""+emojize(":plus:") + " Nuevos positivos Bizkaia: " + str(contBizkaia) + "\n"\
               ""+emojize(":plus:") + " Nuevos positivos Gipuzkoa: " + str(contGip) + "\n"\
               ""+emojize(":plus:") + " Nuevos positivos Araba: " + str(contArab) + "\n"
    chat_id = message.chat.id
    bot.send_message(chat_id, bot_msg,parse_mode= 'Markdown')
    tiempo = datetime.datetime.now()
    print('INFO ' + str(tiempo) + ': Mensaje /datosprovincias enviado correctamente.')


@bot.message_handler(commands=['datoscapitales'])
def datoscapitales(message):
    # 1. Responses
    responseIncidenciaProvincias = requests.get(urlIncidenciaProvincias)
    responsePositivosCiudades = requests.get(urlPositivosCiudades)
    responseDatosDiariosGeneral = requests.get(urlDatosDiariosGeneral)
    # 2. JSON convert
    JSONIncidenciaProvincias = json.loads(responseIncidenciaProvincias.content)
    JSONPositivosCiudades = json.loads(responsePositivosCiudades.content)
    JSONDatosDiariosGeneral = json.loads(responseDatosDiariosGeneral.content)
    # 3. Obtener datos del JSON y manejarlos
    datosIncidenciaBilbo = JSONIncidenciaProvincias["features"][0]["attributes"]
    datosIncidenciaGasteiz = JSONIncidenciaProvincias["features"][1]["attributes"]
    datosIncidenciaDonostia = JSONIncidenciaProvincias["features"][2]["attributes"]
    datosPositivosBilbo = JSONPositivosCiudades["features"][0]["attributes"]
    datosPositivosGasteiz = JSONPositivosCiudades["features"][1]["attributes"]
    datosPositivosDonostia = JSONPositivosCiudades["features"][2]["attributes"]
    datosDiarios = JSONDatosDiariosGeneral["features"][-1]["attributes"]
    # Bilbo
    if datosIncidenciaBilbo["TASA_100_000_BIZTANLEKO_TASA_P"] > 500:
        mensaje1 = str(round(datosIncidenciaBilbo["TASA_100_000_BIZTANLEKO_TASA_P"],2)) + emojize(":red_circle:")
    elif datosIncidenciaBilbo["TASA_100_000_BIZTANLEKO_TASA_P"] < 500:
        mensaje1 = str(round(datosIncidenciaBilbo["TASA_100_000_BIZTANLEKO_TASA_P"], 2))
        #Donos
    if datosIncidenciaDonostia["TASA_100_000_BIZTANLEKO_TASA_P"] > 500:
        mensaje2 = str(round(datosIncidenciaDonostia["TASA_100_000_BIZTANLEKO_TASA_P"], 2)) + emojize(":red_circle:")
    elif datosIncidenciaDonostia["TASA_100_000_BIZTANLEKO_TASA_P"] < 500:
        mensaje2 = str(round(datosIncidenciaDonostia["TASA_100_000_BIZTANLEKO_TASA_P"], 2))
        #Gasteiz
    if datosIncidenciaGasteiz["TASA_100_000_BIZTANLEKO_TASA_P"] > 500:
        mensaje3 = str(round(datosIncidenciaGasteiz["TASA_100_000_BIZTANLEKO_TASA_P"], 2)) + emojize(":red_circle:")
    if datosIncidenciaGasteiz["TASA_100_000_BIZTANLEKO_TASA_P"] < 500:
        mensaje3 = str(round(datosIncidenciaGasteiz["TASA_100_000_BIZTANLEKO_TASA_P"], 2))
    #4. Crear mensaje
    bot_msg = "*Datos COVID-19 Provincias: " + str(datosDiarios["DATA___FECHA"]) + "*\n" \
          ""+emojize(":plus:") + "Nuevos positivos Bilbo: " + str(datosPositivosBilbo["NUEVOS_POS"]) + "\n" \
          "IA Bilbo: " + mensaje1 + "\n" \
          ""+emojize(":plus:") + "Nuevos positivos Donostia: " + str(datosPositivosDonostia["NUEVOS_POS"]) + "\n" \
          "IA Donostia: " + mensaje2 + "\n" \
          ""+emojize(":plus:") + "Nuevos positivos Gasteiz: " + str(datosPositivosGasteiz["NUEVOS_POS"]) + "\n" \
           "IA Gasteiz: " + mensaje3 + "\n"


    chat_id = message.chat.id
    bot.send_message(chat_id, bot_msg,parse_mode= 'Markdown')
    tiempo = datetime.datetime.now()
    print('INFO ' + str(tiempo) + ': Mensaje /datoscapitales enviado correctamente.')

@bot.message_handler(commands=['grafica'])
def grafica(message):
    # 1. Responses
    responseIncidenciaEuskadi = requests.get(urlIncidenciaEuskadi)
    # 2. JSON convert
    JSONIncidenciaEuskadi = json.loads(responseIncidenciaEuskadi.content)
    # 3. Obtener datos del JSON y manejarlos
    i=0
    casos = []
    fechas = []
    for i in JSONIncidenciaEuskadi["features"]:
        casos.append(i["attributes"]["KASUAK_CASOS"])
        fechas.append(i["attributes"]["DATA_FECHA"])
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(casos, color='tab:blue')
    ax.set_title('Casos por día')
    ax.set_ylabel('Casos')
    ax.set_xlabel('Dias')
    plt.savefig('grafica.png')
    chat_id = message.chat.id
    photo = open('grafica.png', 'rb')
    tiempo = datetime.datetime.now()
    bot.send_photo(chat_id, photo)
    print('INFO ' + str(tiempo) + ': Mensaje /grafica enviado correctamente.')

@bot.message_handler(commands=['datosmunicipio'])
def datosmunicipio(message):
    # 1. Extraer el municipio del comando
    municipio = extract_arg(message.text)
    if municipio != []:
        responsePositivosCiudades = requests.get(urlPositivosCiudades)
        JSONPositivosCiudades = json.loads(responsePositivosCiudades.content)
        i =0
        for i in JSONPositivosCiudades["features"]:
            if i["attributes"]["UDALERRIA___MUNICIPIO"] == municipio[0]:
                print(i["attributes"]["UDALERRIA___MUNICIPIO"])
                casos = i["attributes"]["NUEVOS_POS"]

        # 4. Crear mensaje
        bot_msg = "*Nuevos positvos COVID-19 en: " + municipio[0] + "*\n" \
             "" + emojize(":plus:") + " " + str(casos) + "\n"
        chat_id = message.chat.id
        bot.send_message(chat_id, bot_msg, parse_mode='Markdown')
        tiempo = datetime.datetime.now()
        print('INFO ' + str(tiempo) + ': Mensaje /datosmunicipio enviado correctamente.')
    else:
        bot_msg = "*Por favor, inserta un municipio*"
        chat_id = message.chat.id
        bot.send_message(chat_id, bot_msg, parse_mode='Markdown')
        tiempo = datetime.datetime.now()
        print('WARN ' + str(tiempo) + ': Mensaje /datosmunicipio enviado sin municipio.')
def extract_arg(arg):
    return arg.split()[1:]

bot.polling()



