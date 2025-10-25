"""カメラオブジェクトのパーサー"""

import math
from typing import Dict, Any
import bpy


class CameraParser:
    """カメラオブジェクトのパース処理を担当"""

    @staticmethod
    def parse(obj: bpy.types.Object) -> Dict[str, Any]:
        """カメラオブジェクトをパースしてパラメータを返す

        Args:
            obj: カメラオブジェクト

        Returns:
            カメラパラメータを含む辞書
        """
        if obj.name not in bpy.data.cameras:
            return {}

        camera = bpy.data.cameras[obj.name]
        render = bpy.context.scene.render

        # アスペクト比を計算
        width = render.pixel_aspect_x * render.resolution_x
        height = render.pixel_aspect_y * render.resolution_y
        aspect_ratio = width / height

        # FOVを計算
        fov_radian = 1.0

        if aspect_ratio >= 1.0:
            if camera.sensor_fit != 'VERTICAL':
                fov_radian = 2.0 * math.atan(math.tan(camera.angle * 0.5) / aspect_ratio)
            else:
                fov_radian = camera.angle
        else:
            if camera.sensor_fit != 'HORIZONTAL':
                fov_radian = camera.angle
            else:
                fov_radian = 2.0 * math.atan(math.tan(camera.angle * 0.5) / aspect_ratio)

        return {
            "fov": fov_radian / math.pi * 180
        }
