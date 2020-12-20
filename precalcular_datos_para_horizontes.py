# Pre-calculate data for different time horizons
#+ Output: pickle de un diccionario con keys[afp][años_de_horizonte]
# + de 1 a 6 años(inclusive) de años de horizonte
# + todas las afp con lag 0
# + fyf con lag 0 a 4 (y una para cada afp)
# + fyf inversa con lag 0 a 4 (y una para cada afp)

from src import (Estrategia, agrega_estrategias,
                 generate_returns_for_different_starting_dates,
                 )
import sqlite3
import pickle
import pandas as pd

#Cargar base de días hábiles
conn_habiles = sqlite3.connect(r'processed_data/db_habiles.db')
df_dias_habiles = pd.read_sql('SELECT * FROM HABILES',
                              conn_habiles, parse_dates=['Fecha'])

# PARAMETROS PARA DEFINIR LA ESTRATEGIA
#fecha_ini = datetime.datetime.strptime('2014-01-01', '%Y-%m-%d').date()
fecha_ini = pd.to_datetime('2014-01-01').date()
fecha_end = pd.to_datetime('2020-12-08').date()
monto_inicial = 100

estrategia_a = Estrategia(fecha_ini, fecha_end, 'A')
estrategia_c = Estrategia(fecha_ini, fecha_end, 'C')
estrategia_e = Estrategia(fecha_ini, fecha_end, 'E')
estrategia_ff = Estrategia(fecha_ini, fecha_end, 'FF',
                           'raw_data/anuncios_ff.xlsx')
estrategia_ff_inv = Estrategia(fecha_ini, fecha_end, 'FF_INV',
                               'raw_data/anuncios_ff_inversa.xlsx')

#No incluyo UNO por problemas de datos
lista_afps = ['CAPITAL', 'CUPRUM', 'HABITAT', 'PLANVITAL', 'PROVIDA', 'MODELO']
#'UNO']

# Parámetros
######################3
#Una sola estrategia (lag = 0) y varias estrategias
# fyf e inversa fyf para considerar lags de 0 a 4
lista_estrategias = [estrategia_a, estrategia_c, estrategia_e,
                     estrategia_ff, estrategia_ff, estrategia_ff,
                     estrategia_ff, estrategia_ff,
                     estrategia_ff_inv, estrategia_ff_inv, estrategia_ff_inv,
                     estrategia_ff_inv, estrategia_ff_inv]

lags_f_y_f = [0, 1, 2, 3, 4]
lags = [0, 0, 0] + lags_f_y_f + lags_f_y_f

min_años_horizonte, max_años_horizonte = 1, 6

afp_año_dict = {}

# Generar el diccionario
##############

for afp in lista_afps:
    print(f"Doing afp {afp}")
    df = agrega_estrategias(lista_estrategias, df_dias_habiles,
                            afp, monto_inicial, lag_solicitud=lags)
    beg_period = df.Fecha.min()
    afp_año_dict[afp] = {}
    #Ahora producimos resultados por cada año de horizonte de tiempo
    for año_de_horizonte in range(min_años_horizonte, max_años_horizonte + 1):
        results = generate_returns_for_different_starting_dates(df, año_de_horizonte,
                                                                beg_period)
        afp_año_dict[afp][año_de_horizonte] = results

#Pickle dictionary :D
with open('processed_data/horizonte_de_tiempo_data_dict.pickle', 'wb') as handle:
    pickle.dump(afp_año_dict, handle)
