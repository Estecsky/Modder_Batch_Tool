import bpy

from .. import addon_updater_ops
from .. import globs


class UpdateMenu(bpy.types.Panel):
    bl_label = 'Updates'
    bl_idname = 'SMC_PT_Update_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI' if globs.is_blender_2_80_or_newer else 'TOOLS'
    bl_category = "Modder's Batch Tool"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        
        return bool(False)

    def draw(self, context: bpy.types.Context) -> None:
        addon_updater_ops.update_settings_ui(self, context)
