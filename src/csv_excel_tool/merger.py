# csv_excel_tool/merger.py
import pandas as pd
from pathlib import Path
# from tqdm import tqdm
from csv_excel_tool.utils import tqdm
import glob

def merge_csvs(folder, pattern="*.csv", output_path=None):
    folder = Path(folder)
    files = sorted(folder.glob(pattern))
    if not files:
        raise FileNotFoundError("没找到匹配的文件")
    output_path = output_path or folder / f"merged_{folder.name}.csv"
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        for i, f in enumerate(tqdm(files, desc="合并 CSV")):
            with open(f, 'r', encoding='utf-8') as infile:
                if i > 0:
                    next(infile)  # 跳过表头
                outfile.write(infile.read())
                outfile.write("\n")
    return output_path

def merge_excels(folder, pattern="*.xlsx", output_path=None):
    folder = Path(folder)
    files = sorted(folder.glob(pattern))
    if not files:
        raise FileNotFoundError("没找到匹配的文件")
    output_path = output_path or folder / f"merged_{folder.name}.xlsx"
    dfs = [pd.read_excel(f, engine="openpyxl") for f in tqdm(files, desc="合并 Excel")]
    pd.concat(dfs, ignore_index=True).to_excel(output_path, index=False, engine="openpyxl")
    return output_path