import pandas as pd
import os
from typing import Optional, List

MAPFONDOS = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
ROOT = os.path.dirname(os.path.abspath(__file__))


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




