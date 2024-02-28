import bpy


from ..icons import get_icon_id
from .. import globs


class CreditsMenu(bpy.types.Panel):
    bl_label = 'Credits'
    bl_idname = 'SMC_PT_Credits_Menu'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI' if globs.is_blender_2_80_or_newer else 'TOOLS'
    bl_category = "Modder's Batch Tool"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        
        return bool(False)

    def draw(self, context: bpy.types.Context) -> None:
        github = 'https://github.com/Grim-es/material-combiner-addon/issues'
        discord = 'https://discordapp.com/users/275608234595713024'
        patreon = 'https://www.patreon.com/shotariya'
        buymeacoffee = 'https://buymeacoffee.com/shotariya'

        m_col = self.layout.column()
        box = m_col.box()
        col = box.column()
        col.scale_y = 1.2
        col.label(text='Material Combiner', icon_value=get_icon_id('smc'))
        row = box.row(align=True)
        row.scale_y = 1.2
        row.alignment = 'LEFT'
        row.label(text='Created by:')
        row.label(text='shotariya', icon_value=get_icon_id('shot'))
        col = box.column(align=True)
        col.scale_y = 1.2
        col.label(text='If you have found a bug:')
        col.operator('smc.browser', text='Contact me on Discord (@shotariya)',
                     icon_value=get_icon_id('discord')).link = discord
        col.operator('smc.browser', text='Report a Bug on GitHub', icon_value=get_icon_id('github')).link = github
        col.separator()
        col.label(text='If this saved you time:')
        col.operator('smc.browser', text='Support Material Combiner', icon_value=get_icon_id('patreon')).link = patreon
        col.operator('smc.browser', text='Buy Me a Coffee', icon_value=get_icon_id('bmc')).link = buymeacoffee
