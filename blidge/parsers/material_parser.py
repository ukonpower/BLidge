"""ユニフォームのパーサー"""

from typing import Dict, Any, Optional
import bpy


class MaterialParser:
    """ユニフォームのパース処理を担当"""

    @staticmethod
    def parse(obj: bpy.types.Object, animation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """ユニフォームをパースして返す

        Args:
            obj: オブジェクト
            animation_data: アニメーションデータの辞書

        Returns:
            ユニフォーム情報を含む辞書、またはNone
        """
        animation_list = obj.blidge.animation_list

        # as_uniformがTrueのアニメーションのみを抽出
        uniform_items = [item for item in animation_list if item.as_uniform]

        # ユニフォームがない場合はNone
        if len(uniform_items) == 0:
            return None

        # ユニフォーム
        uniforms: Dict[str, Any] = {}

        for uni in uniform_items:
            if uni.accessor in animation_data.get('dict', {}):
                # nameが設定されている場合はそれを使用、なければaccessorを使用
                key = uni.name if uni.name else uni.accessor
                uniforms[key] = animation_data['dict'][uni.accessor]

        return uniforms if len(uniforms) > 0 else None
