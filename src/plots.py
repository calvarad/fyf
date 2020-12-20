import numpy as np
import seaborn as sns
import pandas as pd

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


def compare_distributions(dataframe, col_names: list, ax, kde_kws={},
                         hist=False):
    """
    kde_kws={'cumulative': True} for cumulative plots
    """
    for col in col_names:
        sns.distplot(dataframe[col], ax=ax, label=col,
                     hist=hist, kde_kws=kde_kws)
