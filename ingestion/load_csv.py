import polars as pl

def load_csv(file_path: str) -> pl.DataFrame:
    """
    Loads a CSV file using Polars.
    """
    df = pl.read_csv(file_path)
    return df