# csv_excel_tool/splitter.py
import pandas as pd
from pathlib import Path
# from tqdm import tqdm
from csv_excel_tool.utils import tqdm

def split_csv(csv_path, output_dir, max_rows=100000):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    chunk_iter = pd.read_csv(csv_path, chunksize=max_rows)
    files = []
    for i, chunk in enumerate(tqdm(chunk_iter, desc="拆分 CSV")):
        out_file = output_dir / f"{csv_path.stem}_part{i+1:04d}.csv"
        chunk.to_csv(out_file, index=False)
        files.append(out_file)
    return files

def split_excel(excel_path, output_dir, max_rows=100000):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_excel(excel_path)
    total = len(df)
    files = []
    for i in tqdm(range(0, total, max_rows), desc="拆分 Excel"):
        chunk = df.iloc[i:i+max_rows]
        out_file = output_dir / f"{excel_path.stem}_part{i//max_rows + 1:04d}.xlsx"
        chunk.to_excel(out_file, index=False)
        files.append(out_file)
    return files