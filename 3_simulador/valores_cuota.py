import datetime
import pandas as pd
import sqlite3


dbpath = r'../data_auxiliar/db_habiles.db'
conn_habiles = sqlite3.connect(dbpath)

#lo dejo como global para que cargue solo 1 vez
df_habiles = pd.read_sql('SELECT * FROM HABILES', conn_habiles, parse_dates=['Fecha'])


def df_valores_cuota(estrategia, afp, monto_inicial, lag_solicitud, lag_venta=2, lag_compra=2):

    fecha_ini = estrategia.fecha_ini
    fecha_end = estrategia.fecha_end

    df_valores = get_df_valores(afp, fecha_ini, fecha_end)
    
    valores_ini = get_valores(df_valores, fecha_ini)

    monto_valorizado_ini = monto_inicial
    allocation_ini = estrategia.posiciones[0].porcentajes

    n_cuotas_ini = get_num_cuotas(monto_valorizado_ini, allocation_ini, valores_ini)

    fechas_cambios = {posicion.fecha_inicio : i for i, posicion in enumerate(estrategia.posiciones)}

    #erased

    aux_data = [[fecha_ini, monto_valorizado_ini] + n_cuotas_ini]
    
    dateitera = daterange(fecha_ini + datetime.timedelta(days=1), fecha_end)
    
    for fecha in dateitera:
        #hay cambio de fondo
        if fecha in fechas_cambios:
            fecha_solicitud = fecha + datetime.timedelta(days=lag_solicitud)
            
            
            new_allocation = estrategia.posiciones[fechas_cambios[fecha]].porcentajes

            sell_date = get_posible_date(fecha_solicitud, lag_venta)
            buy_date =  get_posible_date(fecha_solicitud, lag_compra)

            valores_ini = get_valores(df_valores, sell_date)
            valores_end = get_valores(df_valores, buy_date)

            monto_valorizado = get_monto_valorizado(n_cuotas_ini, valores_ini)

            new_cuotas = get_num_cuotas(monto_valorizado, new_allocation, valores_end)

            n_cuotas_ini = new_cuotas
           
            # me muevo hacia adelante para seguir despues de la nueva venta/compra
            # esto asume que no puedo moverme de fondo mientras no se termine de
            # materializar el cambio solicitado
            while fecha < buy_date:
                try:
                    fecha = next(dateitera)
                except:
                    break

        #no hay cambio de fondo
        else:

            valores_actual = get_valores(df_valores, fecha)
            monto_valorizado = get_monto_valorizado(n_cuotas_ini, valores_actual)

        data = [fecha, monto_valorizado] + n_cuotas_ini
        aux_data.append(data)
        
    df = pd.DataFrame.from_records(aux_data, columns = [
        'Fecha', 'Val_{}_lag_{}'.format(estrategia.nombre_estrategia, lag_solicitud), 
        'CP_A', 'CP_B', 'CP_C', 'CP_D', 'CP_E'])
    
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%Y-%m-%d')

    return df


def get_df_valores(afp, fecha_ini, fecha_end):
    path = r'../1_valores_cuota/valores_cuota.db'
    conn = sqlite3.connect(path)

    query = '''
        SELECT DATE(FECHA_DIA) AS Fecha,
            AVG(CASE WHEN TICKER = '{afp}_A' THEN VALOR ELSE NULL END) AS FondoA,
            AVG(CASE WHEN TICKER = '{afp}_B' THEN VALOR ELSE NULL END) AS FondoB,
            AVG(CASE WHEN TICKER = '{afp}_C' THEN VALOR ELSE NULL END) AS FondoC,
            AVG(CASE WHEN TICKER = '{afp}_D' THEN VALOR ELSE NULL END) AS FondoD,
            AVG(CASE WHEN TICKER = '{afp}_E' THEN VALOR ELSE NULL END) AS FondoE
        FROM VALORES_CUOTA
        WHERE VALOR > 1
        GROUP BY DATE(FECHA_DIA)
    '''.format(afp=afp)
    
    df_valores = pd.read_sql(query, conn, parse_dates=['Fecha'])
        
    df_valores.set_index('Fecha', inplace=True)
    
    df_valores.dropna(inplace=True)
    
    sel = (df_valores.FondoA < 1) | (df_valores.FondoB < 1) | (df_valores.FondoC < 1) | (df_valores.FondoD < 1) | (df_valores.FondoE < 1)
    
    df_valores = df_valores[~sel]
    
    return df_valores


def daterange(start_date, end_date):
    'entrega fechas entre start_date y end_date, ambas inclusive'    
    for n in range(int ((end_date - start_date).days) + 1):
        yield start_date + datetime.timedelta(n)


def get_num_cuotas(valor, new_allocation, valores_end):
    
    num_cuotas = []
    
    for perc, new_valor in zip(new_allocation, valores_end):
        num_cuotas.append((valor*perc)/new_valor)
    
    return num_cuotas

def get_posible_date(fecha_cambio, days_ahead):
    
    sel = (df_habiles['Fecha'].dt.date >= fecha_cambio) & (df_habiles['Habil'] == True)
    
    df_habiles_sel = df_habiles[sel]
    
    fecha_ahead = df_habiles_sel.iloc[days_ahead]['Fecha']
        
    return fecha_ahead

def get_valores(df_valores, fecha):
    values = df_valores.loc[fecha.strftime('%Y-%m-%d')]
    #strftime('%Y-%m-%d')
    return list(values)

def get_monto_valorizado(cuotas, valores):
    suma = 0
    for c, v in zip(cuotas, valores):
        suma += c * v
    return suma
