"""メッシュデータのパーサー"""

from typing import Dict, Any, List
import bpy
from ..utils.base64 import float_array_to_base64, int_array_to_base64
from ..transforms import convert_normal


class MeshParser:
    """メッシュデータのパース処理を担当"""

    @staticmethod
    def parse(obj: bpy.types.Object) -> Dict[str, Any]:
        """メッシュデータをパースしてパラメータを返す

        Args:
            obj: メッシュオブジェクト

        Returns:
            メッシュパラメータを含む辞書(position, normal, uv, index)
        """
        if obj.blidge.type != 'mesh' or obj.type != 'MESH':
            return {}

        position: List[float] = []
        normal: List[float] = []
        index: List[int] = []
        uv: List[float] = []

        # UVデータの取得
        if len(obj.data.uv_layers) > 0:
            for uvdata in obj.data.uv_layers[0].data:
                uv.extend([
                    uvdata.uv.x,
                    uvdata.uv.y,
                ])

        # ポリゴンごとに頂点データを処理
        for pl in obj.data.polygons:
            for vt_index in pl.vertices:
                vt = obj.data.vertices[vt_index]

                # 位置座標をBlender座標系からカスタム座標系に変換
                position.extend([
                    vt.co[0],
                    vt.co[2],
                    -vt.co[1],
                ])

                # 法線の取得と変換
                if pl.use_smooth:
                    normal.extend(convert_normal(vt.normal))
                else:
                    normal.extend(convert_normal(pl.normal))

            # インデックスの処理
            lp = pl.loop_indices

            if len(lp) == 3:
                # 三角形
                index.extend([lp[0], lp[1], lp[2]])

            if len(lp) == 4:
                # 四角形を三角形に分割
                index.extend([
                    lp[0], lp[1], lp[2],
                    lp[0], lp[2], lp[3],
                ])

        # Base64エンコードして返す
        return {
            'position': float_array_to_base64(position),
            'normal': float_array_to_base64(normal),
            'uv': float_array_to_base64(uv),
            'index': int_array_to_base64(index),
        }
