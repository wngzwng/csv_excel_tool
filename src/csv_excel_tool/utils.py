# src/csv_excel_tool/utils.py
import sys
from tqdm import tqdm as _tqdm
from functools import partial

def tqdm(*args, **kwargs):
    """
    智能 tqdm：自动判断是否在管道中，如果是则隐藏进度条
    用法和原生 tqdm 完全一样，直接全局替换即可
    """
    # if 'disable' not in kwargs:
    #     # 自动隐藏条件：
    #     # 1. stdout 被管道接住了（最常见）
    #     # 2. 或者明确设置了 QUICKCSV_NO_PROGRESS 环境变量（给脚本用的）
    #     import os
    #     disable = not sys.stdout.isatty() or bool(os.getenv("CSV_TOOL_NO_PROGRESS"))
    #     kwargs['disable'] = disable
    kwargs["file"] = sys.stderr
    return _tqdm(*args, **kwargs)

# 可选：再加一个强制静默的版本
tqdm_quiet = partial(tqdm, disable=True)