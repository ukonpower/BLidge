"""UUID生成およびハッシュ化ユーティリティ"""
import hashlib
import bpy


def get_object_uuid(obj: bpy.types.Object) -> str:
    """オブジェクトの短縮UUID（8文字）を取得

    既存のUUIDがあればそれを返し、なければ生成して保存する。

    Args:
        obj: 対象のBlenderオブジェクト

    Returns:
        8文字の16進数文字列UUID
    """
    # 既存のUUIDがあればそれを使用
    if hasattr(obj, 'blidge') and obj.blidge.uuid:
        return obj.blidge.uuid

    # なければBlenderの内部データからハッシュ生成
    # オブジェクトのメモリアドレス（as_pointer）を使用して一意性を確保
    # 名前ベースだと同名オブジェクトで衝突するため、ポインタ値を使用
    hash_source = f"{obj.as_pointer()}_{obj.name_full}_{obj.type}"
    hash_obj = hashlib.sha256(hash_source.encode('utf-8'))
    short_uuid = hash_obj.hexdigest()[:8]

    # 保存して次回以降も同じIDを使用
    if hasattr(obj, 'blidge'):
        obj.blidge.uuid = short_uuid

    return short_uuid
