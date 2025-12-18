from typing import Callable, Iterable
import pandas as pd


DfCallback = Callable[[pd.DataFrame], pd.DataFrame]


def apply_df_callbacks(
    df: pd.DataFrame,
    callbacks: Iterable[DfCallback] | None
) -> pd.DataFrame:
    if not callbacks:
        return df

    for cb in callbacks:
        df = cb(df)

    return df