import polars as pl

def descriptive_statistics(df: pl.DataFrame) -> dict:
    """
    Computes descriptive statistics for numeric columns.
    """
    stats = {}

    numeric_cols = [
        col for col, dtype in zip(df.columns, df.dtypes)
        if dtype in (pl.Int64, pl.Float64)
    ]

    for col in numeric_cols:
        stats[col] = {
            "mean": df[col].mean(),
            "min": df[col].min(),
            "max": df[col].max(),
            "std": df[col].std()
        }

    return stats