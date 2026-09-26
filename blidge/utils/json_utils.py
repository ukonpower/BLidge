"""JSON関連のユーティリティ関数"""


def round_floats(obj):
    """
    オブジェクト内のすべての浮動小数点数を3桁に丸める

    Args:
        obj: 処理対象のオブジェクト（dict, list, float, その他）

    Returns:
        丸められた数値を含むオブジェクト
    """
    if isinstance(obj, float):
        return round(obj, 3)
    elif isinstance(obj, dict):
        return {k: round_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(item) for item in obj]
    return obj
