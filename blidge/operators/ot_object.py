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
        print("=== BLIDGE_OT_AddFCurveToAccessor: execute開始 ===")

        obj = context.object
        scene = context.scene

        print(f"  オブジェクト: {obj.name if obj else 'None'}")
        print(f"  アクセサー: {self.accessor}")
        print(f"  ターゲット軸: {self.target_axis}")
        print(f"  プロパティ名: {self.prop_name}")
        print(f"  プロパティ型: {self.prop_type}")

        if not obj:
            print("  エラー: オブジェクトが選択されていません")
            self.report({'ERROR'}, "オブジェクトが選択されていません")
            return {'CANCELLED'}

        # プロパティ名の検証
        print("  ステップ1: プロパティ名の検証")
        if not self.prop_name or self.prop_name.strip() == "":
            print("  エラー: プロパティ名が空です")
            self.report({'ERROR'}, "プロパティ名を入力してください")
            return {'CANCELLED'}

        # 既に存在するかチェック
        print("  ステップ2: 既存プロパティのチェック")
        for item in obj.blidge.custom_property_list:
            if item.name == self.prop_name:
                print(f"  エラー: プロパティ '{self.prop_name}' は既に存在します")
                self.report({'WARNING'}, f"プロパティ '{self.prop_name}' は既に存在します")
                return {'CANCELLED'}

        # 指定された軸が既に使用されていないか確認
        print("  ステップ3: 軸の使用状況チェック")
        for fc in scene.blidge.fcurve_list:
            if fc.accessor == self.accessor and fc.axis == self.target_axis:
                print(f"  エラー: 軸 [{self.target_axis.upper()}] は既に使用されています")
                self.report({'ERROR'}, f"軸 [{self.target_axis.upper()}] は既に使用されています")
                return {'CANCELLED'}

        # カスタムプロパティを追加
        print("  ステップ4: カスタムプロパティを追加")
        try:
            custom_prop = obj.blidge.custom_property_list.add()
            print("    custom_property_list.add() 成功")
            custom_prop.name = self.prop_name
            print(f"    name設定: {custom_prop.name}")
            custom_prop.prop_type = self.prop_type
            print(f"    prop_type設定: {custom_prop.prop_type}")
        except Exception as e:
            print(f"  エラー: カスタムプロパティ追加失敗: {e}")
            self.report({'ERROR'}, f"カスタムプロパティ追加失敗: {e}")
            return {'CANCELLED'}

        # F-Curveメタデータを作成
        print("  ステップ5: F-Curveメタデータを作成")
        try:
            fcurve_id = f"{obj.name}_custom_{self.prop_name}"
            print(f"    F-Curve ID: {fcurve_id}")

            fcurve = scene.blidge.fcurve_list.add()
            print("    fcurve_list.add() 成功")

            # プロパティを設定（updateFCurveAccessorは無限再帰ガードで保護されている）
            print("    プロパティ設定開始")
            fcurve.id = fcurve_id
            print(f"    id設定: {fcurve.id}")

            fcurve.axis = self.target_axis
            print(f"    axis設定: {fcurve.axis}")

            # accessorを設定（updateコールバックが呼ばれる）
            print(f"    accessor設定開始: {self.accessor}")
            fcurve.accessor = self.accessor
            print(f"    accessor設定完了: {fcurve.accessor}")

            print("    F-Curve作成完了")
        except Exception as e:
            print(f"  エラー: F-Curve作成失敗: {e}")
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"F-Curve作成失敗: {e}")
            return {'CANCELLED'}

        print("  ステップ6: 完了")
        self.report({'INFO'}, f"カスタムプロパティ '{self.prop_name}' とF-Curve [{self.target_axis.upper()}] を追加しました")
        print("=== BLIDGE_OT_AddFCurveToAccessor: execute完了 ===")
        return {'FINISHED'}

    def invoke(self, context, event):
        print("=== BLIDGE_OT_AddFCurveToAccessor: invoke開始 ===")
        print(f"  アクセサー: {self.accessor}")
        print(f"  ターゲット軸: {self.target_axis}")
        print("  ダイアログを表示")
        result = context.window_manager.invoke_props_dialog(self)
        print(f"  invoke結果: {result}")
        return result

    def draw(self, context):
        print("=== BLIDGE_OT_AddFCurveToAccessor: draw開始 ===")
        try:
            layout = self.layout
            layout.label(text=f"アクセサー: {self.accessor}")
            layout.label(text=f"軸: [{self.target_axis.upper()}]")
            layout.prop(self, "prop_name")
            layout.prop(self, "prop_type")
            print("  draw完了")
        except Exception as e:
            print(f"  draw エラー: {e}")