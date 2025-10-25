import bpy
from bpy.types import Operator

# --------------------
#  Custom Property
# --------------------


class BLIDGE_OT_AddCustomProperty(Operator):
    """BLidge用カスタムプロパティを追加"""
    bl_idname = "blidge.add_custom_property"
    bl_label = "カスタムプロパティを追加"
    bl_options = {'REGISTER', 'UNDO'}

    prop_name: bpy.props.StringProperty(
        name="プロパティ名",
        default="custom_property",
        description="カスタムプロパティの名前"
    )

    prop_type: bpy.props.EnumProperty(
        name="型",
        items=[
            ('FLOAT', 'Float', '浮動小数点数'),
            ('INT', 'Int', '整数'),
            ('BOOL', 'Bool', 'ブール値'),
        ],
        default='FLOAT'
    )

    def execute(self, context):
        obj = context.object

        if not obj:
            self.report({'ERROR'}, "オブジェクトが選択されていません")
            return {'CANCELLED'}

        # プロパティ名の検証
        if not self.prop_name or self.prop_name.strip() == "":
            self.report({'ERROR'}, "プロパティ名を入力してください")
            return {'CANCELLED'}

        # 既に存在するかチェック
        for item in obj.blidge.custom_property_list:
            if item.name == self.prop_name:
                self.report({'WARNING'}, f"プロパティ '{self.prop_name}' は既に存在します")
                return {'CANCELLED'}

        # BLidgeのカスタムプロパティとして追加
        item = obj.blidge.custom_property_list.add()
        item.name = self.prop_name
        item.prop_type = self.prop_type

        self.report({'INFO'}, f"カスタムプロパティ '{self.prop_name}' を追加しました")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "prop_name")
        layout.prop(self, "prop_type")


class BLIDGE_OT_RemoveCustomProperty(Operator):
    """BLidge用カスタムプロパティを削除"""
    bl_idname = "blidge.remove_custom_property"
    bl_label = "カスタムプロパティを削除"
    bl_options = {'REGISTER', 'UNDO'}

    item_index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        obj = context.object

        if not obj:
            self.report({'ERROR'}, "オブジェクトが選択されていません")
            return {'CANCELLED'}

        if self.item_index < 0 or self.item_index >= len(obj.blidge.custom_property_list):
            self.report({'ERROR'}, "無効なインデックスです")
            return {'CANCELLED'}

        # プロパティ名を取得してからリストから削除
        prop_name = obj.blidge.custom_property_list[self.item_index].name
        obj.blidge.custom_property_list.remove(self.item_index)

        self.report({'INFO'}, f"カスタムプロパティ '{prop_name}' を削除しました")
        return {'FINISHED'}


# --------------------
#  Uniforms
# --------------------


class BLIDGE_OT_ObjectUniformCreate(Operator):
    bl_idname = 'blidge.object_uniform_create'
    bl_label = "Create Animation (as Uniform)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object = context.object
        item = object.blidge.animation_list.add()
        item.as_uniform = True

        return {'FINISHED'}


class BLIDGE_OT_ObjectUniformRemove(Operator):
    bl_idname = 'blidge.object_uniform_remove'
    bl_label = "Remove Animation"
    bl_options = {'REGISTER', 'UNDO'}

    item_index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        object = context.object
        object.blidge.animation_list.remove(self.item_index)

        return {'FINISHED'}


# --------------------
#  Animation
# --------------------


class BLIDGE_OT_ObjectAnimationCreate(Operator):
    bl_idname = 'blidge.object_animation_create'
    bl_label = "Create Animation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        object = context.object
        item = object.blidge.animation_list.add()

        return {'FINISHED'}


class BLIDGE_OT_ObjectAnimationRemove(Operator):
    bl_idname = 'blidge.object_animation_remove'
    bl_label = "Remove Animation"
    bl_options = {'REGISTER', 'UNDO'}

    item_index: bpy.props.IntProperty(default=0)

    def execute(self, context):
        object = context.object
        object.blidge.animation_list.remove(self.item_index)

        return {'FINISHED'}