"""アニメーション(F-Curve)のパーサー"""

from typing import Dict, Any, List, Optional
import bpy
from .fcurve_id import get_fcurve_id

# 補間タイプのマッピング: L(Linear)=0, C(Constant)=1, B(Bezier)=2
INTERPOLATION_MAP = {
    'L': 0,  # Linear
    'C': 1,  # Constant
    'B': 2,  # Bezier
}


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
            [補間タイプ(数値), [座標とハンドル]]
        """
        c = AnimationParser.parse_vector(keyframe.co)
        interpolation_char = keyframe.interpolation[0]
        # 補間タイプを数値に変換 (L→0, C→1, B→2)
        interpolation_code = INTERPOLATION_MAP.get(interpolation_char, 0)

        parsed_keyframe = [
            interpolation_code,
            [c["x"], c["y"]],
        ]

        # ベジエ補間の場合のみ、ハンドル情報を追加
        if interpolation_char == 'B' or (before_keyframe is not None and before_keyframe.interpolation[0] == 'B'):
            h_l = AnimationParser.parse_vector(keyframe.handle_left)
            parsed_keyframe[1].extend([h_l["x"], h_l["y"]])

        if interpolation_char == 'B':
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
            パースされたキーフレームのリスト（差分エンコーディング適用）
        """
        parsed_keyframes = []
        prev_frame = 0

        for i, keyframe in enumerate(keyframes):
            if i > 0:
                prev_keyframe = keyframes[i - 1]
                parsed_keyframe = AnimationParser.parse_keyframe(keyframe, prev_keyframe)
            else:
                parsed_keyframe = AnimationParser.parse_keyframe(keyframe, None)

            # フレーム番号を差分エンコーディングに変換
            current_frame = parsed_keyframe[1][0]
            if i == 0:
                # 最初のキーフレームは絶対値
                frame_value = current_frame
            else:
                # 2番目以降は前のフレームからの差分
                frame_value = current_frame - prev_frame

            parsed_keyframe[1][0] = frame_value
            prev_frame = current_frame

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
        for fcurve_prop in bpy.context.scene.blidge.fcurve_mappings:
            if fcurve_prop.id == fcurve_id:
                parsed_fcurve['axis'] = fcurve_prop.axis
                break

        return parsed_fcurve

    @staticmethod
    def _get_fcurve_props(fcurve: bpy.types.FCurve) -> List[Any]:
        """F-Curveに紐づくプロパティをすべて取得

        Args:
            fcurve: 対象のF-Curve

        Returns:
            マッチしたF-Curveプロパティのリスト
        """
        fcurve_axis_id = get_fcurve_id(fcurve, True)
        return [
            fcurve_prop
            for fcurve_prop in bpy.context.scene.blidge.fcurve_mappings
            if fcurve_prop.id == fcurve_axis_id
        ]

    @staticmethod
    def _ensure_animation_id_exists(animation_id: str, animation_dict: Dict[str, int],
                                     animation_list: List[List], counter: int) -> int:
        """アニメーションIDが存在しない場合、新規追加

        Args:
            animation_id: アニメーションID
            animation_dict: アニメーションIDとインデックスのマッピング
            animation_list: アニメーションデータのリスト
            counter: 現在のカウンター値

        Returns:
            更新後のカウンター値
        """
        if animation_id not in animation_dict:
            animation_dict[animation_id] = counter
            animation_list.append([])
            return counter + 1
        return counter

    @staticmethod
    def _process_fcurve(fcurve: bpy.types.FCurve, animation_dict: Dict[str, int],
                        animation_list: List[List], fcurve_list: List[Dict[str, Any]],
                        fcurve_dict: Dict[str, int]) -> None:
        """F-Curveを処理してアニメーションリストに追加

        Args:
            fcurve: 処理対象のF-Curve
            animation_dict: アニメーションIDとインデックスのマッピング
            animation_list: アニメーションデータのリスト
            fcurve_list: F-Curveデータの共有リスト
            fcurve_dict: F-Curve IDとインデックスのマッピング
        """
        fcurve_props = AnimationParser._get_fcurve_props(fcurve)
        fcurve_id = get_fcurve_id(fcurve, True)

        # F-Curveがまだ共有リストにない場合は追加
        if fcurve_id not in fcurve_dict:
            parsed_fcurve = AnimationParser.parse_fcurve(fcurve)
            fcurve_dict[fcurve_id] = len(fcurve_list)
            fcurve_list.append(parsed_fcurve)

        fcurve_index = fcurve_dict[fcurve_id]

        # 各アニメーションIDに対してF-Curveインデックスを追加
        for fcurve_prop in fcurve_props:
            if not fcurve_prop.animation_id:
                continue

            animation_id = fcurve_prop.animation_id
            animation_index = animation_dict.get(animation_id)

            if animation_index is not None:
                animation_list[animation_index].append(fcurve_index)

    @staticmethod
    def parse_animation_list() -> Dict[str, Any]:
        """すべてのアニメーションをパース

        Returns:
            list(アニメーションリスト)とdict(アニメーションIDマッピング)、fcurves(F-Curveリスト)を含む辞書
        """
        animation_list: List[List] = []
        animation_dict: Dict[str, int] = {}
        fcurve_list: List[Dict[str, Any]] = []
        fcurve_dict: Dict[str, int] = {}  # F-Curve IDとインデックスのマッピング
        counter = 0

        # 1パス目: すべてのanimation_idを収集して辞書とリストを構築
        for action in bpy.data.actions:
            for fcurve in action.fcurves:
                fcurve_props = AnimationParser._get_fcurve_props(fcurve)
                for fcurve_prop in fcurve_props:
                    if fcurve_prop.animation_id:
                        counter = AnimationParser._ensure_animation_id_exists(
                            fcurve_prop.animation_id, animation_dict, animation_list, counter
                        )

        # 2パス目: F-Curveデータを処理し、共有リストとアニメーションへの参照を構築
        for action in bpy.data.actions:
            for fcurve in action.fcurves:
                AnimationParser._process_fcurve(fcurve, animation_dict, animation_list, fcurve_list, fcurve_dict)

        return {"list": animation_list, "dict": animation_dict, "fcurves": fcurve_list}
