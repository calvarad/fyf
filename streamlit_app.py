import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
from src import Estrategia, agrega_estrategias
import sqlite3

matplotlib.style.use("fivethirtyeight") #type: ignore

#Cargar base de días hábiles
dbpath = r'processed_data/db_habiles.db'
conn_habiles = sqlite3.connect(dbpath)
df_dias_habiles = pd.read_sql('SELECT * FROM HABILES',
                              conn_habiles, parse_dates=['Fecha'])

# PARAMETROS PARA DEFINIR LA ESTRATEGIA
fecha_ini = pd.to_datetime('2014-01-01').date()
fecha_end = pd.to_datetime('2020-12-08').date()

afp = st.sidebar.selectbox(
    'AFP para hacer las comparaciones',
    ('HABITAT', 'MODELO')
)

estrategia_a = Estrategia(fecha_ini, fecha_end, 'A')
estrategia_e = Estrategia(fecha_ini, fecha_end, 'E')
estrategia_ff = Estrategia(fecha_ini, fecha_end, 'FF',
                           'raw_data/anuncios_ff.xlsx')

monto_inicial = 100
lag_solicitud = st.sidebar.slider(
    'Lag solicitud', 0, 5, value=0)

@st.cache
def load_data(afp, monto_inicial, lag_solicitud):

    lista_estrategias = [estrategia_a, estrategia_e, estrategia_ff]

    df = agrega_estrategias(lista_estrategias, df_dias_habiles,
                            afp, monto_inicial, lag_solicitud)
                        
    return df

def main():
    st.title("Dashboard de Retornos Felices y Forrados")
    st.sidebar.title("Opciones")

    df = load_data(afp, monto_inicial, lag_solicitud) #type: ignore

    ax = df.set_index('Fecha').plot()
    st.pyplot(ax.get_figure())

if __name__ == "__main__":
    main()
