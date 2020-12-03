import datetime
import pandas as pd
import sys

sys.path.append(r'../2_avisos_cambio_fondos')
sys.path.append(r'../3_simulador')
sys.path.append(r'../4_comparador_estrategias')

from estrategias import Estrategia
from valores_cuota import df_valores_cuota
from comparador import agrega_estrategias

FONDOS = ['A', 'B', 'C', 'D', 'E']

def estrategia_optima(afp, fecha_inicio, fecha_termino, monto_inicial):
    '''
    Busca la estrategia óptima de cambio de fondos
    

    Guarda archivo xlsx con fechas de cambio y sugerencia óptima
    '''

    lista_estrategias = [Estrategia(fecha_inicio, fecha_termino, nombre_estrategia = x) for x in FONDOS ]

    df = agrega_estrategias(lista_estrategias, afp, monto_inicial, lag_solicitud=0)

    df['YM'] = df.Fecha.dt.year.astype(str) + df.Fecha.dt.month.astype(str)
    df_fechas_min = df.groupby('YM').min()[['Fecha']]
    df_fechas_max = df.groupby('YM').max()[['Fecha']]

    df_start = df.merge(df_fechas_min, on='Fecha', how='inner')
    df_end = df.merge(df_fechas_max, on='Fecha', how='inner')

    df_mes = df_start.merge(df_end, on='YM', how='inner')

    for fondo in FONDOS:
        df_mes['rent_{}'.format(fondo)] = df_mes['Val_{}_lag_0_y'.format(fondo)] / df_mes['Val_{}_lag_0_x'.format(fondo)] - 1

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

    fecha_ini = datetime.datetime.strptime('2010-01-01', '%Y-%m-%d').date()
    fecha_end = datetime.datetime.strptime('2020-11-23', '%Y-%m-%d').date()
    monto_inicial = 100

    for afp in ['HABITAT', 'CUPRUM', 'CAPITAL', 'PLANVITAL']:

        df = estrategia_optima(afp, fecha_ini, fecha_end, monto_inicial)
        
        df.to_excel('../2_avisos_cambio_fondos/optima_{}.xlsx'.format(afp))