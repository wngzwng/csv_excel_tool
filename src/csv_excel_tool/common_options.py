import click


def common_dataframe_options(func):
    """
    通用 DataFrame 后处理参数：
    --distinct / --reindex
    """
    func = click.option(
        "--distinct",
        type=str,
        default=None,
        help="去重列名，多个以逗号分隔；不传表示不去重"
    )(func)

    func = click.option(
        "--reindex",
        type=str,
        default=None,
        help="重置为 1..N 的列名"
    )(func)

    return func


def parse_common_options(distinct, reindex):
    distinct_cols = (
        [c.strip() for c in distinct.split(",") if c.strip()]
        if distinct else None
    )
    reindex_col = reindex.strip() if reindex else None
    return distinct_cols, reindex_col