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
        box_animation.label(text="Animations", icon='GRAPH')

        # 各アニメーションアイテムをカスタム描画
        animation_list = object.blidge.animation_list
        for i, item in enumerate(animation_list):
            # アイテム全体のボックス
            item_box = box_animation.box()

            # メイン行
            main_row = item_box.row(align=True)

            # 削除ボタン（左端に配置）
            ot_remove = main_row.operator("blidge.object_animation_remove", text='', icon='X', emboss=False)
            ot_remove.item_index = i

            # アクセサー選択 (editableの場合のみ操作可)
            accessor_col = main_row.column(align=True)
            accessor_col.enabled = item.editable
            accessor_col.prop_search(item, 'accessor', scene.blidge, 'accessor_list', text='', icon="FCURVE")

            # as_uniformボタン (右端に配置、常に操作可能)
            uniform_col = main_row.column(align=True)
            if item.as_uniform:
                uniform_col.prop(item, 'as_uniform', text='', icon='SHADING_TEXTURE', emboss=True)
            else:
                uniform_col.prop(item, 'as_uniform', text='', icon='SHADING_TEXTURE', emboss=False)

            # as_uniformがTrueの場合、下にUniform設定を展開
            if item.as_uniform:
                sub_row = item_box.row(align=True)
                sub_row.label(text='', icon='BLANK1')
                sub_row.prop(item, 'name', text='Uniform Name', icon='CUBE')

            # アクセサーに紐づくF-Curveリストを表示
            if item.accessor:
                # このアクセサーに紐づくF-Curveを検索
                fcurves_with_accessor = [fc for fc in scene.blidge.fcurve_list if fc.accessor == item.accessor]

                if fcurves_with_accessor:
                    # F-Curveリストのヘッダー
                    fcurve_header_row = item_box.row(align=True)
                    fcurve_header_row.label(text='', icon='BLANK1')
                    fcurve_header_row.label(text=f'F-Curves ({len(fcurves_with_accessor)})', icon='GRAPH')

                    # 各F-Curveを表示
                    for fc in fcurves_with_accessor:
                        fcurve_row = item_box.row(align=True)
                        fcurve_row.label(text='', icon='BLANK1')
                        fcurve_row.label(text='', icon='BLANK1')
                        fcurve_row.label(text=fc.id, icon='FCURVE_SNAPSHOT')
                        fcurve_row.label(text=f'[{fc.axis.upper()}]')

        # 作成ボタン
        animation_controls = box_animation.row()
        animation_controls.operator("blidge.object_animation_create", text='Create', icon="PLUS")

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