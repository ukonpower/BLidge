import bpy
from bpy.types import Operator
import uuid

from ..utils.fcurve_manager import get_fcurve_id


def detect_default_animation_type(fcurve_id):
    """F-Curve IDからデフォルトアニメーションタイプを検出"""
    if 'location' in fcurve_id.lower():
        return 'position'
    elif 'rotation_euler' in fcurve_id.lower():
        return 'rotation'
    elif 'scale' in fcurve_id.lower():
        return 'scale'
    elif 'hide_render' in fcurve_id.lower():
        return 'hide'
    return None


def get_or_create_default_animation(obj, anim_type):
    """オブジェクトのデフォルトアニメーション項目を取得または作成

    Args:
        obj: Blenderオブジェクト
        anim_type: 'position', 'rotation', 'scale', 'hide'

    Returns:
        animation項目のID
    """
    # 既存のanimation項目を検索(editableがFalseでnameが一致するもの)
    for anim in obj.blidge.animation_list:
        if not anim.editable and anim.name == anim_type:
            return anim.id

    # 存在しない場合は新規作成
    anim = obj.blidge.animation_list.add()
    anim.id = str(uuid.uuid4())
    anim.name = anim_type
    anim.editable = False

    # 優先順位に基づいて適切な位置に挿入
    # position, rotation, scale, hideの順
    priority_order = ['position', 'rotation', 'scale', 'hide']
    target_priority = priority_order.index(anim_type) if anim_type in priority_order else len(priority_order)

    # 新しく追加したアイテムのインデックス
    new_index = len(obj.blidge.animation_list) - 1

    # 挿入位置を見つける
    insert_position = 0
    for i, existing_anim in enumerate(obj.blidge.animation_list):
        if existing_anim == anim:
            continue
        if not existing_anim.editable and existing_anim.name in priority_order:
            existing_priority = priority_order.index(existing_anim.name)
            if existing_priority < target_priority:
                insert_position = i + 1

    # 適切な位置に移動
    if insert_position != new_index:
        obj.blidge.animation_list.move(new_index, insert_position)

    return anim.id


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
    target_object: bpy.props.StringProperty(name="Target Object", default="")

    def invoke(self, context, event):
        # デフォルトアニメーションタイプを検出
        anim_type = detect_default_animation_type(self.fcurve_id)

        if anim_type and self.target_object:
            # position/rotation/scale/hideの場合は自動作成して即実行
            obj = context.scene.objects.get(self.target_object)
            if obj:
                self.animation_id = get_or_create_default_animation(obj, anim_type)
                return self.execute(context)

        # それ以外の場合はダイアログを表示
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


class BLIDGE_OT_FCurveAccessorAdd(Operator):
	"""F-Curveに新しいアクセサを追加"""
	bl_idname = 'blidge.fcurve_accessor_add'
	bl_label = "アクセサを追加"
	bl_options = {'REGISTER', 'UNDO'}

	fcurve_id: bpy.props.StringProperty(name="Curve ID", default="")
	animation_id: bpy.props.EnumProperty(
		name="Animation項目",
		description="紐づけるAnimation項目を選択",
		items=get_animation_items_for_enum
	)
	fcurve_axis: bpy.props.StringProperty(name="Curve Axis", default="")
	target_object: bpy.props.StringProperty(name="Target Object", default="")

	def invoke(self, context, event):
		# 既にこのF-Curveにアクセサが設定されているかチェック
		existing_accessors = [curve for curve in context.scene.blidge.fcurve_list if curve.id == self.fcurve_id]
		
		if len(existing_accessors) == 0:
			# まだ設定されていない場合
			# デフォルトアニメーションタイプを検出
			anim_type = detect_default_animation_type(self.fcurve_id)
			
			if anim_type and self.target_object:
				obj = context.scene.objects.get(self.target_object)
				if obj:
					# position/rotation/scale/hideの場合は自動作成して即実行
					# EnumPropertyを経由せずに直接animation_idを作成して実行
					created_id = get_or_create_default_animation(obj, anim_type)
					
					# fcurve_listに新しいエントリを追加
					item = context.scene.blidge.fcurve_list.add()
					item.id = self.fcurve_id
					item.animation_id = created_id
					item.axis = self.fcurve_axis
					
					return {'FINISHED'}

		# 既に設定がある場合、または通常の場合はダイアログを表示
		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "animation_id")
		layout.prop(self, "fcurve_axis", text="Axis")

	def execute(self, context):
		if self.animation_id == "NONE":
			self.report({'WARNING'}, "Animation項目を選択してください")
			return {'CANCELLED'}

		# fcurve_listに新しいエントリを追加
		item = context.scene.blidge.fcurve_list.add()
		item.id = self.fcurve_id
		item.animation_id = self.animation_id
		item.axis = self.fcurve_axis

		return {'FINISHED'}


class BLIDGE_OT_FCurveAccessorRemove(Operator):
	"""F-Curveからアクセサを削除"""
	bl_idname = 'blidge.fcurve_accessor_remove'
	bl_label = "アクセサを削除"
	bl_options = {'REGISTER', 'UNDO'}

	fcurve_id: bpy.props.StringProperty(name="Curve ID", default="")
	animation_id: bpy.props.StringProperty(name="Animation ID", default="")

	def execute(self, context):
		# fcurve_listから該当するエントリを削除
		# 同じidとanimation_idを持つ最初の項目を削除
		for index, curve in enumerate(context.scene.blidge.fcurve_list):
			if curve.id == self.fcurve_id and curve.animation_id == self.animation_id:
				context.scene.blidge.fcurve_list.remove(index)
				break

		return {'FINISHED'}


class BLIDGE_OT_FCurveAccessorChange(Operator):
	"""F-Curveのアクセサのアニメーション項目を変更"""
	bl_idname = 'blidge.fcurve_accessor_change'
	bl_label = "アニメーション項目を変更"
	bl_options = {'REGISTER', 'UNDO'}

	fcurve_id: bpy.props.StringProperty(name="Curve ID", default="")
	old_animation_id: bpy.props.StringProperty(name="Old Animation ID", default="")
	new_animation_id: bpy.props.EnumProperty(
		name="Animation項目",
		description="紐づけるAnimation項目を選択",
		items=get_animation_items_for_enum
	)

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "new_animation_id", text="新しいAnimation項目")

	def execute(self, context):
		if self.new_animation_id == "NONE":
			self.report({'WARNING'}, "Animation項目を選択してください")
			return {'CANCELLED'}

		# fcurve_listから該当するエントリを探して変更
		for curve in context.scene.blidge.fcurve_list:
			if curve.id == self.fcurve_id and curve.animation_id == self.old_animation_id:
				curve.animation_id = self.new_animation_id
				break

		context.area.tag_redraw()

		return {'FINISHED'}
