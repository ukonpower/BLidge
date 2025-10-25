"""マテリアルとユニフォームのパーサー"""

from typing import Dict, Any, Optional
import bpy


class MaterialParser:
    """マテリアルとユニフォームのパース処理を担当"""

    @staticmethod
    def parse(obj: bpy.types.Object, animation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """マテリアルとユニフォームをパースして返す

        Args:
            obj: オブジェクト
            animation_data: アニメーションデータの辞書

        Returns:
            マテリアル情報を含む辞書、またはNone
        """
        material = obj.blidge.material

        # マテリアルもユニフォームもない場合はNone
        if material.name == '' and len(material.uniform_list) == 0:
            return None

        material_data: Dict[str, Any] = {}

        # マテリアル名
        if material.name != '':
            material_data['name'] = material.name

        # ユニフォーム
        if len(material.uniform_list) > 0:
            material_data['uniforms'] = {}

            for uni in material.uniform_list:
                if uni.accessor in animation_data.get('dict', {}):
                    material_data['uniforms'][uni.name] = animation_data['dict'][uni.accessor]

        return material_data
