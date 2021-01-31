import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as ptch

def get_results_for_different_starting_days(df, horizonte_de_tiempo: pd.Timedelta):

    beg_period = df.Fecha.min()
    #end_period = df.Fecha.max() - horizonte_de_tiempo
    end_period = df.Fecha.min() + pd.Timedelta("50d")

    all_starting_days_of_experiment = pd.date_range(
        beg_period, end_period, freq='d')

    relevant_columns = [col for col in df.columns if col != 'Fecha']

    rows = []
    for start_date in all_starting_days_of_experiment:
        start_data = df.loc[df.Fecha == start_date, relevant_columns]
        end_data = df.loc[df.Fecha == start_date +
                        horizonte_de_tiempo, relevant_columns]
        rows.append(pd.DataFrame(100 * (end_data.values / start_data.values - 1), columns=relevant_columns,
                                index=[start_date]))

    results = pd.concat(rows)

    return results


def compare_distributions(dataframe, col_names: list, label_names: list,
                            ax, kde_kws={}, hist=False):
    """
    kde_kws={'cumulative': True} for cumulative plots
    """
    for col, label in zip(col_names, label_names):
        sns.distplot(dataframe[col], ax=ax, label=label,
                     hist=hist, kde_kws=kde_kws)


def compare_afp_with_ff_distributions(dataframe, años_de_horizonte: int, afp: str,
                                      lag_solicitud_afp: int, lag_solicitud_ff: int, figsize=(16, 12)):
    """
    Produce un plot comparando los retornos de una estrategia FyF 
    y una estrategia simple (pasiva) de una afp en particular.
    El plot es de 3 por 2: la densidad y la distribución acumulada
    en cada columna y las tres filas con la rentabilidad del fondo A, C y E.

    Permite adicionalmente especificar el lag tanto de la afp como 
    la de la estrategia de FyF
    """
    fig, axes = plt.subplots(3, 2, figsize=figsize, sharex=True,
                             sharey="col")
    kde_option_list = [{}, {"cumulative": True}]
    axes_horizontal_pairs = [[axes[0, 0], axes[0, 1]],
                             [axes[1, 0], axes[1, 1]],
                             [axes[2, 0], axes[2, 1]]]

    for kde_kws, ax in zip(kde_option_list, axes_horizontal_pairs[0]):
        compare_distributions(dataframe, col_names=[f"V_{afp}_A_lag_{lag_solicitud_afp}",
                                                    f"V_{afp}_FF_lag_{lag_solicitud_ff}"],
                                         label_names=[f"AFP {afp} fondo A",
                                                      f"FyF lag {lag_solicitud_ff}"],
                                         ax=ax, kde_kws=kde_kws)

    for kde_kws, ax in zip(kde_option_list, axes_horizontal_pairs[1]):
        compare_distributions(dataframe, col_names=[f"V_{afp}_C_lag_{lag_solicitud_afp}",
                                                    f"V_{afp}_FF_lag_{lag_solicitud_ff}"],
                                         label_names=[f"AFP {afp} fondo C",
                                                      f"FyF lag {lag_solicitud_ff}"],
                                         ax=ax, kde_kws=kde_kws)
    
    for kde_kws, ax in zip(kde_option_list, axes_horizontal_pairs[2]):
        compare_distributions(dataframe, col_names=[f"V_{afp}_E_lag_{lag_solicitud_afp}",
                                                    f"V_{afp}_FF_lag_{lag_solicitud_ff}"],
                                         label_names=[f"AFP {afp} fondo E",
                                                      f"FyF lag {lag_solicitud_ff}"],
                                         ax=ax, kde_kws=kde_kws)

    for ax in axes.flatten():
        ax.legend()
        ax.set_xlabel("% de rentabilidad anual")
        ax.set_ylabel("")
        ax.set_yticklabels([])

    axes[0, 0].set_title("Distribución de retornos")
    axes[0, 1].set_title("Distribución de retornos acumulados")

    fig.tight_layout()

    fig.suptitle(f"""Comparación de rentabilidades anualizadas partiendo desde diferentes puntos de tiempo \n
                    Horizonte de tiempo: {años_de_horizonte} años """, y=1.13)

    rec1 = ptch.Rectangle((1, 0), 505, 590, fill=False, lw=4, edgecolor='grey')
    rec2 = ptch.Rectangle((512, 0), 505, 590, fill=False, lw=4, edgecolor='grey')
    fig.patches.extend([rec1, rec2])

    return fig, axes
