"""ライトオブジェクトのパーサー"""

from typing import Dict, Any
import bpy


class LightParser:
    """ライトオブジェクトのパース処理を担当"""

    @staticmethod
    def parse(obj: bpy.types.Object) -> Dict[str, Any]:
        """ライトオブジェクトをパースしてパラメータを返す

        Args:
            obj: ライトオブジェクト

        Returns:
            ライトパラメータを含む辞書
        """
        if obj.type != 'LIGHT':
            return {}

        light = obj.data
        param = {
            'shadow_map': obj.blidge.param_light.shadow_map,
            'color': {
                'x': light.color[0],
                'y': light.color[1],
                'z': light.color[2],
            },
            # OREngine の Light.intensity は Blender と同じ放射量の単位（Sun は W/m²、Spot は W）なので換算しない
            'intensity': light.energy
        }

        # ライトタイプ別の処理
        if light.type == 'SUN':
            param['type'] = 'directional'
        elif light.type == 'SPOT':
            param['type'] = 'spot'
            param.update({
                'angle': light.spot_size,
                'blend': light.spot_blend
            })
            # カスタム距離が有効な場合はdistanceを出力
            if light.use_custom_distance:
                param['distance'] = light.cutoff_distance

        return param
