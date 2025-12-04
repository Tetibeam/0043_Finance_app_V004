import pandas as pd
import os
from .exceptions import FileFormatError, MissingFileError, RawDataError

def load_parquet(filepath):
    if not filepath.lower().endswith(".parquet"):
        raise FileFormatError(f"Not a parquet file: {filepath}")

    if not os.path.exists(filepath):
        raise MissingFileError(f"Parquet file not found: {filepath}")

    if os.path.getsize(filepath) == 0:
        raise FileFormatError(f"Parquet file is empty: {filepath}")

    try:
        return pd.read_parquet(filepath, engine='pyarrow')

    except ValueError as e:
        # schema mismatch / corrupted parquet など
        raise ValueError(f"Invalid parquet file: {filepath}\nDetails: {e}")

    except ImportError as e:
        # pyarrow が無いなど
        raise ImportError(f"Parquet engine error (pyarrow?): {e}")

    except Exception as e:
        # 他の想定外の例外はまとめて投げ直す
        raise RuntimeError(f"Unexpected error while loading parquet: {filepath}\nDetails: {e}")

def save_parquet(df, filepath):
    if df is None:
        raise ValueError("Attempted to save None dataframe.")
    out_dir = os.path.dirname(filepath)
    if out_dir and not os.path.exists(out_dir):
        raise MissingFileError(f"Output directory does not exist: {out_dir}")

    tmp_path = filepath + ".tmp"

    try:
        df.to_parquet(tmp_path, engine='pyarrow')
        os.replace(tmp_path, filepath)
    except Exception as e:
        raise RawDataError(f"Failed to save parquet: {filepath}\n{e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def load_csv(filepath):
    if not filepath.lower().endswith(".csv"):
        raise FileFormatError(f"Not a CSV file: {filepath}")

    if not os.path.exists(filepath):
        raise MissingFileError(f"CSV file not found: {filepath}")

    if os.path.getsize(filepath) == 0:
        raise FileFormatError(f"CSV file is empty: {filepath}")

    try:
        df = pd.read_csv(filepath)
        return df
    except UnicodeDecodeError as e:
        raise FileFormatError(f"Encoding error in CSV: {filepath}\n{e}")
    except pd.errors.ParserError as e:
        raise FileFormatError(f"CSV parse error: {filepath}\n{e}")
    except Exception as e:
        raise RawDataError(f"Unexpected CSV load error: {filepath}\n{e}")

def save_csv(df, filepath):
    if df is None:
        raise ValueError("Attempted to save None dataframe.")

    out_dir = os.path.dirname(filepath)
    if out_dir and not os.path.exists(out_dir):
        raise MissingFileError(f"Output directory does not exist: {out_dir}")

    tmp_path = filepath + ".tmp"

    try:
        df.to_csv(tmp_path, index=False)
        os.replace(tmp_path, filepath)
    except Exception as e:
        raise RawDataError(f"Failed to save CSV: {filepath}\n{e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
