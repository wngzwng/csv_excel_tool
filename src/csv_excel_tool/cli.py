# cli.py
import click
import time
from csv_excel_tool.common_options import common_dataframe_options
from csv_excel_tool.converter import csv_to_excel, excel_to_csv
from csv_excel_tool.splitter import split_csv, split_excel
from csv_excel_tool.merger import merge_csvs, merge_excels
from csv_excel_tool.utils import tqdm
from csv_excel_tool.df_io import read_df, write_df
from csv_excel_tool.fdlogger import FdLogger
from pathlib import Path


logger = FdLogger()

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """CSV ↔ Excel 批量处理工具（支持拆分、合并、管道输出）"""
    pass

# 1. 转换
@cli.command()
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--asstr", type=str, default=None, help="指定需要强制转为字符串的列名，多个以逗号分隔")
# @click.option("--rerange", type=str, default=None, help="需要进行重新编号的列名（从 1 开始）")
@common_dataframe_options
def convert(input_path, asstr, distinct, reindex, random, seed, sortkey):
    """ CSV <-> Excel 转换 (支持通用后处理) """
    
    from csv_excel_tool.pipeline import apply_common_pipeline
    from csv_excel_tool.common_options import parse_common_options

    p = Path(input_path)
    suffix = p.suffix.lower()

    # ------- 解析列名参数 -------
    asstr_cols = (
        [col.strip() for col in asstr.split(",") if col.strip()]
        if asstr else None
    )

    distinct_cols, reindex_col, sort_col = parse_common_options(distinct, reindex, sortkey)

    logger.info(f"输入文件: {str(p)}")

    def df_callback(df):
        return apply_common_pipeline(
            df,
            distinct=distinct_cols,
            reindex_col=reindex_col,
            logger=logger,
            random=random,
            sortkey=sort_col,
            seed=seed
        )

    # ------- 分支转换 -------
    if suffix == ".csv":
        out = p.with_suffix(".xlsx")
        logger.info("开始执行 CSV → Excel 转换")
        csv_to_excel(p, out, asstr_cols=asstr_cols, callbacks=[df_callback], logger=logger)

    elif suffix in {".xlsx", ".xls"}:
        out = p.with_suffix(".csv")
        logger.info("开始执行 Excel → CSV 转换")
        excel_to_csv(p, out, asstr_cols=asstr_cols, callbacks=[df_callback], logger=logger)

    else:
        logger.error("错误：不支持的文件格式（仅支持 .csv / .xlsx)")
        raise click.Abort()

    click.echo(str(out))  # 输出到 stdout，让管道自然处理

# 2. 拆分
@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--rows', '-r', default=100000, help='每个分片最大行数（默认10万）')
@click.option('--output-dir', '-o', default=None, help='输出目录（默认在源文件同目录创建 split_xxx）')
def split(input_path, rows, output_dir):
    """拆分 CSV 或 Excel"""
    p = Path(input_path)
    out_dir = Path(output_dir) if output_dir else p.parent / f"split_{p.stem}"
    out_dir.mkdir(exist_ok=True)

    logger.info(f"开始拆分文件 {input_path}")
    if p.suffix.lower() == '.csv':
        files = split_csv(p, out_dir, max_rows=rows)
    else:
        files = split_excel(p, out_dir, max_rows=rows)

    for f in files:
        click.echo(str(f))   # 每行输出一个拆分后的文件名（支持管道）

# 3. 合并
@cli.command()
@click.argument('folder', type=click.Path(exists=True))
@click.option('--pattern', '-p', default="*.csv", help='匹配模式，如 *.csv 或 *.xlsx, 默认 *.csv')
@click.option('--output', '-o', type=str, required=True, help='合并后输出文件名')
def merge(folder, pattern, output):
    """合并同目录下所有 CSV 或 Excel 文件"""
    folder_path = Path(folder)
    output_path = Path(output)

    if pattern.endswith('.csv'):
        merged_file = merge_csvs(folder_path, pattern, output_path)
    else:
        merged_file = merge_excels(folder_path, pattern, output_path)

    click.echo(str(merged_file))


@cli.command()
@click.argument("input", required=False)
@click.option('--output', '-o', type=str, required=True, help='处理过后的输出文件')
@common_dataframe_options
def run(input, output, distinct, reindex, random, seed, sortkey):
    """
    通用 DataFrame 处理命令（Unix filter 风格）
    """

    import sys
    import pandas as pd
    from csv_excel_tool.pipeline import apply_common_pipeline
    from csv_excel_tool.common_options import parse_common_options

    distinct_cols, reindex_col, sort_col = parse_common_options(distinct, reindex, sortkey)

    # ---------- 读 ----------
    df = read_df(input)

    # ---------- pipeline ----------
    df = apply_common_pipeline(
        df,
        distinct=distinct_cols,
        reindex_col=reindex_col,
        logger=logger,
        random=random,
        sortkey=sort_col,
        seed=seed
    )

    # ---------- 写 ----------

    write_df(df, output)
    click.echo(output)


@cli.command()
@click.argument("name", type=str, default=None)
def hello(name: str = None):
    """ 测试命令 """
    text = f"Hello, {name or 'World'}"
    logger.info(text)
    click.echo(text)

@cli.command()
@click.argument("total", type=int, default=100)
@click.option("--interval", type=int, default=50, help="每次循环的间隔时间（毫秒）")
def bartest(total: int, interval: int):
    """进度条 测试命令"""
    delay = interval / 1000.0  # 转换为秒

    for _ in tqdm(range(total), desc="进度条测试", ascii=" #"):
        time.sleep(delay)

    click.echo("progress test success")

if __name__ == '__main__':
    cli()