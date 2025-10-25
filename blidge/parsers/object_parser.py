"""オブジェクトパーサー - 個別オブジェクトのパース統括"""

from typing import Dict, Any, List
import bpy
from ..transforms import convert_position, convert_rotation, convert_scale
from .camera_parser import CameraParser
from .light_parser import LightParser
from .geometry_parser import GeometryParser
from .mesh_parser import MeshParser
from .material_parser import MaterialParser


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

        # 基本データ
        object_data = {
            'name': obj.name,
            'class': obj.blidge.blidgeClass,
            'type': obj_type,
            'parent': parent_name,
            'position': convert_position(obj.location),
            'rotation': convert_rotation(obj.rotation_euler),
            'scale': convert_scale(obj.scale),
            'visible': not obj.hide_render,
            'param': {},
        }

        # アニメーション
        animation_list = obj.blidge.animation_list
        if len(animation_list) > 0:
            object_data['animation'] = {}

            for animation in animation_list:
                if animation.accessor in self.animation_data.get('dict', {}):
                    object_data['animation'][animation.name] = \
                        self.animation_data['dict'][animation.accessor]

        # 専門パーサーに委譲してパラメータを取得
        # カメラ
        if obj.type == 'CAMERA':
            object_data['param'].update(CameraParser.parse(obj))

        # ライト
        if obj.type == 'LIGHT':
            object_data['param'].update(LightParser.parse(obj))

        # プリミティブジオメトリ
        if obj.blidge.type in ['cube', 'sphere', 'plane']:
            object_data['param'].update(GeometryParser.parse(obj))

        # メッシュ
        if obj.blidge.type == 'mesh' and obj.type == 'MESH':
            object_data['param'].update(MeshParser.parse(obj))

        # マテリアル
        material_data = MaterialParser.parse(obj, self.animation_data)
        if material_data is not None:
            object_data['material'] = material_data

        # 子オブジェクトの再帰的処理
        if len(obj.children) > 0:
            object_data['children'] = []
            for child in obj.children:
                object_data['children'].append(self.parse(child, obj.name))

        return object_data
