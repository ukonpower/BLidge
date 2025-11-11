"""UUID管理オペレーター"""

import bpy
from ..utils.uuid import ensure_unique_uuids


class BLIDGE_OT_CheckUUID(bpy.types.Operator):
    """UUIDの重複をチェックして修正"""
    bl_idname = "blidge.check_uuid"
    bl_label = "UUID重複チェック"
    bl_description = "UUIDの重複をチェックして、複製されたオブジェクトに新しいUUIDを割り当てます"

    def execute(self, context):
        fixed_count = ensure_unique_uuids(context.scene)
        self.report({'INFO'}, f"{fixed_count}個のUUIDを修正しました")
        return {'FINISHED'}


classes = [
    BLIDGE_OT_CheckUUID,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
