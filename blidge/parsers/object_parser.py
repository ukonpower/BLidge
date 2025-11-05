"""オブジェクトパーサー - 個別オブジェクトのパース統括"""

from typing import Dict, Any, List
import bpy
from ..transforms import convert_position, convert_rotation, convert_scale
from .camera_parser import CameraParser
from .light_parser import LightParser
from .geometry_parser import GeometryParser
from .mesh_parser import MeshParser
from .material_parser import MaterialParser


from ..utils.uuid import get_object_uuid


def _is_default_value(key: str, value: Any) -> bool:
    """デフォルト値かどうかを判定

    Args:
        key: プロパティ名
        value: 判定する値

    Returns:
        デフォルト値の場合True
    """
    defaults = {
        'rotation': [0, 0, 0],
        'scale': [1, 1, 1],
        'visible': True,
        'type': 'empty'
    }

    if key not in defaults:
        return False

    default = defaults[key]
    if isinstance(default, list):
        # リストの場合は各要素を比較（小数点誤差を考慮）
        return len(value) == len(default) and all(abs(v - d) < 0.001 for v, d in zip(value, default))
    else:
        return value == default


class ObjectParser:
    """個別オブジェクトのパース処理を統括し、専門パーサーに委譲"""

    def __init__(self, animation_data: Dict[str, Any]):
        """
        Args:
            animation_data: アニメーションデータの辞書
        """
        self.animation_data = animation_data

    def parse(self, obj: bpy.types.Object, parent_name: str) -> Dict[str, Any]:
        """オブジェクトをパースしてシーングラフノードを返す

        Args:
            obj: パース対象のBlenderオブジェクト
            parent_name: 親オブジェクトの名前

        Returns:
            オブジェクトのシーングラフノード
        """
        # オブジェクトタイプの決定
        obj_type = obj.blidge.type

        if obj.type == 'CAMERA':
            obj_type = 'camera'
        elif obj.type == 'LIGHT':
            obj_type = 'light'

        # 基本データ（必須項目のみ）
        object_data = {
            'name': obj.name,
            'uuid': get_object_uuid(obj),
            'position': convert_position(obj.location),
        }

        # type: デフォルト値('empty')以外の場合のみ追加
        if not _is_default_value('type', obj_type):
            object_data['type'] = obj_type

        # rotation: デフォルト値([0,0,0])以外の場合のみ追加
        rotation = convert_rotation(obj.rotation_euler)
        if not _is_default_value('rotation', rotation):
            object_data['rotation'] = rotation

        # scale: デフォルト値([1,1,1])以外の場合のみ追加
        scale = convert_scale(obj.scale)
        if not _is_default_value('scale', scale):
            object_data['scale'] = scale

        # visible: デフォルト値(True)以外の場合のみ追加
        visible = not obj.hide_render
        if not _is_default_value('visible', visible):
            object_data['visible'] = visible

        # カスタムプロパティ
        custom_property_list = obj.blidge.custom_property_list
        if len(custom_property_list) > 0:
            object_data['custom_properties'] = {}

            for custom_prop in custom_property_list:
                # 値を取得
                if custom_prop.prop_type == 'FLOAT':
                    value = custom_prop.value_float
                elif custom_prop.prop_type == 'INT':
                    value = custom_prop.value_int
                elif custom_prop.prop_type == 'BOOL':
                    value = custom_prop.value_bool
                else:
                    continue

                object_data['custom_properties'][custom_prop.name] = {
                    'type': custom_prop.prop_type.lower(),
                    'value': value
                }

        # アニメーション
        animation_list = obj.blidge.animation_list
        if len(animation_list) > 0:
            object_data['animation'] = {}

            for animation in animation_list:
                if animation.id and animation.id in self.animation_data.get('dict', {}):
                    # nameが設定されている場合はそれを使用、なければIDを使用
                    key = animation.name if animation.name else animation.id
                    object_data['animation'][key] = \
                        self.animation_data['dict'][animation.id]

        # 専門パーサーに委譲してパラメータを取得
        param = {}

        # カメラ
        if obj.type == 'CAMERA':
            param.update(CameraParser.parse(obj))

        # ライト
        if obj.type == 'LIGHT':
            param.update(LightParser.parse(obj))

        # プリミティブジオメトリ
        if obj.blidge.type in ['cube', 'sphere', 'plane']:
            param.update(GeometryParser.parse(obj))

        # メッシュ
        if obj.blidge.type == 'mesh' and obj.type == 'MESH':
            param.update(MeshParser.parse(obj))

        # パラメータがある場合のみ追加
        if len(param) > 0:
            object_data['param'] = param

        # ユニフォーム
        uniforms = MaterialParser.parse(obj, self.animation_data)
        if uniforms is not None:
            object_data['uniforms'] = uniforms

        # 子オブジェクトの再帰的処理
        if len(obj.children) > 0:
            object_data['children'] = []
            for child in obj.children:
                object_data['children'].append(self.parse(child, obj.name))

        return object_data
