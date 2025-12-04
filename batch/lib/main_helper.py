
def safe_load_master(load_tasks: dict):
    """
    マスターデータを安全にロードするための関数。

    Args:
        load_tasks (dict): ロードするマスターデータと、それをロードするための
                           引数なしの関数を値に持つ辞書。
                           例: {"master_name": lambda: load_csv("path/to/master.csv")}

    Returns:
        dict: ロードされたマスターデータ（pandas DataFrame）を値に持つ辞書。

    Raises:
        RuntimeError: いずれかのマスターデータのロードに失敗した場合、またはデータが空だった場合。
    """
    results = {}
    errors = []
    for name, loader in load_tasks.items():
        try:
            df = loader()
            if df.empty:
                raise ValueError(f"{name} is empty")
            results[name] = df
        except Exception as e:
            errors.append(f"{name}: {e}")
    if errors:
        raise RuntimeError("Master load failed:\n" + "\n".join(errors))
    return results

# ---- safe pipe wrapper ----
def safe_pipe(func, *args, debug=False, **kwargs):
    """
    pipe 用ラッパー。
    - func: DataFrame を最初の引数に取る関数
    - *args, **kwargs: func に渡す追加引数
    - debug: True の場合、処理後の DataFrame の shape を出力
    """
    def wrapper(df):
        try:
            result = func(df, *args, **kwargs)
            if debug:
                print(f"[DEBUG] {func.__name__} -> shape: {result.shape}")
            return result
        except Exception as e:
            raise RuntimeError(f"pipeステップ '{func.__name__}' でエラー発生: {e}")
    return wrapper


def get_value_as_str(df, key):
    val = df.loc[df["項目"] == key, "初期値"].values[0]

    # --- tuple/list を1要素なら解体 ---
    if isinstance(val, (tuple, list)) and len(val) == 1:
        val = val[0]

    return str(val)
