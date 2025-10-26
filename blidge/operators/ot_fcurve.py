import bpy
from bpy.types import Operator

from ..utils.fcurve_manager import get_fcurve_id


def get_animation_items_for_enum(self, context):
    """EnumProperty用にanimation項目を取得"""
    items = []
    for obj in context.scene.objects:
        anim_list = obj.blidge.animation_list
        for i, anim in enumerate(anim_list):
            # idがある項目のみ追加
            if anim.id:
                # 表示名: "オブジェクト名 > アニメーション名"
                display_name = f"{obj.name} > {anim.name if anim.name else anim.id[:8]}"
                items.append((anim.id, display_name, f"Object: {obj.name}"))

    if not items:
        items.append(("NONE", "アニメーション項目がありません", ""))

    return items


class BLIDGE_OT_FCurveAccessorCreate(Operator):
    bl_idname = 'blidge.fcurve_accessor_create'
    bl_label = "F-CurveをAnimation項目に紐づける"
    bl_options = {'REGISTER', 'UNDO'}

    fcurve_id: bpy.props.StringProperty(name="Curve ID", default="")
    animation_id: bpy.props.EnumProperty(
        name="Animation項目",
        description="紐づけるAnimation項目を選択",
        items=get_animation_items_for_enum
    )
    fcurve_axis: bpy.props.StringProperty(name="Curve Axis", default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "animation_id")
        layout.prop(self, "fcurve_axis", text="Axis")

    def execute(self, context):
        if self.animation_id == "NONE":
            self.report({'WARNING'}, "Animation項目を選択してください")
            return {'CANCELLED'}

        item = bpy.context.scene.blidge.fcurve_list.add()
        item.id = self.fcurve_id
        item.animation_id = self.animation_id
        item.axis = self.fcurve_axis

        return {'FINISHED'}


class BLIDGE_OT_FCurveSetAnimationID(Operator):
    """F-CurveのAnimation項目を変更"""
    bl_idname = 'blidge.fcurve_set_animation_id'
    bl_label = "Animation項目を変更"
    bl_options = {'REGISTER', 'UNDO'}

    fcurve_id: bpy.props.StringProperty(name="Curve ID", default="")
    animation_id: bpy.props.EnumProperty(
        name="Animation項目",
        description="紐づけるAnimation項目を選択",
        items=get_animation_items_for_enum
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "animation_id")

    def execute(self, context):
        if self.animation_id == "NONE":
            self.report({'WARNING'}, "Animation項目を選択してください")
            return {'CANCELLED'}

        for curveData in bpy.context.scene.blidge.fcurve_list:
            if curveData.id == self.fcurve_id:
                curveData.animation_id = self.animation_id
                break

        bpy.context.area.tag_redraw()

        return {'FINISHED'}


class BLIDGE_OT_FCurveAccessorClear(Operator):
    bl_idname = 'blidge.fcurve_asccessor_clear'
    bl_label = "Clear"
    bl_options = {'REGISTER', 'UNDO'}

    fcurve_id: bpy.props.StringProperty(name="Curve ID", default="")

    def execute(self, context):
        for index, curveData in enumerate(bpy.context.scene.blidge.fcurve_list):
            if curveData.id == self.fcurve_id:
                bpy.context.scene.blidge.fcurve_list.remove(index)
                break

        return {'FINISHED'}