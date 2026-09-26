"""UUID管理ユーティリティ"""

import json
import uuid
import bpy


def get_object_uuid(obj: bpy.types.Object) -> str:
    """オブジェクトのUUIDを取得

    既存のUUIDがあればそれを返し、なければ生成して保存する。

    Args:
        obj: 対象のBlenderオブジェクト

    Returns:
        8文字のUUID文字列
    """
    if hasattr(obj, 'blidge') and obj.blidge.uuid:
        return obj.blidge.uuid

    # 新規生成（uuid.uuid4()）
    new_uuid = str(uuid.uuid4())[:8]

    if hasattr(obj, 'blidge'):
        obj.blidge.uuid = new_uuid

    return new_uuid


def generate_new_uuid(registry: dict) -> str:
    """レジストリと重複しない新しいUUIDを生成

    Args:
        registry: 既存のUUID辞書

    Returns:
        重複しない8文字のUUID文字列
    """
    while True:
        new_uuid = str(uuid.uuid4())[:8]
        if new_uuid not in registry:
            return new_uuid


def build_uuid_registry(scene: bpy.types.Scene = None) -> dict:
    """ファイル読み込み時にUUID→as_pointerのマッピングを構築

    Args:
        scene: 対象シーン（Noneの場合は現在のシーン）

    Returns:
        構築されたレジストリ辞書
    """
    if scene is None:
        scene = bpy.context.scene

    registry = {}

    for obj in bpy.data.objects:
        if hasattr(obj, 'blidge') and obj.blidge.uuid:
            registry[obj.blidge.uuid] = obj.as_pointer()

    # シーンに保存
    scene.blidge.uuid_registry = json.dumps(registry)

    return registry


def ensure_unique_uuids(scene: bpy.types.Scene = None) -> int:
    """UUIDの一意性を確保（複製されたオブジェクトのみ修正）

    Args:
        scene: 対象シーン（Noneの場合は現在のシーン）

    Returns:
        修正されたオブジェクトの数
    """
    if scene is None:
        scene = bpy.context.scene

    # レジストリ読み込み
    try:
        registry = json.loads(scene.blidge.uuid_registry)
    except (json.JSONDecodeError, AttributeError):
        registry = {}

    fixed_count = 0

    for obj in bpy.data.objects:
        if not hasattr(obj, 'blidge'):
            continue

        current_uuid = obj.blidge.uuid
        current_pointer = obj.as_pointer()

        # UUIDが空の場合
        if not current_uuid:
            new_uuid = generate_new_uuid(registry)
            obj.blidge.uuid = new_uuid
            registry[new_uuid] = current_pointer
            fixed_count += 1
            continue

        # UUIDが登録済みの場合
        if current_uuid in registry:
            registered_pointer = registry[current_uuid]

            # as_pointerが違う → 複製されたオブジェクト
            if registered_pointer != current_pointer:
                new_uuid = generate_new_uuid(registry)
                obj.blidge.uuid = new_uuid
                registry[new_uuid] = current_pointer
                fixed_count += 1
        else:
            # 新規オブジェクト（レジストリに追加）
            registry[current_uuid] = current_pointer

    # レジストリを保存
    scene.blidge.uuid_registry = json.dumps(registry)

    return fixed_count
