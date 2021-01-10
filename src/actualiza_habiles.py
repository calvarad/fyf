import datetime
import json 
import requests
import sqlite3
import sys
sys.path.append("../")

from src import daterange

#Cargar base de días hábiles
dbpath = r'../processed_data/db_habiles.db'

conn = sqlite3.connect(dbpath)

def actualiza_indice(conn):
    c = conn.cursor()

    query1 = 'DROP INDEX IF EXISTS ix_fechas'

    c.execute(query1)

    query2 = 'CREATE UNIQUE INDEX ix_fechas ON HABILES(Fecha)'

    c.execute(query2)

    conn.commit()

def get_feriados(fecha_ini, fecha_end):
    
    year_start = fecha_ini.year
    year_end = fecha_end.year
    
    set_out = set()
    for year in range(year_start, year_end+1):
        url_api = 'https://apis.digital.gob.cl/fl/feriados/{}'.format(year)

        response = requests.get(url_api, headers={"User-Agent":"Mozilla/5.0"})

        #with urllib.request.urlopen(url_api) as url:
        #    data = json.loads(url.read().decode())

        data = json.loads(response.text)
        for result in data:
            fecha_feriado = datetime.datetime.strptime(result['fecha'], "%Y-%m-%d").date()
            
            if fecha_ini <= fecha_feriado <= fecha_end:
                set_out.add(fecha_feriado)
    
    return set_out

def save_fecha(fecha, conn):
    data = (fecha, is_habil(fecha))
    
    query = 'REPLACE INTO HABILES(Fecha, Habil) VALUES(?,?);'
    
    c = conn.cursor()
    
    c.execute(query, data)
    
    conn.commit()
    
def is_habil(fecha):
    if fecha in feriados or fecha.weekday() >= 5:
        return 0
    else:
        return 1

if __name__ == '__main__':

    # PARAMETROS PARA BUSCAR DIAS HABILES
    fecha_ini = datetime.datetime.strptime('2020-12-01', '%Y-%m-%d').date()
    fecha_end = datetime.datetime.strptime('2021-01-15', '%Y-%m-%d').date()

    # Paso 0. Actualiza el indice de la base (no es necesario ahora, pero la primera vez si)
    # Este paso es importante si actualizo la base original de dias habiles (reservada)
    actualiza_indice(conn)

    # Paso 1. Busco feriados en la API de Feriados
    # Documentacion: https://apis.digital.gob.cl/fl
    feriados = get_feriados(fecha_ini, fecha_end)

    # Paso 2. Guardo los dias habiles en la base de datos
    for fecha in daterange(fecha_ini, fecha_end):
        save_fecha(fecha, conn)
