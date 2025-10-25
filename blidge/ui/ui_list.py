import bpy
from bpy.types import (UIList)

from ..utils.fcurve_manager import (get_fcurve_id, get_fcurve_prop)

# updateFCurveAccessorの再帰呼び出しを防ぐためのフラグ
_updating_fcurve_accessor = False

def updateFCurveAccessor(self,context):
    global _updating_fcurve_accessor

    # 既に更新中の場合は何もしない（無限再帰を防ぐ）
    if _updating_fcurve_accessor:
        return

    _updating_fcurve_accessor = True
    try:
        context.scene.blidge.accessor_list.clear()
        for item in context.scene.blidge.fcurve_list:
            accessor = item.accessor
            if ( accessor in context.scene.blidge.accessor_list ) == False:
                new_item = context.scene.blidge.accessor_list.add()
                new_item.accessor = item.accessor
    finally:
        _updating_fcurve_accessor = False

    # default animation

    table = [
        { "target": "_hide_render" },
        { "target": "_scale" },
        { "target": "_rotation_euler" },
        { "target": "_location" },
    ]

    for obj in context.scene.objects:
        blidge = obj.blidge
        animation_list = blidge.animation_list

        if obj.animation_data and obj.animation_data.action:
            for t in table:
                # 既存のアイテムを検索して削除
                for i in range(len(animation_list) - 1, -1, -1):
                    if animation_list[i].accessor.find(t["target"]) > -1:
                        animation_list.remove(i)

                # 新しいアイテムを追加
                for fcurve in obj.animation_data.action.fcurves:
                    fcurve_prop = get_fcurve_prop(get_fcurve_id(fcurve, True))
                    if fcurve_prop != None and fcurve_prop.accessor.find(t["target"]) > -1:
                        # 既に同じアクセサーが存在するかチェック
                        exists = False
                        for existing in animation_list:
                            if existing.accessor == fcurve_prop.accessor:
                                exists = True
                                break

                        if not exists:
                            item = animation_list.add()
                            item.accessor = fcurve_prop.accessor
                            item.editable = False
                            animation_list.move(len(animation_list) - 1, 0)
                            break

    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                    


class BLIDGE_UL_Uniforms(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.enabled = item.editable
        if item.as_uniform:
            row.prop(item, 'name', text='', emboss=False, icon='CUBE')
        row.prop_search(item, 'accessor', context.scene.blidge, 'accessor_list', text='', icon="FCURVE")
        row.prop(item, 'as_uniform', text='')
        ot_remove = row.operator( "blidge.object_animation_remove", text='', icon='CANCEL', emboss=False )
        ot_remove.item_index = index

class BLIDGE_UL_Animations(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.enabled = item.editable
        if item.as_uniform:
            row.prop(item, 'name', text='', emboss=False, icon='CUBE')
        row.prop_search(item, 'accessor', context.scene.blidge, 'accessor_list', text='', icon="FCURVE")
        row.prop(item, 'as_uniform', text='')
        ot_remove = row.operator( "blidge.object_animation_remove", text='', icon='CANCEL', emboss=False )
        ot_remove.item_index = index


    