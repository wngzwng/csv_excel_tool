import pandas as pd
from typing import Iterable, Optional


import pandas as pd
from typing import Iterable, Optional, Sequence


def apply_sort(
    df: pd.DataFrame,
    by: Optional[Iterable[str]] = None,
    *,
    ascending: bool | Sequence[bool] = True,
    na_position: str = "last",
    reset_index: bool = False,
    logger=None,
) -> pd.DataFrame:
    """
    对 DataFrame 排序（仅排序）

    :param df: 输入 DataFrame
    :param by: 排序列名；None 表示不排序（直接返回副本）
    :param ascending: 升序 / 降序
    :param na_position: {"first", "last"}
    :param reset_index: 是否重置索引
    :param logger: 可选 logger
    :return: 排序后的 DataFrame
    """
    # ---------- 参数校验 ----------
    if by is None:
        if logger:
            logger.info("sort skipped (no sort keys)")
        return df

    by = list(by)
    if not by:
        if logger:
            logger.warning("empty sort keys, skip sorting")
        return df

    missing = set(by) - set(df.columns)
    if missing:
        raise KeyError(f"sort columns not in DataFrame: {sorted(missing)}")

    if na_position not in ("first", "last"):
        raise ValueError(f"invalid na_position: {na_position!r}")

    # ---------- 执行排序 ----------
    before = len(df)

    result = df.sort_values(
        by=by,
        ascending=ascending,
        na_position=na_position,
        kind="mergesort",  # 稳定排序（对 pipeline 很重要）
    )

    if reset_index:
        result = result.reset_index(drop=True)

    # ---------- 日志 ----------
    if logger:
        logger.info(
            "sort",
            extra={
                "by": by,
                "ascending": ascending,
                "na_position": na_position,
                "rows": before,
            },
        )

    return result

