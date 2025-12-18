import pandas as pd
from typing import Iterable, Optional


def apply_deduplicate(
    df: pd.DataFrame,
    subset: Optional[Iterable[str]] = None,
    keep: str = "first",
    logger=None
) -> pd.DataFrame:
    """
    对 DataFrame 去重

    :param df: 输入 DataFrame
    :param subset: 用于判重的列名集合；None 表示整行
    :param keep: {"first", "last", False}
    :param logger: 可选 logger
    :return: 去重后的 DataFrame
    """
    before = len(df)

    df2 = df.drop_duplicates(subset=subset, keep=keep)

    after = len(df2)
    removed = before - after

    if logger:
        if subset:
            logger.info(
                f"deduplicate by {list(subset)}: {before} -> {after} (removed {removed})"
            )
        else:
            logger.info(
                f"deduplicate by full row: {before} -> {after} (removed {removed})"
            )

    return df2
