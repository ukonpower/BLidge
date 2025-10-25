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
        uniform_list = obj.blidge.uniform_list

        # ユニフォームがない場合はNone
        if len(uniform_list) == 0:
            return None

        # ユニフォーム
        uniforms: Dict[str, Any] = {}

        for uni in uniform_list:
            if uni.accessor in animation_data.get('dict', {}):
                uniforms[uni.accessor] = animation_data['dict'][uni.accessor]

        return {'uniforms': uniforms} if len(uniforms) > 0 else None
