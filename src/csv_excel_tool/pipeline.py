import pandas as pd
from typing import Optional, Iterable

from csv_excel_tool.deduplicate import apply_deduplicate
from csv_excel_tool.reindex import apply_reindex


def apply_common_pipeline(
    df: pd.DataFrame,
    *,
    distinct: Optional[Iterable[str]] = None,
    reindex_col: Optional[str] = None,
    random: bool = False,
    seed: Optional[int] = None,
    logger=None
) -> pd.DataFrame:
    """
    通用 DataFrame 后处理管道
    顺序：去重 → 重置 ID
    """

    if distinct is not None:
        df = apply_deduplicate(
            df,
            subset=distinct,
            logger=logger
        )

    if random:
            logger and logger.info(f"Shuffle DataFrame (seed={seed})")
            df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    if reindex_col:
        df = apply_reindex(
            df,
            col_name=reindex_col,
            logger=logger
        )

            
    return df
