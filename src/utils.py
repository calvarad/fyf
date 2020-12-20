import datetime
import os
import pandas as pd
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_df_valores_cuota(estrategia, afp, monto_inicial,
                     lag_solicitud, df_dias_habiles,
                     lag_venta=2,
                      lag_compra=2) -> pd.DataFrame:
    """
    Retorna un dataframe con la serie histórica de monto_inicial,
    ajustado según el valor cuota asociado a una estrategia de inversión
    determinada

    Cuando hay cambios de fondo es necesario ajustar para reflejar
    el mismo valor
    """
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

            sell_date = get_posible_date(df_dias_habiles, fecha_solicitud,
                                        lag_venta)
            buy_date =  get_posible_date(df_dias_habiles, fecha_solicitud,
                                        lag_compra)

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
        'Fecha', 'V_{}_{}_lag_{}'.format(afp, estrategia.nombre_estrategia, lag_solicitud), 
        'CP_A', 'CP_B', 'CP_C', 'CP_D', 'CP_E'])
    
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%Y-%m-%d')

    return df


def get_df_valores(afp, fecha_ini, fecha_end):
    path = ROOT + r'/processed_data/valores_cuota.db'
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

def get_posible_date(df_dias_habiles, fecha_cambio, days_ahead):
    
    sel = ((df_dias_habiles['Fecha'].dt.date >= fecha_cambio) 
    & (df_dias_habiles['Habil'] == True))
    
    df_habiles_sel = df_dias_habiles[sel]
    
    fecha_ahead = df_habiles_sel.iloc[days_ahead]['Fecha']
        
    return fecha_ahead


def get_valores(df_valores, fecha):
    values = df_valores.loc[fecha.strftime('%Y-%m-%d')]
    #strftime('%Y-%m-%d')
    return list(values)


def get_monto_valorizado(cuotas, valores) -> int:
    suma = 0
    for c, v in zip(cuotas, valores):
        suma += c * v
    return suma

def cuadro_rentabilidades(df_valores_cuota, df_dias_habiles):
    
    cols = [c for c in df_valores_cuota.columns if 'V_' in c]
    
    df_aux = fix_fechas(df_valores_cuota, df_dias_habiles)

    aux_data = []
    for serie in cols:
            
        fecha0 = max(df_aux.index.unique()).date()
        year0 = fecha0.year
        month0 = fecha0.month
        fechamtd = datetime.datetime(year0, month0, 1).date()
        fechaytd = datetime.datetime(year0, 1, 1).date()
        fecha1y = fecha0 - datetime.timedelta(days=365*1)
        fecha2y = fecha0 - datetime.timedelta(days=365*2)
        fecha3y = fecha0 - datetime.timedelta(days=365*3)
        fecha5y = fecha0 - datetime.timedelta(days=365*5)
        fecha8y = fecha0 - datetime.timedelta(days=365*8)

        rentmtd = df_aux.loc[fecha0][serie] / df_aux.loc[fechamtd][serie] - 1
        rentytd = df_aux.loc[fecha0][serie] / df_aux.loc[fechaytd][serie] - 1
        rent1y = df_aux.loc[fecha0][serie] / df_aux.loc[fecha1y][serie] - 1
        rent2y = (df_aux.loc[fecha0][serie] / df_aux.loc[fecha2y][serie]) ** (1/2) - 1
        rent3y = (df_aux.loc[fecha0][serie] / df_aux.loc[fecha3y][serie]) ** (1/3) - 1
        rent5y = (df_aux.loc[fecha0][serie] / df_aux.loc[fecha5y][serie]) ** (1/5) - 1
        rent8y = (df_aux.loc[fecha0][serie] / df_aux.loc[fecha8y][serie]) ** (1/8) - 1
        
        aux_data.append((serie, rentmtd, rentytd, rent1y, rent2y, rent3y, rent5y, rent8y))

    df = pd.DataFrame.from_records(aux_data, columns=[
            'Serie', 'Rent MTD', 'Rent YTD', 'Rent 1y', 'Rent 2y', 'Rent 3y', 'Rent 5y', 'Rent 8y'])

    return df

def fix_fechas(df_valores_cuota, df_dias_habiles):
    
    max_fecha = max(df_valores_cuota['Fecha']).date()
    df_aux = df_valores_cuota.merge(df_dias_habiles[df_dias_habiles['Fecha'].dt.date <= max_fecha], how='outer', on='Fecha')
    df_aux.sort_values('Fecha', inplace=True)
    df_aux.set_index('Fecha', inplace=True)
    df_aux.fillna(method='ffill', inplace=True)
    
    return df_aux


def get_annual_interest_rate(return_perc: float, 
                             n_years: float) -> float:
    """
    (1 + rx) = (1 + ra) ^ {n_years}

    ra = annual return

    return_perc = rx. Return over the n_years
    """

    return (1 + return_perc)**(1.0 / n_years) - 1
