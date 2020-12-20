import datetime
import sys
import pandas as pd
import os
from typing import Optional, List
from .utils import generate_df_valores_cuota

MAPFONDOS = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Posicion():
    'Define una Posición particular en alguno de los 5 multifondos'
    def __init__(self, porcentajes, fecha_inicio, fecha_termino):
        self.porcentajes = porcentajes
        self.fecha_inicio = fecha_inicio
        self.fecha_termino = fecha_termino
    
    def __repr__(self):
        tt = '{} - {} : {}'.format(self.fecha_inicio,
         self.fecha_termino, self.porcentajes)
        return tt


class Estrategia():
    """
    Una Estrategia es una colección (lista) de posiciones
    entre una fecha inicial y una fecha final

    Las posiciones son leídas de un archivo de estrategias simuladas
    """
    estrategias_base = list(MAPFONDOS.keys())

    def __init__(self, fecha_ini, fecha_end, nombre_estrategia, path=None):
        self.fecha_ini = fecha_ini
        self.fecha_end = fecha_end
        self.nombre_estrategia = nombre_estrategia
        self.posiciones = self.__crea_posiciones(path)


    def __crea_posiciones(self, path: Optional[str]) -> List[Posicion]:
        """
        Si se le pasa un path, lee las posiciones de ese archivo
        Si no, asume una estrategia pasiva fija en un fondo ('A' hasta 'E')
        """
        posiciones = []

        if path:
            data = self.__get_data(path)

            date_mask = ((data['Fecha término'].dt.date >= self.fecha_ini) & \
                  (data['Fecha inicio'].dt.date <= self.fecha_end))

            df_sel = data[date_mask]
            for __, row in df_sel.iterrows():
                fini = max(row['Fecha inicio'].date(), self.fecha_ini)
                fend = min(row['Fecha término'].date(), self.fecha_end)
                porcentajes = self.__helper_porcentajes(row['Sugerencia'])
                posiciones.append(Posicion(porcentajes, fini, fend))

        else:
            #Estrategia pasiva en un solo tipo de fondo
            assert self.nombre_estrategia in self.estrategias_base, 'No existe esa estrategia'

            porcentajes = [0] * 5
            porcentajes[MAPFONDOS[self.nombre_estrategia]] = 1
            posiciones.append(Posicion(porcentajes, self.fecha_ini,
                                        self.fecha_end))
            
        return posiciones
    

    def __get_data(self, path):
        df = pd.read_excel(ROOT + '/' + path)
        df.sort_values('Fecha inicio', ascending=True, inplace=True)
        return df

    @staticmethod
    def __helper_porcentajes(sugerencia):

        partes = sugerencia.split('/')
        
        out_data = []
        for parte in partes:
            str_pos = parte.find('%')
            percent = int(parte[:str_pos])
            fondo = parte.strip()[-1]
            out_data.append((fondo, percent))
            
        allocation = [0]*5
        for fondo, perc in out_data:
            allocation[MAPFONDOS[fondo]] = perc / 100
        
        return allocation

    
    def __repr__(self):
        tt = 'Estrategia: {}\nFecha Inicio: {}\nFecha Término: {}\n\n'.format(
                self.nombre_estrategia, self.fecha_ini, self.fecha_end)
        for pos in self.posiciones[0:3]:
            tt += str(pos) + '\n'
        
        if len(self.posiciones) > 4:
            tt += '...\n' 
        tt += str(self.posiciones[-1]) + '\n'

        return tt



def agrega_estrategias(lista_estrategias, df_dias_habiles,
                        afp, monto_inicial, 
                        lag_solicitud) -> pd.DataFrame:
    '''
    Toma varias estrategias y crea un DataFrame con todas ellas consolidadas
    '''

    if type(lag_solicitud) != list:
        lag_solicitud = [lag_solicitud]*len(lista_estrategias)

    for i, estrategia in enumerate(lista_estrategias):

        df = generate_df_valores_cuota(estrategia, afp, monto_inicial,
                              lag_solicitud[i], 
                              df_dias_habiles, lag_venta=2, lag_compra=2)
        col = [c for c in df.columns if 'V_' in c]

        df = df[['Fecha'] + col]

        if i == 0:
            df_out = df
        else:
            df_out = df_out.merge(df, on=['Fecha'], how='outer')

    #arreglo los valores por si hay missings
    df_out.sort_values('Fecha', inplace=True)
    df_out.set_index('Fecha', inplace=True)
    df_out.fillna(method='ffill', inplace=True)
    df_out.reset_index(inplace=True)

    return df_out


def generate_returns_for_different_starting_dates(df: pd.DataFrame,
            años_de_horizonte: int,
            beg_period: datetime.datetime) -> pd.DataFrame:
    """
    Genera resultados desde el periodo inicial `beg_period`
    para x años hacia adelante de horizonte
    """
    horizonte_de_tiempo = pd.Timedelta(años_de_horizonte*365, unit="d")
    end_period = df.Fecha.max() - horizonte_de_tiempo
    all_starting_days_of_experiment = pd.date_range(
        beg_period, end_period, freq='d')

    relevant_columns = [col for col in df.columns if col != 'Fecha']

    rows = []
    for start_date in all_starting_days_of_experiment:
        start_data = df.loc[df.Fecha == start_date, relevant_columns]
        end_data = df.loc[df.Fecha == start_date +
                          horizonte_de_tiempo, relevant_columns]
        try:
            rows.append(
                pd.DataFrame(100 * (end_data.values / start_data.values - 1),
                             columns=relevant_columns, index=[start_date])
            )
        except:
            pass

    results = pd.concat(rows)

    return results
