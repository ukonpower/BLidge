import bpy
from bpy.types import Operator
import uuid

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

        # BLidgeのカスタムプロパティリストに追加
        item = obj.blidge.custom_property_list.add()
        item.name = self.prop_name
        item.prop_type = self.prop_type

        # デフォルト値を設定
        if self.prop_type == 'FLOAT':
            item.value_float = 0.0
        elif self.prop_type == 'INT':
            item.value_int = 0
        elif self.prop_type == 'BOOL':
            item.value_bool = False

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
        scene = context.scene

        if not obj:
            self.report({'ERROR'}, "オブジェクトが選択されていません")
            return {'CANCELLED'}

        if self.item_index < 0 or self.item_index >= len(obj.blidge.custom_property_list):
            self.report({'ERROR'}, "無効なインデックスです")
            return {'CANCELLED'}

        # プロパティ名を取得
        prop_name = obj.blidge.custom_property_list[self.item_index].name
        prop_type = obj.blidge.custom_property_list[self.item_index].prop_type
        
        # data_pathを構築
        if prop_type == 'FLOAT':
            data_path = f'blidge.custom_property_list[{self.item_index}].value_float'
        elif prop_type == 'INT':
            data_path = f'blidge.custom_property_list[{self.item_index}].value_int'
        elif prop_type == 'BOOL':
            data_path = f'blidge.custom_property_list[{self.item_index}].value_bool'
        
        # 関連するF-Curveを削除
        if obj.animation_data and obj.animation_data.action:
            fcurves_to_remove = []
            for fcurve in obj.animation_data.action.fcurves:
                if fcurve.data_path == data_path:
                    fcurves_to_remove.append(fcurve)
            
            for fcurve in fcurves_to_remove:
                obj.animation_data.action.fcurves.remove(fcurve)
        
        # 関連するfcurve_listエントリを削除
        # (このカスタムプロパティのF-Curveに紐づくアクセサーを削除)
        from ..utils.fcurve_manager import get_fcurve_id
        fcurve_ids_to_remove = []
        
        # まず削除対象のF-Curve IDを特定
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                if fcurve.data_path == data_path:
                    fcurve_id = get_fcurve_id(fcurve, False)
                    fcurve_ids_to_remove.append(fcurve_id)
        
        # fcurve_listから該当するエントリを削除
        indices_to_remove = []
        for i, fc in enumerate(scene.blidge.fcurve_list):
            if fc.id in fcurve_ids_to_remove:
                indices_to_remove.append(i)
        
        # 逆順で削除(インデックスのずれを防ぐ)
        for i in sorted(indices_to_remove, reverse=True):
            scene.blidge.fcurve_list.remove(i)
        
        # リストから削除
        obj.blidge.custom_property_list.remove(self.item_index)

        # 削除したインデックス以降のF-Curveのdata_pathを更新
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                # カスタムプロパティのdata_pathかチェック
                if fcurve.data_path.startswith('blidge.custom_property_list['):
                    # インデックスを抽出
                    import re
                    match = re.search(r'blidge\.custom_property_list\[(\d+)\]\.value_(float|int|bool)', fcurve.data_path)
                    if match:
                        current_index = int(match.group(1))
                        value_type = match.group(2)

                        # 削除したインデックスより大きい場合、-1する
                        if current_index > self.item_index:
                            new_index = current_index - 1
                            fcurve.data_path = f'blidge.custom_property_list[{new_index}].value_{value_type}'

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
        item.id = str(uuid.uuid4())
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
        item.id = str(uuid.uuid4())

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


class BLIDGE_OT_ObjectAnimationToggleUniform(Operator):
    bl_idname = 'blidge.object_animation_toggle_uniform'
    bl_label = "Toggle Uniform"
    bl_options = {'REGISTER', 'UNDO'}

    item_index: bpy.props.IntProperty(default=0)
    enable: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        object = context.object

        if self.item_index < 0 or self.item_index >= len(object.blidge.animation_list):
            return {'CANCELLED'}

        item = object.blidge.animation_list[self.item_index]
        item.as_uniform = self.enable

        return {'FINISHED'}


class BLIDGE_OT_AddFCurveToAnimation(Operator):
    """アニメーション項目にF-Curveを追加"""
    bl_idname = "blidge.add_fcurve_to_animation"
    bl_label = "F-Curveを追加"
    bl_options = {'REGISTER', 'UNDO'}

    animation_id: bpy.props.StringProperty(
        name="アニメーションID",
        default="",
        description="F-Curveを追加するアニメーション項目のID"
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
            if fc.animation_id == self.animation_id and fc.axis == self.target_axis:
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
                        fcurve_id = get_fcurve_id(fcurve, axis=True)
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
            fcurve.animation_id = self.animation_id

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"F-Curve作成失敗: {e}")
            return {'CANCELLED'}

        # UIを更新
        context.area.tag_redraw()

        self.report({'INFO'}, f"カスタムプロパティ '{self.prop_name}' とF-Curve [{self.target_axis.upper()}] を追加しました")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text=f"軸: [{self.target_axis.upper()}]")
        layout.prop(self, "prop_name")
        layout.prop(self, "prop_type")