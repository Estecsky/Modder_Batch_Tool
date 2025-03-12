import bpy
import os
from ..config import __addon_name__
from ..operators.imagecombiner import globs
from ..operators.imagecombiner.icons import get_icon_id
from ....common.i18n.i18n import i18n
from ....common.types.framework import reg_order
from ..operators.imagecombiner.type_annotations import Scene

class BasePanel(object):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Modder Batch Tool"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return context is not None

@reg_order(0)
class MBTShowPanel(bpy.types.Panel):
    bl_label = "Show Panel Settings"
    bl_idname = "OBJECT_PT_MBT_ShowPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Modder Batch Tool"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context: bpy.types.Context):
        return context is not None

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        scene = context.scene
        mbt_toolpanel = context.scene.mbt_toolpanel
        row.prop(mbt_toolpanel, "show_mhwilds")

@reg_order(1)
class UniversalFunction(bpy.types.Panel):
    bl_label = "Universal Function"
    bl_idname = "OBJECT_PT_MBT_UniversalFunction"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Modder Batch Tool"

    @classmethod
    def poll(self, context: bpy.types.Context):
        return context is not None

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("mbt.separate_by_materials", icon="OUTLINER_DATA_MESH")

        row = layout.row()
        row.operator("mbt.clean_zero_vg", icon="OUTLINER_DATA_MESH")
        row = layout.row()
        row.operator("mbt.remove_shapekeys", icon="OUTLINER_DATA_MESH")

        layout.label(text="Batch delete unnecessary UVs and unify UV names")
        row = layout.row()
        row.operator("mbt.unify_uvs", icon="OUTLINER_DATA_MESH")


@reg_order(2)
class MBTMHWilds(bpy.types.Panel):
    global PCOLL
    bl_label = "MHWilds"
    bl_idname = "OBJECT_PT_MBT_MHWilds"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Modder Batch Tool"
    # bl_context = "objectmode"
    # bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        mbt_toolpanel = context.scene.mbt_toolpanel
        return bool(mbt_toolpanel.show_mhwilds)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mbt_toolpanel = context.scene.mbt_toolpanel
        # row = layout.row()
        # row.scale_y = 1.2
        # row.label(text="Make sure you have installed <RE Mesh Editor> plugin", icon="INFO")

        layout.label(text="Import MHWilds basic mesh")
        row = layout.row()
        row.operator("mbt.import_mhwilds_fmesh", icon="OUTLINER_OB_MESH")
        # row.operator("tool.importmhwildsmmesh", icon="OUTLINER_OB_MESH")

        layout.label(text="Convert to t-pose")
        row = layout.row()
        row.operator("mbt.mhwilds_tpose", icon="OUTLINER_OB_ARMATURE")
        row = layout.row()

        layout.label(text="Batch absorb bones (only support t-pose)")
        row = layout.row()
        row.scale_y = 1.2
        row.label(text="Make sure you select armature below first and then the game armature in the object mode",
                  icon="ERROR")
        row = layout.row()
        layout.prop(mbt_toolpanel, "MHWildsBoneList")
        layout.operator("mbt.mhwilds_snapbone", icon="OUTLINER_OB_ARMATURE")

        # layout.label(text="Batch rename vertex groups")
        row = layout.row()
        row.operator("mbt.mhwilds_rename_vg", icon="OUTLINER_DATA_MESH")

        layout.label(text="Batch normalize and limit weight to 6wt")
        row = layout.row()
        row.operator("mbt.normalize_limit_6wt_vg", icon="OUTLINER_DATA_MESH")

        layout.label(text="Batch split seam edge")
        row = layout.row()
        row.operator("mbt.split_seam_edge", icon="OUTLINER_DATA_MESH")

        layout.label(text="Batch rename meshes to re format")
        row = layout.row()
        row.operator("mbt.rename_mesh_to_reformat", icon="OUTLINER_DATA_MESH")

        layout.label(text="Generate or export fbxskel")
        row = layout.row()
        row.operator("mbt.generate_fbxskel", icon="OUTLINER_OB_ARMATURE")
        row.operator("mbt.export_fbxskel", icon="OUTLINER_OB_ARMATURE")



DIR_PATH = os.path.dirname(os.path.split(os.path.abspath(__file__))[0])
ICONS_PATH = os.path.join(DIR_PATH, "icons")
PCOLL = None
preview_collections = {}
@reg_order(3)
class MBTCredits(bpy.types.Panel):
    global PCOLL
    bl_label = "Credits"
    bl_idname = "OBJECT_PT_MBT_credits"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Modder Batch Tool"
    # bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context: bpy.types.Context):
        return context is not None

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=False)
        row.label(text = f"Modder Batch Tool", icon_value=preview_collections["icons"]["korone"].icon_id)
        col.separator()
        row = col.row(align=False) ; row.scale_y = 0.75
        row.label(text = "Modified by:")
        row = col.row(align=False) ; row.scale_y = 0.75
        row.label(text = "Korone")
        col.separator()
        row = col.row(align=False) ; row.scale_y = 0.75
        row.label(text = "Special thanks:")
        row = col.row(align=False) ; row.scale_y = 0.75
        row.label(text = "ZJCS, Dytser, Shotariya, NSACloud")
        col.separator()
        row = col.row() ; row.scale_y = 1.1
        button = row.operator("mtb.github_website", icon_value=preview_collections["icons"]["github"].icon_id)
        row = col.row() ; row.scale_y = 1.1
        button = row.operator("mtb.bilibili_website", icon_value=preview_collections["icons"]["bilibili"].icon_id)
        row = col.row() ; row.scale_y = 1.1
        button = row.operator("mtb.qq_website", icon_value=preview_collections["icons"]["qq"].icon_id)
        row = col.row() ; row.scale_y = 1.1
        button = row.operator("mtb.caimogu_website", icon_value=preview_collections["icons"]["caimogu"].icon_id)


