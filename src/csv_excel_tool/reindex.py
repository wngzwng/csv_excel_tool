import pandas as pd


def apply_reindex(
    df: pd.DataFrame,
    col_name: str,
    start: int = 1,
    logger=None
) -> pd.DataFrame:
    """
    对指定列重置为连续编号

    :param df: 输入 DataFrame
    :param col_name: 需要重置的列名
    :param start: 起始编号（默认 1）
    :param logger: 可选 logger
    :return: 新 DataFrame
    """
    if not col_name:
        return df

    if col_name not in df.columns:
        if logger:
            logger.warning(f"reindex 列 '{col_name}' 不存在，跳过处理")
        return df

    df = df.copy()
    end = start + len(df) - 1
    df[col_name] = range(start, start + len(df))

    if logger:
        logger.info(
            f"reindex column '{col_name}' -> [{start}..{end}]"
        )

    return df
