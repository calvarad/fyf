

import sys
sys.path.append("../")

from src import Estrategia, generate_df_valores_cuota, agrega_estrategias
import datetime
import os
import pandas as pd
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONDOS = ['A', 'B', 'C', 'D', 'E']

def estrategia_optima(afp, df_dias_habiles, fecha_inicio,
 fecha_termino, monto_inicial):
    '''
    Busca la estrategia óptima de cambio de fondos
    

    Guarda archivo xlsx con fechas de cambio y sugerencia óptima
    '''

    lista_estrategias = [Estrategia(fecha_inicio, fecha_termino,
                     nombre_estrategia = x) for x in FONDOS ]

    df = agrega_estrategias(lista_estrategias, df_dias_habiles, afp,
                           monto_inicial, lag_solicitud=0)

    df['YM'] = df.Fecha.dt.year.astype(str) + df.Fecha.dt.month.astype(str)
    df_fechas_min = df.groupby('YM').min()[['Fecha']]
    df_fechas_max = df.groupby('YM').max()[['Fecha']]

    df_start = df.merge(df_fechas_min, on='Fecha', how='inner')
    df_end = df.merge(df_fechas_max, on='Fecha', how='inner')

    df_mes = df_start.merge(df_end, on='YM', how='inner')

    for fondo in FONDOS:
        df_mes['rent_{}'.format(fondo)] = df_mes['V_{}_{}_lag_0_y'.format(afp, fondo)] / df_mes['V_{}_{}_lag_0_x'.format(afp, fondo)] - 1

    data = []
    for i, row in df_mes.iterrows():
        
        #asume cambios el último dia del mes (conociendo la rentabilidad de los fondos del mes que viene)
        fecha_solicitud = (row['Fecha_x'] - datetime.timedelta(days=1)).date()
        fecha_termino = (row['Fecha_y']).date()
        sugerencia = parse_sugerencia(row)

        data.append((fecha_solicitud, fecha_termino, sugerencia))

    df_optimo = pd.DataFrame.from_records(data, columns = ['Fecha inicio', 'Fecha término', 'Sugerencia'])

    return df_optimo


def parse_sugerencia(row):

    lista_rentabilidades = list(row[['rent_A', 'rent_B', 'rent_C', 'rent_D', 'rent_E']])
    pos = lista_rentabilidades.index(max(lista_rentabilidades))

    sugerencia_str = '100% {}'.format(FONDOS[pos])

    return sugerencia_str


if __name__ == '__main__':
    #Load df_dias_habiles
    #Cargar base de días hábiles
    dbpath = ROOT + r'/processed_data/db_habiles.db'
    conn_habiles = sqlite3.connect(dbpath)
    df_dias_habiles = pd.read_sql('SELECT * FROM HABILES',
                              conn_habiles, parse_dates=['Fecha'])


    fecha_ini = datetime.datetime.strptime('2010-01-01', '%Y-%m-%d').date()
    fecha_end = datetime.datetime.strptime('2020-12-13', '%Y-%m-%d').date()
    monto_inicial = 100

    for afp in ['HABITAT', 'CUPRUM', 'CAPITAL', 'PLANVITAL']:

        df = estrategia_optima(afp, df_dias_habiles,
         fecha_ini, fecha_end, monto_inicial)
        
        df.to_excel(ROOT+r'/processed_data/optima_{}.xlsx'.format(afp))
