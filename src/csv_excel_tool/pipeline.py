import pandas as pd
from typing import Optional, Iterable

from csv_excel_tool.deduplicate import apply_deduplicate
from csv_excel_tool.reindex import apply_reindex
from csv_excel_tool.sort_key import apply_sort


def apply_common_pipeline(
    df: pd.DataFrame,
    *,
    distinct: Optional[Iterable[str]] = None,
    reindex_col: Optional[str] = None,
    random: bool = False,
    seed: Optional[int] = None,
    sortkey: Optional[Iterable[str]] = None,
    logger=None,
) -> pd.DataFrame:
    """
    通用 DataFrame 后处理管道

    执行顺序：
        1. 去重（distinct）
        2. 随机打乱（random）或 排序（sortkey，二选一）
        3. 重建索引列（reindex）

    注意：
        random 与 sortkey 互斥，random 优先
    """

    # ---------- 去重 ----------
    if distinct is not None:
        df = apply_deduplicate(
            df,
            subset=distinct,
            logger=logger,
        )

    # ---------- shuffle / sort ----------
    if random:
        if sortkey is not None and logger:
            logger.warning("random=True overrides sortkey")

        if logger:
            logger.info("shuffle dataframe", extra={"seed": seed})

        df = (
            df.sample(frac=1, random_state=seed)
              .reset_index(drop=True)
        )

    elif sortkey is not None:
        df = apply_sort(
            df,
            by=sortkey,
            logger=logger,
        )

    # ---------- reindex ----------
    if reindex_col:
        df = apply_reindex(
            df,
            col_name=reindex_col,
            logger=logger,
        )

    return df
