import bpy

from ..utils.fcurve_manager import get_fcurve_id
from ..operators.ot_fcurve import (BLIDGE_OT_FCurveAccessorCreate, BLIDGE_OT_FCurveSetAnimationID, BLIDGE_OT_FCurveAccessorClear)

def get_fcurve_axis(fcurveId: str, axis: str):

    axisList = 'xyzw'

    if( not fcurveId.find( 'Shader NodetreeAction' ) > -1 ):
        axisList = 'xzyw'

    axisIndex = axisList.find(axis)

    if( axisIndex > -1 ):
        return 'xyzw'[axisIndex]

    return axis

def get_animation_items(scene, context):
    """すべてのオブジェクトのanimation項目を取得"""
    items = []
    for obj in scene.objects:
        for anim in obj.blidge.animation_list:
            if anim.id:
                # 表示名: "オブジェクト名 > アニメーション名"
                display_name = f"{obj.name} > {anim.name if anim.name else anim.id[:8]}"
                items.append((anim.id, display_name, f"Object: {obj.name}"))

    if not items:
        items.append(("", "アニメーション項目がありません", ""))

    return items


class BLIDGE_PT_FCurveAccessor(bpy.types.Panel):

    bl_label = 'BLidge'
    bl_category = 'F-Curve'
    bl_space_type = 'GRAPH_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):

        layout = self.layout
        layout.label(text="F-Curve to Animation")

        # アクティブなオブジェクトを取得
        active_obj = context.active_object

        for fcurve in bpy.context.selected_editable_fcurves:
            fcurve_id = get_fcurve_id(fcurve, axis=True)
            
            # F-Curve全体を囲む大きなボックス
            main_box = layout.box()
            
            # F-CurveのIDヘッダー
            header = main_box.row()
            if active_obj:
                header.label(text=f"{active_obj.name}: {fcurve_id}", icon='FCURVE')
            else:
                header.label(text=fcurve_id, icon='FCURVE')

            # このF-CurveのIDに紐づくすべてのアクセサを取得
            accessors = [curve for curve in bpy.context.scene.blidge.fcurve_list if curve.id == fcurve_id]

            # アクセサリストを表示
            if len(accessors) > 0:
                accessor_box = main_box.box()
                accessor_box.label(text="アクセサリスト", icon='LINENUMBERS_ON')
                
                for accessor in accessors:
                    # 各アクセサを表示
                    accessor_row = accessor_box.row(align=True)
                    
                    # アニメーション情報を検索
                    found_obj = None
                    found_anim = None
                    if accessor.animation_id:
                        for obj in context.scene.objects:
                            for anim in obj.blidge.animation_list:
                                if anim.id == accessor.animation_id:
                                    found_obj = obj
                                    found_anim = anim
                                    break
                            if found_obj:
                                break

                    if found_anim:
                        # アニメーション名を表示
                        info_text = f"{found_obj.name} > {found_anim.name if found_anim.name else found_anim.id[:8]}"
                        accessor_row.label(text=info_text, icon='ANIM_DATA')
                    else:
                        accessor_row.label(text="(未設定)", icon='ERROR')

                    # Axis設定
                    accessor_row.prop(accessor, 'axis', text='')

                    # 削除ボタン
                    op_delete = accessor_row.operator('blidge.fcurve_accessor_remove', text="", icon='X')
                    op_delete.fcurve_id = fcurve_id
                    op_delete.animation_id = accessor.animation_id

            # アクセサ追加ボタン
            add_row = main_box.row()
            op_add = add_row.operator('blidge.fcurve_accessor_add', text="アクセサを追加", icon='PLUS')
            op_add.fcurve_id = fcurve_id
            op_add.fcurve_axis = get_fcurve_axis(fcurve_id, 'xyzw'[fcurve.array_index])
            if active_obj:
                op_add.target_object = active_obj.name
        