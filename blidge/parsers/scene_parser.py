"""シーンパーサー - シーン全体のパース統括"""

from typing import Dict, Any
import bpy
from ..animation.parser import AnimationParser
from .object_parser import ObjectParser


class SceneParser:
    """シーン全体のパース処理を統括"""

    def __init__(self):
        """コンストラクタ"""
        self.animation_data: Dict[str, Any] = {}

    def _parse_scene_graph(self) -> Dict[str, Any]:
        """シーングラフを構築

        Returns:
            ルートノードを含むシーングラフ
        """
        objects = bpy.data.objects

        # ルートノードの作成
        root_node = {
            "name": "root",
            "parent": None,
            "children": [],
            "type": 'empty',
            "visible": True,
        }

        # ObjectParserを初期化
        object_parser = ObjectParser(self.animation_data)

        # 親を持たないオブジェクトのみをルートに追加
        for obj in objects:
            if obj.parent is None:
                root_node['children'].append(object_parser.parse(obj, 'root'))

        return root_node

    def parse_scene(self) -> Dict[str, Any]:
        """シーン全体をパース

        Returns:
            アニメーション、シーングラフ、フレーム情報を含む辞書
        """
        # アニメーションデータのパース
        self.animation_data = AnimationParser.parse_animation_list()

        # シーングラフの構築
        scene_graph = self._parse_scene_graph()

        # シーンデータの構築
        scene_data = {
            "version": 2,  # データフォーマットバージョン（圧縮最適化適用）
            "animations": self.animation_data["list"],
            "fcurves": self.animation_data["fcurves"],
            "root": scene_graph,
            "frame": {
                'start': bpy.context.scene.frame_start,
                'end': bpy.context.scene.frame_end,
                'fps': bpy.context.scene.render.fps,
                'playing': False
            }
        }

        return scene_data
