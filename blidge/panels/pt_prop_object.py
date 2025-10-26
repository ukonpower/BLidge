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

            # 上段: 名前と削除ボタン
            header_row = item_box.row(align=True)

            # 名前フィールド (editableの場合のみ編集可)
            name_col = header_row.column(align=True)
            name_col.enabled = item.editable
            name_col.scale_x = 2.0
            name_col.prop(item, 'name', text='', emboss=item.editable, icon='ANIM_DATA')

            # 削除ボタン (editableの場合のみ有効)
            remove_col = header_row.column(align=True)
            remove_col.enabled = item.editable
            ot_remove = remove_col.operator("blidge.object_animation_remove", text='', icon='TRASH', emboss=False)
            ot_remove.item_index = i

            # 下段: アクセサーとF-Curve
            item_box.separator(factor=0.3)

            # アクセサー選択
            accessor_row = item_box.row(align=True)
            accessor_row.enabled = item.editable
            accessor_row.label(text="Accessor:", icon='FCURVE')
            accessor_row.prop_search(item, 'accessor', scene.blidge, 'accessor_list', text='', icon="NONE")

            # アクセサーに紐づくF-Curveをグリッド表示 (インデント)
            if item.accessor:
                # このアクセサーに紐づくF-Curveを検索
                fcurve_dict = {}
                for fc in scene.blidge.fcurve_list:
                    if fc.accessor == item.accessor:
                        fcurve_dict[fc.axis] = fc

                # F-Curveセクション (インデント付き)
                item_box.separator(factor=0.3)

                all_axes = ['x', 'y', 'z', 'w']

                # 各軸を縦に表示 (インデント)
                for axis in all_axes:
                    axis_row = item_box.row(align=True)
                    # 左側に空白を追加してインデント
                    axis_split = axis_row.split(factor=0.08, align=True)
                    axis_split.label(text="")  # インデント用の空白

                    # F-Curveコンテンツ
                    content_split = axis_split.split(factor=0.12, align=True)

                    # 軸ラベル
                    label_col = content_split.column(align=True)
                    label_col.alignment = 'CENTER'
                    label_col.label(text=axis.upper(), icon='DOT')

                    # F-Curveまたは追加ボタン
                    fcurve_col = content_split.column(align=True)
                    if axis in fcurve_dict:
                        # F-Curveが存在する場合
                        fc = fcurve_dict[axis]
                        fcurve_col.label(text=fc.id, icon='HANDLETYPE_AUTO_CLAMP_VEC')
                    else:
                        # 追加ボタン
                        ot_add = fcurve_col.operator("blidge.add_fcurve_to_accessor",
                                                     text='追加', icon='ADD')
                        ot_add.accessor = item.accessor
                        ot_add.target_axis = axis

            # Uniformセクション (F-Curveの下に配置)
            item_box.separator(factor=0.5)
            uniform_row = item_box.row(align=True)
            uniform_row.label(text="Use as Uniform:")
            uniform_row.prop(item, 'as_uniform', text='')

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
