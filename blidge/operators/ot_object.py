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

        # カスタムプロパティを実際にオブジェクトに追加
        if self.prop_type == 'FLOAT':
            obj[self.prop_name] = 0.0
        elif self.prop_type == 'INT':
            obj[self.prop_name] = 0
        elif self.prop_type == 'BOOL':
            obj[self.prop_name] = False

        # IDプロパティのメタデータを設定（アニメーション可能にする）
        id_props = obj.id_properties_ui(self.prop_name)
        if self.prop_type == 'FLOAT':
            id_props.update(min=-1000000.0, max=1000000.0, soft_min=-100.0, soft_max=100.0)
        elif self.prop_type == 'INT':
            id_props.update(min=-1000000, max=1000000, soft_min=-100, soft_max=100)

        # 現在のフレームでキーフレームを挿入
        current_frame = context.scene.frame_current
        try:
            obj.keyframe_insert(data_path=f'["{self.prop_name}"]', frame=current_frame)
        except Exception as e:
            self.report({'ERROR'}, f"キーフレーム挿入エラー: {str(e)}")
            return {'CANCELLED'}

        # BLidgeのカスタムプロパティリストに追加
        item = obj.blidge.custom_property_list.add()
        item.name = self.prop_name
        item.prop_type = self.prop_type

        self.report({'INFO'}, f"カスタムプロパティ '{self.prop_name}' を追加し、キーフレームを挿入しました")
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


class BLIDGE_OT_AddFCurveToAccessor(Operator):
    """アクセサーの空きスロットにF-Curveを追加"""
    bl_idname = "blidge.add_fcurve_to_accessor"
    bl_label = "F-Curveを追加"
    bl_options = {'REGISTER', 'UNDO'}

    accessor: bpy.props.StringProperty(
        name="アクセサー",
        default="",
        description="F-Curveを追加するアクセサー"
    )

    target_axis: bpy.props.StringProperty(
        name="軸",
        default="",
        description="割り当てる軸(x,y,z,w)"
    )

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
        scene = context.scene

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

        # 指定された軸が既に使用されていないか確認
        for fc in scene.blidge.fcurve_list:
            if fc.accessor == self.accessor and fc.axis == self.target_axis:
                self.report({'ERROR'}, f"軸 [{self.target_axis.upper()}] は既に使用されています")
                return {'CANCELLED'}

        # BLidgeメタデータにカスタムプロパティを追加
        try:
            custom_prop = obj.blidge.custom_property_list.add()
            custom_prop.name = self.prop_name
            custom_prop.prop_type = self.prop_type
            
            # デフォルト値を設定
            if self.prop_type == 'FLOAT':
                custom_prop.value_float = 0.0
            elif self.prop_type == 'INT':
                custom_prop.value_int = 0
            elif self.prop_type == 'BOOL':
                custom_prop.value_bool = False
                
        except Exception as e:
            self.report({'ERROR'}, f"BLidgeメタデータ追加失敗: {e}")
            return {'CANCELLED'}

        # BLidgeカスタムプロパティにキーフレームを挿入
        try:
            current_frame = scene.frame_current
            custom_prop_index = len(obj.blidge.custom_property_list) - 1
            
            # プロパティタイプに応じてdata_pathを設定
            if self.prop_type == 'FLOAT':
                data_path = f'blidge.custom_property_list[{custom_prop_index}].value_float'
            elif self.prop_type == 'INT':
                data_path = f'blidge.custom_property_list[{custom_prop_index}].value_int'
            elif self.prop_type == 'BOOL':
                data_path = f'blidge.custom_property_list[{custom_prop_index}].value_bool'
            
            obj.keyframe_insert(data_path=data_path, frame=current_frame)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"キーフレーム挿入失敗: {e}")
            return {'CANCELLED'}

        # 作成されたF-CurveからIDを取得
        fcurve_id = None
        try:
            from ..utils.fcurve_manager import get_fcurve_id
            
            # オブジェクトのアニメーションデータからF-Curveを探す
            if obj.animation_data and obj.animation_data.action:
                for fcurve in obj.animation_data.action.fcurves:
                    if fcurve.data_path == data_path:
                        fcurve_id = get_fcurve_id(fcurve, False)
                        break
            
            if not fcurve_id:
                self.report({'ERROR'}, "F-Curveが見つかりません")
                return {'CANCELLED'}
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"F-Curve ID取得失敗: {e}")
            return {'CANCELLED'}

        # F-Curveメタデータを作成
        try:
            fcurve = scene.blidge.fcurve_list.add()
            fcurve.id = fcurve_id
            fcurve.axis = self.target_axis
            fcurve.accessor = self.accessor

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"F-Curve作成失敗: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"カスタムプロパティ '{self.prop_name}' とF-Curve [{self.target_axis.upper()}] を追加しました")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"アクセサー: {self.accessor}")
        layout.label(text=f"軸: [{self.target_axis.upper()}]")
        layout.prop(self, "prop_name")
        layout.prop(self, "prop_type")