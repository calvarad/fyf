import datetime
import pandas as pd
import sys

sys.path.append(r'../2_avisos_cambio_fondos')
sys.path.append(r'../3_simulador')

from estrategias import Estrategia
from valores_cuota import df_valores_cuota

def agrega_estrategias(lista_estrategias, afp, monto_inicial, lag_solicitud):
    '''
    Toma varias estrategias y crea un DataFrame con todas ellas consolidadas
    '''
    aux = []
    first = True
    if type(lag_solicitud) != list:
        lag_solicitud = [lag_solicitud]*len(lista_estrategias)

    for i, est in enumerate(lista_estrategias):
        df = df_valores_cuota(est, afp, monto_inicial, lag_solicitud[i], lag_venta=2, lag_compra=2)
        col = [c for c in df.columns if 'Val' in c]

        df = df[['Fecha'] + col]

        if first:
            df_out = df
            first = False
        else:
            df_out = df_out.merge(df, on=['Fecha'], how='outer')

    #arreglo los valores por si hay missings
    df_out.sort_values('Fecha', inplace=True)
    df_out.set_index('Fecha', inplace=True)
    df_out.fillna(method='ffill', inplace=True)
    df_out.reset_index(inplace=True)

    return df_out