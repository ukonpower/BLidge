import bpy


class BLIDGE_PT_ObjectPropertie(bpy.types.Panel):

    bl_label = 'BLidge'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        object = context.object
        layout = self.layout

        object_type = object.blidge.type

        # type

        if object.type == 'CAMERA':
            layout.label(text='Type: Camera')
        elif object.type == 'LIGHT':
            layout.label(text='Type: Light')
            column = layout.column(align=True)
            column.prop(object.blidge.param_light, 'shadow_map')
        else:
            layout.prop(object.blidge, 'type', text='Type')

        if object_type == 'cube':
            box_geometry = layout.box()
            box_geometry.label(text="Cube Geometry", icon='MESH_DATA')
            column = box_geometry.column(align=True)
            column.prop(object.blidge.param_cube, 'x')
            column.prop(object.blidge.param_cube, 'y')
            column.prop(object.blidge.param_cube, 'z')

        if object_type == 'sphere':
            box_geometry = layout.box()
            box_geometry.label(text="Sphere Geometry", icon='MESH_DATA')
            column = box_geometry.column(align=True)
            column.prop(object.blidge.param_sphere, 'radius')

        if object_type == 'plane':
            box_geometry = layout.box()
            box_geometry.label(text="Plane Geometry", icon='MESH_DATA')
            column = box_geometry.column(align=True)
            column.prop(object.blidge.param_plane, 'x')
            column.prop(object.blidge.param_plane, 'z')

        # render

        layout.prop(object.blidge, "render_virtual_mesh", text="Render virtual mesh")

        # animations

        scene = bpy.context.scene

        box_animation = layout.box()
        header_row = box_animation.row()
        header_row.label(text="Animations", icon='GRAPH')

        # 各アニメーションアイテムをカスタム描画
        animation_list = object.blidge.animation_list

        if len(animation_list) == 0:
            # リストが空の場合のメッセージ
            empty_row = box_animation.row()
            empty_row.alignment = 'CENTER'
            empty_row.label(text="アニメーションがありません", icon='INFO')

        for i, item in enumerate(animation_list):
            # 各アニメーションアイテムをボックスで囲む
            item_box = box_animation.box()

            # メイン行: アクセサー選択と削除ボタン
            main_row = item_box.row(align=True)

            # アクセサー選択 (editableの場合のみ操作可)
            accessor_col = main_row.column(align=True)
            accessor_col.enabled = item.editable
            accessor_col.scale_x = 1.5
            accessor_col.prop_search(item, 'accessor', scene.blidge, 'accessor_list', text='', icon="ANIM")

            # 削除ボタン
            remove_col = main_row.column(align=True)
            ot_remove = remove_col.operator("blidge.object_animation_remove", text='', icon='TRASH', emboss=False)
            ot_remove.item_index = i

            # アクセサーに紐づくF-Curveをグリッド表示
            if item.accessor:
                # このアクセサーに紐づくF-Curveを検索
                fcurve_dict = {}
                for fc in scene.blidge.fcurve_list:
                    if fc.accessor == item.accessor:
                        fcurve_dict[fc.axis] = fc

                # F-Curve縦積みリスト
                item_box.separator(factor=0.5)
                fcurve_label = item_box.row()
                fcurve_label.label(text="F-Curves", icon='FCURVE')

                all_axes = ['x', 'y', 'z', 'w']

                # 各軸を縦に表示
                for axis in all_axes:
                    axis_row = item_box.row(align=True)
                    axis_split = axis_row.split(factor=0.15, align=True)

                    # 軸ラベル
                    label_col = axis_split.column(align=True)
                    label_col.alignment = 'CENTER'
                    label_col.label(text=axis.upper())

                    # F-Curveまたは追加ボタン
                    content_col = axis_split.column(align=True)
                    if axis in fcurve_dict:
                        # F-Curveが存在する場合
                        fc = fcurve_dict[axis]
                        content_col.label(text=fc.id, icon='HANDLETYPE_AUTO_CLAMP_VEC')
                    else:
                        # 追加ボタン
                        ot_add = content_col.operator("blidge.add_fcurve_to_accessor",
                                                     text='追加', icon='ADD')
                        ot_add.accessor = item.accessor
                        ot_add.target_axis = axis

            # Uniformセクション (F-Curveの下に配置)
            item_box.separator(factor=0.5)
            uniform_row = item_box.row(align=True)

            if item.as_uniform:
                # Uniform名入力フィールドとリセットボタン
                uniform_row.prop(item, 'name', text='', icon='SHADING_TEXTURE', emboss=True)
                # リセットボタン (as_uniformをFalseにする)
                reset_op = uniform_row.operator("blidge.object_animation_toggle_uniform", text='', icon='X', emboss=False)
                reset_op.item_index = i
                reset_op.enable = False
            else:
                # Use as Uniformボタン
                enable_op = uniform_row.operator("blidge.object_animation_toggle_uniform", text='Use as Uniform', icon='SHADING_TEXTURE')
                enable_op.item_index = i
                enable_op.enable = True

        # 作成ボタン
        box_animation.separator()
        create_row = box_animation.row()
        create_row.scale_y = 1.2
        create_row.operator("blidge.object_animation_create", text='アニメーションを作成', icon="ADD")

        # custom properties (折りたたみ可能、animationsの外の下)
        box_custom = layout.box()

        # ヘッダー行（クリックで展開/折りたたみ）
        header_row = box_custom.row()
        icon = 'DOWNARROW_HLT' if object.blidge.custom_properties_expanded else 'RIGHTARROW'
        header_row.prop(object.blidge, "custom_properties_expanded",
                       text="Custom Properties",
                       icon=icon,
                       emboss=False)

        # 展開されている場合のみ内容を表示
        if object.blidge.custom_properties_expanded:
            # カスタムプロパティリスト表示
            custom_property_list = object.blidge.custom_property_list
            for i, item in enumerate(custom_property_list):
                item_row = box_custom.row(align=True)

                # 削除ボタン
                ot_remove = item_row.operator("blidge.remove_custom_property", text='', icon='X', emboss=False)
                ot_remove.item_index = i

                # プロパティ名
                item_row.label(text=item.name, icon='DOT')

                # 型表示
                item_row.label(text=f"({item.prop_type})")

                # 値の編集
                if item.prop_type == 'FLOAT':
                    item_row.prop(item, 'value_float', text='')
                elif item.prop_type == 'INT':
                    item_row.prop(item, 'value_int', text='')
                elif item.prop_type == 'BOOL':
                    item_row.prop(item, 'value_bool', text='')

            # 追加ボタン
            box_custom.operator("blidge.add_custom_property", text='カスタムプロパティを追加', icon="ADD")
