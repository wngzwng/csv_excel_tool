import click


def common_dataframe_options(func):
    """
    通用 DataFrame 后处理参数（Unix filter 风格）：

    --distinct   去重列（支持多列）
    --reindex    重建连续索引列（1..N）
    --random     随机打乱行顺序
    --seed       随机种子（保证可复现）
    """

    func = click.option(
        "--distinct",
        type=str,
        default=None,
        metavar="COLS",
        help="去重列名，多个以逗号分隔（如: id,name）；不传表示不去重"
    )(func)

    func = click.option(
        "--reindex",
        type=str,
        default=None,
        metavar="COL",
        help="将指定列重建为连续 1..N（如: id）"
    )(func)

    func = click.option(
        "--random",
        is_flag=True,
        help="随机打乱行顺序"
    )(func)

    func = click.option(
        "--seed",
        type=int,
        default=None,
        show_default=True,
        help="随机种子（用于 --random，保证结果可复现）"
    )(func)

    return func


def parse_common_options(distinct, reindex):
    distinct_cols = (
        [c.strip() for c in distinct.split(",") if c.strip()]
        if distinct else None
    )
    reindex_col = reindex.strip() if reindex else None
    return distinct_cols, reindex_col