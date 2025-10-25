"""プリミティブジオメトリのパーサー"""

from typing import Dict, Any
import bpy


class GeometryParser:
    """プリミティブジオメトリ(cube/sphere/plane)のパース処理を担当"""

    @staticmethod
    def parse(obj: bpy.types.Object) -> Dict[str, Any]:
        """プリミティブジオメトリをパースしてパラメータを返す

        Args:
            obj: ジオメトリオブジェクト

        Returns:
            ジオメトリパラメータを含む辞書
        """
        param = {}
        obj_type = obj.blidge.type

        if obj_type == 'cube':
            # 立方体: Y軸とZ軸を入れ替え
            param.update({
                'x': obj.blidge.param_cube.x,
                'y': obj.blidge.param_cube.z,
                'z': obj.blidge.param_cube.y,
            })

        elif obj_type == 'sphere':
            # 球体
            param.update({
                'r': obj.blidge.param_sphere.radius,
            })

        elif obj_type == 'plane':
            # 平面: Y軸をZ軸に変換
            param.update({
                'x': obj.blidge.param_plane.x,
                'y': obj.blidge.param_plane.z
            })

        return param
