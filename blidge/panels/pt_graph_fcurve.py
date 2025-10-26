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
            box = layout.box()

            # F-CurveのIDにオブジェクト名が含まれている場合、それを表示
            if active_obj:
                box.label(text=f"{active_obj.name}: {fcurve_id}", icon='FCURVE')
            else:
                box.label(text=fcurve_id, icon='FCURVE')

            curve_data = None

            for curve in bpy.context.scene.blidge.fcurve_list:
                if( curve.id == fcurve_id ):
                    curve_data = curve
                    break

            # animation_idから対応するオブジェクトとアニメーション項目を検索
            found_obj = None
            found_anim = None
            if curve_data:
                for obj in context.scene.objects:
                    for anim in obj.blidge.animation_list:
                        if anim.id == curve_data.animation_id:
                            found_obj = obj
                            found_anim = anim
                            break
                    if found_obj:
                        break

            if found_anim:
                # アニメーション項目が設定されている場合
                # アニメーション項目名と変更ボタンを横並び
                row = box.row(align=True)
                info_text = f"{found_obj.name} > {found_anim.name if found_anim.name else found_anim.id[:8]}"
                row.label(text=info_text, icon='ANIM_DATA')

                # 変更ボタン
                op_change = row.operator( BLIDGE_OT_FCurveSetAnimationID.bl_idname, text="", icon='FILE_REFRESH' )
                op_change.fcurve_id = fcurve_id

                # Axis設定
                box.prop(curve_data, 'axis', text='Axis', icon='EMPTY_ARROWS')

                # 削除ボタン
                op_delete = box.operator( BLIDGE_OT_FCurveAccessorClear.bl_idname, text="Remove", icon='CANCEL' )
                op_delete.fcurve_id = fcurve_id

            else:
                # まだ設定されていない場合 - Createボタンのみ
                op_create = box.operator( BLIDGE_OT_FCurveAccessorCreate.bl_idname, text="Create", icon='PLUS' )
                op_create.fcurve_id = fcurve_id
                op_create.fcurve_axis = get_fcurve_axis( fcurve_id, 'xyzw'[fcurve.array_index] )
                # アクティブなオブジェクトを渡す
                if active_obj:
                    op_create.target_object = active_obj.name
        