import pandas as pd
import os

MAPFONDOS = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
ROOT = os.path.dirname(os.path.abspath(__file__))

class Posicion():
    'Define una Posición particular en alguno de los 5 multifondos'
    def __init__(self, porcentajes, fecha_inicio, fecha_termino):
        self.porcentajes = porcentajes
        self.fecha_inicio = fecha_inicio
        self.fecha_termino = fecha_termino
    
    def __repr__(self):
        tt = '{} - {} : {}'.format(self.fecha_inicio, self.fecha_termino, self.porcentajes)
        return tt
    
class Estrategia():
    'Una Estrategia es una colección (lista) de posiciones'
    def __init__(self, fecha_ini, fecha_end, tipo_estrategia):
        self.fecha_ini = fecha_ini
        self.fecha_end = fecha_end
        self.tipo_estrategia = tipo_estrategia
        self.posiciones = []
    
    def add_posicion(self, posicion):
        self.posiciones.append(posicion)
    
    def __repr__(self):
        tt = 'Estrategia: {}\nFecha Inicio: {}\nFecha Término: {}\n\n'.format(self.tipo_estrategia, self.fecha_ini, self.fecha_end)
        for pos in self.posiciones[0:3]:
            tt += str(pos) + '\n'
        
        if len(self.posiciones) > 3:
            tt += '...'

        return tt

class BaseEstrategias():
    def __init__(self):
        self.estrategias_posibles = ['FF', 'A', 'B', 'C', 'D', 'E']
        self.data_ff = self.__helper_base_ff()

    def crea_estrategia(self, fecha_ini, fecha_end, tipo_estrategia):
        assert tipo_estrategia in self.estrategias_posibles, 'No existe esa estrategia'

        estrategia = Estrategia(fecha_ini, fecha_end, tipo_estrategia)
        porcentajes = [0] * 5

        if tipo_estrategia == 'FF':
            sel = ((self.data_ff['Fecha término'].dt.date >= fecha_ini) & \
                  (self.data_ff['Fecha inicio'].dt.date <= fecha_end))

            df_sel = self.data_ff[sel]

            for i, row in df_sel.iterrows():
                fini = max(row['Fecha inicio'].date(), fecha_ini)
                fend = min(row['Fecha término'].date(), fecha_end)
                porcentajes = self.__helper_porcentajes(row['Sugerencia FyF'])
                posicion = Posicion(porcentajes, fini, fend)
                estrategia.add_posicion(posicion)

        else:
            porcentajes[MAPFONDOS[tipo_estrategia]] = 1
            posicion = Posicion(porcentajes, fecha_ini, fecha_end)
            estrategia.add_posicion(posicion)
            
        return estrategia

    def __helper_base_ff(self):
        df = pd.read_excel(ROOT+r'\anuncios_ff.xlsx')
        df.sort_values('Fecha inicio', ascending=True, inplace=True)

        return df

    def __helper_porcentajes(self, sugerencia):

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

