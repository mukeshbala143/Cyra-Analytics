import polars as pl

def missing_value_analysis(df: pl.DataFrame) -> dict:
    """
    Computes missing value count and percentage per column.
    """
    missing_info = {}
    total_rows = df.height

    for col in df.columns:
        null_count = df[col].null_count()
        missing_info[col] = {
            "missing_count": null_count,
            "missing_percentage": (null_count / total_rows) * 100
        }

    return missing_info