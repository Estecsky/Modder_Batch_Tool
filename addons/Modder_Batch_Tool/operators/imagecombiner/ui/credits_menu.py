import bpy


#from ..icons import get_icon_id
from .. import globs


class CreditsMenu(bpy.types.Panel):
    bl_label = 'Credits'
    bl_idname = 'SMC_PT_Credits_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI' if globs.is_blender_2_80_or_newer else 'TOOLS'
    bl_category = "Modder Batch Tool"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        
        return bool(False)

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
