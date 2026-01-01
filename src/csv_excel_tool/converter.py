# csv_excel_tool/converter.py
from typing import List, Optional, Iterable
import pandas as pd
from pathlib import Path
from csv_excel_tool.df_callbacks import DfCallback, apply_df_callbacks
 

# ----------- CSV → Excel -----------
def csv_to_excel(
    csv_path,
    excel_path=None,
    *,
    asstr_cols: Optional[List[str]] = None,
    callbacks: Iterable[DfCallback] | None = None,
    logger=None
):
    csv_path = Path(csv_path)
    excel_path = Path(excel_path or csv_path.with_suffix('.xlsx'))

    # dtype 构造
    dtype = {col: str for col in asstr_cols} if asstr_cols else None

    # CSV 读取
    try:
        df = pd.read_csv(csv_path, dtype=dtype)
    except Exception as e:
        if logger:
            logger.error(f"读取 CSV 失败: {str(e)}")
        raise

    df = apply_df_callbacks(df, callbacks)

    # 保存 Excel
    df.to_excel(excel_path, index=False)

    if logger:
        logger.info(f"CSV → Excel 转换完成: {str(excel_path)}")

    return excel_path

# ----------- Excel → CSV -----------
def excel_to_csv(
    excel_path,
    csv_path=None,
    *,
    asstr_cols: Optional[List[str]] = None,
    callbacks: Iterable[DfCallback] | None = None,
    logger=None
):
    excel_path = Path(excel_path)
    csv_path = Path(csv_path or excel_path.with_suffix('.csv'))

    dtype = {col: str for col in asstr_cols} if asstr_cols else None

    # Excel 读取
    try:
        # 注意：pandas 的 read_excel 对 dtype=str 兼容性比 read_csv 弱
        # 如果 dtype 无效，仍然能读取，只是当作 object
        df = pd.read_excel(excel_path, dtype=dtype, engine="openpyxl")
    except Exception as e:
        if logger:
            logger.error(f"读取 Excel 失败: {str(e)}")
        raise

    df = apply_df_callbacks(df, callbacks)
    
    # 保存 CSV
    df.to_csv(csv_path, index=False)

    if logger:
        logger.info(f"Excel → CSV 转换完成: {str(csv_path)}")

    return csv_path