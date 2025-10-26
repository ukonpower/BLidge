"""アニメーション(F-Curve)のパーサー"""

from typing import Dict, Any, List, Optional
import bpy
from ..utils.fcurve_manager import get_fcurve_id


class AnimationParser:
    """アニメーションデータのパース処理を担当"""

    @staticmethod
    def parse_vector(vector: Any) -> Dict[str, float]:
        """ベクトルを辞書形式にパース

        Args:
            vector: ベクトルオブジェクト

        Returns:
            x, y, z, w要素を持つ辞書
        """
        parsed_vector = {}
        if hasattr(vector, "x"):
            parsed_vector["x"] = vector.x
        if hasattr(vector, "y"):
            parsed_vector["y"] = vector.y
        if hasattr(vector, "z"):
            parsed_vector["z"] = vector.z
        if hasattr(vector, "w"):
            parsed_vector["w"] = vector.w
        return parsed_vector

    @staticmethod
    def parse_keyframe(
        keyframe: bpy.types.Keyframe,
        before_keyframe: Optional[bpy.types.Keyframe]
    ) -> List[Any]:
        """キーフレームをパース

        Args:
            keyframe: キーフレーム
            before_keyframe: 前のキーフレーム

        Returns:
            [補間タイプ, [座標とハンドル]]
        """
        c = AnimationParser.parse_vector(keyframe.co)
        interpolation = keyframe.interpolation[0]
        parsed_keyframe = [
            interpolation,
            [c["x"], c["y"]],
        ]

        # ベジエ補間の場合、ハンドル情報を追加
        if interpolation == 'B' or (before_keyframe is not None and before_keyframe.interpolation[0] == 'B'):
            h_l = AnimationParser.parse_vector(keyframe.handle_left)
            parsed_keyframe[1].extend([h_l["x"], h_l["y"]])

        if interpolation == 'B':
            h_r = AnimationParser.parse_vector(keyframe.handle_right)
            parsed_keyframe[1].extend([h_r["x"], h_r["y"]])

        return parsed_keyframe

    @staticmethod
    def parse_keyframe_list(
        keyframes: List[bpy.types.Keyframe],
        invert: bool
    ) -> List[List[Any]]:
        """キーフレームリストをパース

        Args:
            keyframes: キーフレームのリスト
            invert: Y軸を反転するかどうか

        Returns:
            パースされたキーフレームのリスト
        """
        parsed_keyframes = []
        for i, keyframe in enumerate(keyframes):
            if i > 0:
                prev_keyframe = keyframes[i - 1]
                parsed_keyframe = AnimationParser.parse_keyframe(keyframe, prev_keyframe)
            else:
                parsed_keyframe = AnimationParser.parse_keyframe(keyframe, None)

            # Y軸の反転処理
            if invert:
                parsed_keyframe[1][1] *= -1
                if len(parsed_keyframe[1]) > 2:
                    parsed_keyframe[1][3] *= -1
                if len(parsed_keyframe[1]) > 4:
                    parsed_keyframe[1][5] *= -1

            parsed_keyframes.append(parsed_keyframe)
        return parsed_keyframes

    @staticmethod
    def parse_fcurve(fcurve: bpy.types.FCurve) -> Dict[str, Any]:
        """F-Curveをパース

        Args:
            fcurve: F-Curve

        Returns:
            axis(軸)とk(キーフレーム)を含む辞書
        """
        parsed_fcurve = {
            "axis": "x",
            "k": None
        }

        # Y軸プロパティは反転フラグを立てる
        fcurve_id = get_fcurve_id(fcurve, True)
        invert = fcurve_id.find('location_y') > -1 or fcurve_id.find('rotation_euler_y') > -1
        parsed_fcurve['k'] = AnimationParser.parse_keyframe_list(fcurve.keyframe_points, invert)

        # F-Curveプロパティから軸情報を取得
        for fcurve_prop in bpy.context.scene.blidge.fcurve_list:
            if fcurve_prop.id == fcurve_id:
                parsed_fcurve['axis'] = fcurve_prop.axis
                break

        return parsed_fcurve

    @staticmethod
    def parse_animation_list() -> Dict[str, Any]:
        """すべてのアニメーションをパース

        Returns:
            list(アニメーションリスト)とdict(アニメーションIDマッピング)を含む辞書
        """
        animation_list = []
        animation_dict = {}
        dict_counter = 0

        def get_fcurve_prop(fcurve: bpy.types.FCurve) -> Optional[Any]:
            """F-Curveプロパティを取得"""
            fcurve_axis_id = get_fcurve_id(fcurve, True)
            for fcurve_prop in bpy.context.scene.blidge.fcurve_list:
                if fcurve_prop.id == fcurve_axis_id:
                    return fcurve_prop
            return None

        # すべてのアクションからF-Curveを抽出
        for action in bpy.data.actions:
            for fcurve in action.fcurves:
                fcurve_prop = get_fcurve_prop(fcurve)
                if fcurve_prop is not None and fcurve_prop.animation_id:
                    animation_id = fcurve_prop.animation_id
                    if animation_id not in animation_dict:
                        animation_dict[animation_id] = dict_counter
                        animation_list.append([])
                        dict_counter += 1
                    animation_list[animation_dict[animation_id]].append(
                        AnimationParser.parse_fcurve(fcurve)
                    )

        return {"list": animation_list, "dict": animation_dict}
