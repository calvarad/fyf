import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
import os
from src import (Estrategia, agrega_estrategias,
                 get_annual_interest_rate,
                 compare_distributions,
                 get_results_for_different_starting_days)
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
estrategia_c = Estrategia(fecha_ini, fecha_end, 'C')
estrategia_e = Estrategia(fecha_ini, fecha_end, 'E')
estrategia_ff = Estrategia(fecha_ini, fecha_end, 'FF',
                           'raw_data/anuncios_ff.xlsx')

monto_inicial = 100
lag_solicitud = st.sidebar.slider(
    'Lag solicitud', 0, 5, value=0)


@st.cache
def load_data(afp, monto_inicial, lag_solicitud):

    lista_estrategias = [estrategia_a, estrategia_c, estrategia_e, estrategia_ff]

    df = agrega_estrategias(lista_estrategias, df_dias_habiles,
                            afp, monto_inicial, lag_solicitud)
                        
    return df

@st.cache
def compare_afp_with_ff_distributions(dataframe, horizonte_de_tiempo: pd.Timedelta, afp: str,
                                        lag_solicitud: int):
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))

    for kde_kws, ax in zip([{}, {"cumulative": True}],
                          [axes[0, 0], axes[0, 1]]):
        compare_distributions(dataframe, col_names=[f"V_{afp}_A_lag_{lag_solicitud}",
                                                f"V_{afp}_FF_lag_{lag_solicitud}"],
                          ax=ax, kde_kws=kde_kws)

    compare_distributions(dataframe, col_names=[f"V_{afp}_C_lag_{lag_solicitud}",
                                                f"V_{afp}_FF_lag_{lag_solicitud}"],
                        ax=axes[1, 0])
    compare_distributions(dataframe, col_names=[f"V_{afp}_C_lag_{lag_solicitud}",
                                                f"V_{afp}_FF_lag_{lag_solicitud}"],
                        ax=axes[1, 1], kde_kws={"cumulative": True})

    compare_distributions(dataframe, col_names=[f"V_{afp}_E_lag_{lag_solicitud}",
                                                f"V_{afp}_FF_lag_{lag_solicitud}"],
                        ax=axes[2, 0])
    compare_distributions(dataframe, col_names=[f"V_{afp}_E_lag_{lag_solicitud}",
                                                f"V_{afp}_FF_lag_{lag_solicitud}"],
                        ax=axes[2, 1], kde_kws={"cumulative": True})

    for ax in axes.flatten():
        ax.legend()
        ax.set_xlabel("% de rentabilidad")

    ax.legend()

    fig.tight_layout()

    fig.suptitle(f"""Comparación de rentabilidades partiendo desde diferentes puntos de tiempo \n
                    Horizonte de tiempo: {horizonte_de_tiempo.days / 365} años """, y=1.1)

    return fig, axes


def main():
    st.title("Dashboard de Retornos Felices y Forrados")
    st.sidebar.title("Opciones")

    df = load_data(afp, monto_inicial, lag_solicitud) #type: ignore

    ax = df.set_index('Fecha').plot()
    st.pyplot(ax.get_figure())

    st.markdown("### Distribuciones acumuladas")

    st.markdown("""**explicación del ejercicio acá:** Se consideran diferentes puntos de partida
                 para un horizonte de tiempo fijo""")

    n_años_de_horizonte = st.slider(
        'Número de años de horizonte de tiempo', 1, 5, value=3)

    horizonte_de_tiempo: pd.Timedelta = pd.Timedelta(n_años_de_horizonte*365, unit="d")

    #Get dataframe with results
    results_df = get_results_for_different_starting_days(df, horizonte_de_tiempo)

    fig, axes = compare_afp_with_ff_distributions(results_df, horizonte_de_tiempo,
                                                 afp, lag_solicitud)

    st.pyplot(fig)

if __name__ == "__main__":
    main()
