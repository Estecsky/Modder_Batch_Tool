import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, EnumProperty, PointerProperty
import math
from ..operators.rw_presets import reloadPresets


class MBTToolPanelPG(bpy.types.PropertyGroup):

    def getMHWildsBoneList(self, context):
        return reloadPresets("MHWilds")

    MHWildsBoneList: EnumProperty(
        name="",
        description="",
        items=getMHWildsBoneList
    )

    show_mhwilds: BoolProperty(
        name="MHWilds",
        description="Show MHWilds panel",
        default=True
    )

    mhwilds_merge_facial_bones: BoolProperty(
        name="merge facial bones",
        description="",
        default=True
    )

    mhwilds_convert_to_tpose: BoolProperty(
        name="convert to t-pose",
        description="",
        default=True
    )

    # Current_MHWilds_Armature: StringProperty(
    #     name="",
    #     description="",
    #     default=""
    # )
