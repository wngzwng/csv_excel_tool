from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Iterable, List, NamedTuple
from csv_excel_tool.utils import tqdm

import pandas as pd


# ============================================================
# Intent（意图层）
# ============================================================

@dataclass(frozen=True)
class SplitIntent:
    rows: int
    by: str | None
    where: str | None

    def describe(self) -> str:
        if self.where:
            return f"partition({self.where})"
        if self.by:
            return f"groupby({self.by})"
        return f"rows({self.rows})"


# ============================================================
# 基础数据结构
# ============================================================

class SplitResult(NamedTuple):
    name: str
    df: pd.DataFrame


@dataclass(frozen=True)
class SplitContext:
    index: int
    start: int
    end: int
    total: int
    ext: str


NameFunc = Callable[[SplitContext], str]


# ============================================================
# 抽象基类
# ============================================================

class Splitter(ABC):
    """拆分策略抽象基类"""

    @abstractmethod
    def split(self, df: pd.DataFrame) -> Iterable[SplitResult]:
        ...


# ============================================================
# 1️⃣ RowSplitter
# ============================================================

class RowSplitter(Splitter):
    def __init__(
        self,
        *,
        max_rows: int,
        name_func: NameFunc,
        ext: str,
    ):
        if max_rows <= 0:
            raise ValueError("max_rows must be positive")

        self.max_rows = max_rows
        self.name_func = name_func
        self.ext = ext

    def split(self, df: pd.DataFrame) -> List[SplitResult]:
        total = len(df)
        if total == 0:
            return []

        results: List[SplitResult] = []


        for idx, start in enumerate(range(0, total, self.max_rows)):
            end = min(start + self.max_rows, total)

            ctx = SplitContext(
                index=idx,
                start=start,
                end=end,
                total=total,
                ext=self.ext,
            )

            name = self.name_func(ctx)
            results.append(SplitResult(name, df.iloc[start:end]))

        return results


# ============================================================
# 2️⃣ PartitionSplitter
# ============================================================

class PartitionSplitter(Splitter):
    def __init__(
        self,
        *,
        column: str,
        value: object,
        name_func: Callable[[str, object], str],
    ):
        self.column = column
        self.value = value
        self.name_func = name_func

    def split(self, df: pd.DataFrame) -> List[SplitResult]:
        if self.column not in df.columns:
            raise KeyError(self.column)

        series = df[self.column]

        try:
            value = series.dtype.type(self.value)
        except Exception:
            value = self.value

        mask = series == value

        return [
            SplitResult(self.name_func("eq", value), df[mask]),
            SplitResult(self.name_func("ne", value), df[~mask]),
        ]


# ============================================================
# 3️⃣ GroupBySplitter
# ============================================================

class GroupBySplitter(Splitter):
    def __init__(
        self,
        *,
        column: str,
        name_func: Callable[[object], str],
        dropna: bool = False,
        max_groups: int | None = None,
    ):
        if max_groups is not None and max_groups <= 0:
            raise ValueError("max_groups must be positive or None")

        self.column = column
        self.name_func = name_func
        self.dropna = dropna
        self.max_groups = max_groups

    def split(self, df: pd.DataFrame) -> List[SplitResult]:
        if self.column not in df.columns:
            raise KeyError(self.column)

        results: List[SplitResult] = []
        count = 0

        for key, group in df.groupby(self.column, dropna=self.dropna):
            count += 1

            if self.max_groups is not None and count > self.max_groups:
                raise ValueError(
                    f"groupby({self.column}) produced more than "
                    f"{self.max_groups} groups"
                )

            results.append(
                SplitResult(self.name_func(key), group)
            )

        return results



# ============================================================
# Naming helpers
# ============================================================

def default_row_namer(prefix: str) -> NameFunc:
    def _namer(ctx: SplitContext) -> str:
        return f"{prefix}_part{ctx.index:04d}.{ctx.ext}"
    return _namer


def default_group_namer(prefix: str, ext: str):
    def _namer(value: object) -> str:
        suffix = "NA" if pd.isna(value) else str(value)
        return f"{prefix}_{suffix}.{ext}"
    return _namer


def default_partition_namer(prefix: str, ext: str):
    def _namer(op: str, value: object) -> str:
        suffix = "NA" if pd.isna(value) else str(value)
        return f"{prefix}_{op}_{suffix}.{ext}"
    return _namer


# ============================================================
# Factory（意图 → Splitter）
# ============================================================

def resolve_splitter(
    intent: SplitIntent,
    *,
    prefix: str,
    ext: str,
    max_groups: int | None = None,
) -> Splitter:
    if intent.where:
        if "=" not in intent.where:
            raise ValueError("where must be COLUMN=VALUE")

        column, value = intent.where.split("=", 1)
        return PartitionSplitter(
            column=column,
            value=value,
            name_func=default_partition_namer(prefix, ext),
        )

    if intent.by:
        return GroupBySplitter(
            column=intent.by,
            name_func=default_group_namer(prefix, ext),
            max_groups=max_groups
        )

    return RowSplitter(
        max_rows=intent.rows,
        name_func=default_row_namer(prefix),
        ext=ext,
    )
