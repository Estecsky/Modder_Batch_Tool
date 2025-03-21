import bpy
import pathlib
import importlib
import os
import math
import re
import copy
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, EnumProperty, PointerProperty
from bpy_extras.io_utils import ExportHelper
from mathutils import Vector, Euler, Matrix
from .general_function import findArmatureObjFromData, showErrorMessageBox, getCollection
from .file.MHWilds.fbxskel.fbxskel_loader import load_fbxskel
from .file.MHWilds.fbxskel.fbxskel_writer import export_fbxskel, write_fbxskel
from .merge_bone import merge_weights
from ..config import __addon_name__
from ..preference.AddonPreferences import MBTAddonPreferences
import logging
logger = logging.getLogger("mhwilds_fbxskel")

def set_bone_scale(armature_name, scale_value):
    armature = bpy.data.objects.get(armature_name)
    if armature and armature.type == 'ARMATURE':
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in armature.data.edit_bones:
            bone.length = scale_value
        bpy.ops.object.mode_set(mode='OBJECT')



FemaleMesh = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]), "operators/file/MHWilds/model/MHWilds_Female.fbx")
class importMHWildsfmesh(bpy.types.Operator):
    bl_idname = "mbt.import_mhwilds_fmesh"
    bl_label = "female mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 创建一个RE_MESH集合用于放置导入的基本模型
        meshCollection = getCollection("MHWilds_Female.mesh", None, makeNew=True)
        meshCollection.color_tag = "COLOR_01"
        meshCollection["~TYPE"] = "RE_MESH_COLLECTION"
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[
            meshCollection.name]

        bpy.ops.import_scene.fbx(filepath=FemaleMesh, use_custom_props=True, force_connect_children=False)
        ArmatureObj = bpy.context.active_object
        ArmatureName = ArmatureObj.data.name
        ArmatureObj["MBT_Armature_Type"] = "MHWilds"
        bpy.ops.object.mode_set(mode='EDIT')
        # bpy.data.armatures[ArmatureName].edit_bones.active = bpy.data.armatures[ArmatureName].edit_bones["COG"]
        # bpy.context.active_bone.use_connect = False
        # bpy.data.armatures[ArmatureName].edit_bones.active = bpy.data.armatures[ArmatureName].edit_bones["root"]
        # bpy.context.active_bone.tail.z = 0.01
        for bone in ArmatureObj.data.edit_bones:
            bone.length = 0.1
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # bpy.context.scene.mbt_toolpanel.Current_MHWilds_Armature = ArmatureName
        if bpy.context.scene.mbt_toolpanel.mhwilds_convert_to_tpose == True:
            bpy.ops.mbt.mhwilds_tpose()

        self.report({'INFO'}, 'import mesh completed')
        return {'FINISHED'}


class MHWildstpose(bpy.types.Operator):
    bl_idname = "mbt.mhwilds_tpose"
    bl_label = "convert to t-pose"
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context):
    #     if bpy.context.selected_objects is not None:
    #         for obj in bpy.context.selected_objects:
    #             return obj.type == "ARMATURE"

    def execute(self, context):
        bone_list = ['L_UpperArm', 'L_Forearm', 'L_Hand', 'L_HandRZ_HJ_00', 'L_IndexF1', 'L_IndexF2', 'L_IndexF3',
                     'L_IndexF_HJ_03', 'L_IndexF_HJ_02', 'L_IndexF_HJ_00', 'L_IndexF_HJ_01', 'L_IndexF_HJ_04',
                     'L_MiddleF1', 'L_MiddleF2', 'L_MiddleF3', 'L_MiddleF_HJ_03', 'L_MiddleF_HJ_02', 'L_MiddleF_HJ_00',
                     'L_MiddleF_HJ_01', 'L_MiddleF_HJ_04', 'L_Palm', 'L_RingF1', 'L_RingF2', 'L_RingF3',
                     'L_RingF_HJ_03', 'L_RingF_HJ_02', 'L_RingF_HJ_00', 'L_RingF_HJ_01', 'L_RingF_HJ_04', 'L_PinkyF1',
                     'L_PinkyF2', 'L_PinkyF3', 'L_PinkyF_HJ_03', 'L_PinkyF_HJ_02', 'L_PinkyF_HJ_00', 'L_PinkyF_HJ_01',
                     'L_PinkyF_HJ_04', 'L_Hand_HJ_01', 'L_Hand_HJ_00', 'L_ForearmTwist_HJ_02', 'L_ForearmRY_HJ_00',
                     'L_ForearmRY_HJ_01', 'L_ForearmTwist_HJ_01', 'L_ForearmTwist_HJ_00', 'L_Elbow_HJ_00',
                     'L_UpperArmTwist_HJ_01', 'L_Triceps_HJ_00', 'L_Biceps_HJ_00', 'L_Biceps_HJ_01',
                     'L_UpperArmTwist_HJ_02', 'L_Deltoid_HJ_00', 'L_Deltoid_HJ_01', 'L_Deltoid_HJ_02', 'R_UpperArm',
                     'R_Forearm', 'R_Hand', 'R_HandRZ_HJ_00', 'R_IndexF1', 'R_IndexF2', 'R_IndexF3', 'R_IndexF_HJ_03',
                     'R_IndexF_HJ_02', 'R_IndexF_HJ_00', 'R_IndexF_HJ_01', 'R_IndexF_HJ_04', 'R_MiddleF1', 'R_MiddleF2',
                     'R_MiddleF3', 'R_MiddleF_HJ_03', 'R_MiddleF_HJ_02', 'R_MiddleF_HJ_00', 'R_MiddleF_HJ_01',
                     'R_MiddleF_HJ_04', 'R_Palm', 'R_RingF1', 'R_RingF2', 'R_RingF3', 'R_RingF_HJ_03', 'R_RingF_HJ_02',
                     'R_RingF_HJ_00', 'R_RingF_HJ_01', 'R_RingF_HJ_04', 'R_PinkyF1', 'R_PinkyF2', 'R_PinkyF3',
                     'R_PinkyF_HJ_03', 'R_PinkyF_HJ_02', 'R_PinkyF_HJ_00', 'R_PinkyF_HJ_01', 'R_PinkyF_HJ_04',
                     'R_Hand_HJ_01', 'R_Hand_HJ_00', 'R_ForearmTwist_HJ_02', 'R_ForearmRY_HJ_00', 'R_ForearmRY_HJ_01',
                     'R_ForearmTwist_HJ_01', 'R_ForearmTwist_HJ_00', 'R_Elbow_HJ_00', 'R_UpperArmTwist_HJ_01',
                     'R_Triceps_HJ_00', 'R_Biceps_HJ_00', 'R_Biceps_HJ_01', 'R_UpperArmTwist_HJ_02', 'R_Deltoid_HJ_00',
                     'R_Deltoid_HJ_01', 'R_Deltoid_HJ_02', 'L_Thigh', 'L_Knee', 'L_Shin', 'L_Foot', 'L_Instep', 'L_Toe',
                     'L_Foot_HJ_00', 'L_Calf_HJ_00', 'L_Shin_HJ_00', 'L_Shin_HJ_01', 'L_Knee_HJ_00', 'L_KneeRX_HJ_00','L_ThighTwist_HJ_00',
                     'L_Foot_HJ_00', 'L_Calf_HJ_00', 'L_Shin_HJ_00', 'L_Shin_HJ_01', 'L_Knee_HJ_00', 'L_KneeRX_HJ_00',
                     'L_ThighTwist_HJ_01', 'L_ThighTwist_HJ_02', 'R_Thigh', 'R_Knee', 'R_Shin', 'R_Foot', 'R_Instep',
                     'R_Toe', 'R_Foot_HJ_00', 'R_Calf_HJ_00', 'R_Shin_HJ_00', 'R_Shin_HJ_01', 'R_KneeRX_HJ_00',
                     'R_Knee_HJ_00', 'R_ThighTwist_HJ_00', 'R_ThighTwist_HJ_01', 'R_ThighTwist_HJ_02', 'L_ThighRZ_HJ_00', 'L_ThighRZ_HJ_01',
                     'R_ThighRZ_HJ_00', 'R_ThighRZ_HJ_01', 'L_Hip_HJ_00', 'L_Hip_HJ_01', 'R_Hip_HJ_00', 'R_Hip_HJ_01',
                     'L_ThighRX_HJ_00', 'L_ThighRX_HJ_01', 'R_ThighRX_HJ_00', 'R_ThighRX_HJ_01']

        ArmatureObj = bpy.context.active_object
        ArmatureName = ArmatureObj.data.name

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')

        for bone in bone_list:
            bpy.ops.object.select_pattern(pattern=bone, case_sensitive=False, extend=True)

        for i in range(len(bpy.context.selected_pose_bones)):
            zero = copy.deepcopy(bpy.context.selected_pose_bones[i].matrix)

            zero[0][0] = 1.0
            zero[0][1] = 0.0
            zero[0][2] = 0.0
            zero[1][0] = 0.0
            zero[1][1] = 0.0
            zero[1][2] = -1.0
            zero[2][0] = 0.0
            zero[2][1] = 1.0
            zero[2][2] = 0.0
            zero[3][0] = 0.0
            zero[3][1] = 0.0
            zero[3][2] = 0.0
            zero[3][3] = 1.0

            bpy.context.selected_pose_bones[i].matrix = zero
            bpy.context.view_layer.update()

        bpy.ops.object.mode_set(mode='OBJECT')
        if ArmatureObj.children:
            bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE', extend=True)
            bpy.ops.object.convert(target='MESH')

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.armature_apply(selected=True)
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')


        if ArmatureObj.children:
            bpy.ops.object.select_hierarchy(direction='CHILD', extend=False)
            modifier = bpy.context.active_object.modifiers.new(name="", type='ARMATURE')
            modifier.object = ArmatureObj
            bpy.ops.object.make_links_data(type='MODIFIERS')
            bpy.ops.object.select_hierarchy(direction='PARENT', extend=False)
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_hierarchy(direction='CHILD', extend=True)
        bpy.context.view_layer.objects.active = ArmatureObj

        # self.report({'INFO'}, 'conversion completed')
        return {'FINISHED'}

class MHWildsOpenDictionaryFolder(bpy.types.Operator):
    bl_label = "open dictionary folder"
    bl_description = "Open the dictionary folder in file explorer"
    bl_idname = "mbt.mhwilds_open_dictionary_folder"

    def execute(self, context):
        presetsPath = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]),"operators/file/MHWilds/bonenamelist/")
        os.startfile(presetsPath)
        return {'FINISHED'}


def Merge_MHWilds_Facial_Bones(ArmatureName, name_list):

    merge_bone_list = ['HeadAll_SCL', 'Ear_SCL', 'Head_SCL', 'C_ForeHead_LOD02', 'L_ForeHead_LOD01',
                       'R_ForeHead_LOD01', 'C_EyeBrow_LOD02', 'L_BetweenEyeBrow_LOD01', 'R_BetweenEyeBrow_LOD01',
                       'L_EyeBrow_LOD02', 'L_EyeBrow_A_LOD01', 'L_EyeBrow_B_LOD01', 'L_EyeBrow_C_LOD01',
                       'R_EyeBrow_LOD02', 'R_EyeBrow_A_LOD01', 'R_EyeBrow_B_LOD01', 'R_EyeBrow_C_LOD01',
                       'L_Eye_Master', 'L_EyeJ_LOD02', 'L_DoubleEyeLidJ_LOD02', 'L_DoubleEyeLid_LOD01',
                       'L_DoubleEyeLid_A_LOD00', 'L_DoubleEyeLid_B_LOD00', 'L_UpEyeLidJ_LOD02', 'L_UpEyeLid_LOD01',
                       'L_UpEyeLid_A_LOD00', 'L_UpEyeLid_B_LOD00', 'L_LoEyeLidJ_LOD02', 'L_LoEyeLid_LOD01',
                       'L_LoEyeLid_A_LOD00', 'L_LoEyeLid_B_LOD00', 'L_EyeBagJ_LOD02', 'L_EyeBagJ_LOD01',
                       'L_EyeBagJ_A_LOD00', 'L_EyeBagJ_B_LOD00', 'L_OuterEyeJ_LOD02', 'L_UpOuterEyeJ_LOD01',
                       'L_LoOuterEyeJ_LOD01', 'L_InnerEyeJ_LOD02', 'L_LoInnerEyeJ_LOD01', 'L_UpInnerEyeJ_LOD01',
                       'R_Eye_Master', 'R_EyeJ_LOD02', 'R_DoubleEyeLidJ_LOD02', 'R_DoubleEyeLid_LOD01',
                       'R_DoubleEyeLid_A_LOD00', 'R_DoubleEyeLid_B_LOD00', 'R_UpEyeLidJ_LOD02', 'R_UpEyeLid_LOD01',
                       'R_UpEyeLid_A_LOD00', 'R_UpEyeLid_B_LOD00', 'R_LoEyeLidJ_LOD02', 'R_LoEyeLid_LOD01',
                       'R_LoEyeLid_A_LOD00', 'R_LoEyeLid_B_LOD00', 'R_EyeBagJ_LOD02', 'R_EyeBagJ_LOD01',
                       'R_EyeBagJ_A_LOD00', 'R_EyeBagJ_B_LOD00', 'R_InnerEyeJ_LOD02', 'R_UpInnerEyeJ_LOD01',
                       'R_LoInnerEyeJ_LOD01', 'R_OuterEyeJ_LOD02', 'R_UpOuterEyeJ_LOD01', 'R_LoOuterEyeJ_LOD01',
                       'C_Nose_Master', 'C_Nose_LOD02', 'L_NoseNaso_LOD02', 'R_NoseNaso_LOD02',
                       'C_Nose_Master_LOD02', 'C_Nose_LOD01', 'L_Nose_LOD01', 'L_NoseUnder_LOD00', 'R_Nose_LOD01',
                       'R_NoseUnder_LOD00', 'L_Naso_LOD02', 'R_Naso_LOD02', 'L_CheekBone_LOD02',
                       'L_malarFat_A_LOD01', 'L_malarFat_B_LOD01', 'R_CheekBone_LOD02', 'R_malarFat_A_LOD01',
                       'R_malarFat_B_LOD01', 'L_NasoB_LOD02', 'R_NasoB_LOD02', 'L_Cheek_LOD02', 'L_Cheek_LOD01',
                       'C_Mouth_Master', 'C_upLip_LOD02', 'C_upLip_LOD01', 'C_upLip_T_LOD01', 'L_upLip_LOD02',
                       'L_upLip_LOD01', 'L_upLip_A_LOD01', 'L_upLip_A_LOD00', 'L_upLip_AT_LOD00', 'L_upLip_B_LOD01',
                       'L_upLip_B_LOD00', 'L_upLip_BT_LOD00', 'L_upLip_T_LOD01', 'R_upLip_LOD02', 'R_upLip_LOD01',
                       'R_upLip_A_LOD01', 'R_upLip_A_LOD00', 'R_upLip_AT_LOD00', 'R_upLip_B_LOD01',
                       'R_upLip_B_LOD00', 'R_upLip_BT_LOD00', 'R_upLip_T_LOD01', 'L_cornerLip_LOD02',
                       'L_cornerLip_A_LOD01', 'L_cornerLip_B_LOD01', 'L_cornerLipInner_LOD01', 'R_cornerLip_LOD02',
                       'R_cornerLip_A_LOD01', 'R_cornerLip_B_LOD01', 'R_cornerLipInner_LOD01', 'C_loLip_LOD02',
                       'C_loLip_LOD01', 'C_loLip_T_LOD01', 'L_loLip_LOD02', 'L_loLip_LOD01', 'L_loLip_A_LOD01',
                       'L_loLip_A_LOD00', 'L_loLip_AT_LOD00', 'L_loLip_B_LOD01', 'L_loLip_B_LOD00',
                       'L_loLip_BT_LOD00', 'L_loLip_T_LOD01', 'R_loLip_LOD02', 'R_loLip_LOD01', 'R_loLip_A_LOD01',
                       'R_loLip_A_LOD00', 'R_loLip_AT_LOD00', 'R_loLip_B_LOD01', 'R_loLip_B_LOD00',
                       'R_loLip_BT_LOD00', 'R_loLip_T_LOD01', 'C_Jaw_LOD02', 'C_Chin_LOD01', 'C_Chin_LOD00',
                       'L_JawLine_LOD01', 'L_JawLine_LOD00', 'R_JawLine_LOD01', 'R_JawLine_LOD00',
                       'C_TongueA_LOD01', 'C_TongueB_LOD01', 'R_TongueB_LOD00', 'C_TongueC_LOD01',
                       'L_TongueC_LOD00', 'R_TongueC_LOD00', 'L_TongueB_LOD00', 'LowerTeeth', 'C_UnderJaw_LOD02',
                       'L_UnderJaw_LOD02', 'R_UnderJaw_LOD02', 'L_Temporal_LOD01', 'R_Temporal_LOD01',
                       'L_Masseter_LOD01', 'R_Masseter_LOD01', 'R_Cheek_LOD02', 'R_Cheek_LOD01', 'HelmJoint_L_Hoho',
                       'HelmJoint_L_Era', 'HelmJoint_Mayu', 'HelmJoint_Ago', 'HelmJoint_R_Era', 'HelmJoint_R_Hoho',
                       'UpperTeeth', 'fcParam_000', 'fcParam_001', 'fcParam_002', 'fcParam_003', 'fcParam_004',
                       'fcParam_005', 'fcParam_006', 'fcParam_007', 'fcParam_008', 'fcParam_009', 'fcParam_010',
                       'fcParam_011', 'fcParam_012', 'fcParam_013', 'fcParam_014', 'fcParam_015', 'fcParam_016',
                       'fcParam_017', 'fcParam_018', 'fcParam_019', 'fcParam_020', 'fcParam_021', 'fcParam_022',
                       'fcParam_023', 'fcParam_024', 'fcParam_025', 'fcParam_026', 'fcParam_027', 'fcParam_028',
                       'fcParam_029', 'fcParam_030', 'fcParam_031', 'fcParam_032', 'fcParam_033', 'fcParam_034',
                       'fcParam_035', 'fcParam_036', 'fcParam_037', 'fcParam_038', 'fcParam_039', 'fcParam_040',
                       'fcParam_041', 'fcParam_042', 'fcParam_043', 'fcParam_044', 'fcParam_045', 'fcParam_046',
                       'fcParam_047', 'fcParam_048', 'fcParam_049', 'fcParam_050', 'fcParam_051', 'fcParam_052',
                       'fcParam_053', 'fcParam_054', 'fcParam_055', 'fcParam_056', 'fcParam_057', 'fcParam_058',
                       'fcParam_059', 'fcParam_060', 'fcParam_061', 'fcParam_062', 'fcParam_063', 'fcParam_064',
                       'fcParam_065', 'fcParam_066', 'fcParam_067', 'fcParam_068', 'fcParam_069', 'fcParam_070',
                       'fcParam_071', 'fcParam_072', 'fcParam_073', 'fcParam_074', 'fcParam_075', 'fcParam_076',
                       'fcParam_077', 'fcParam_078', 'fcParam_079', 'fcParam_080', 'fcParam_081', 'fcParam_082',
                       'fcParam_083', 'fcParam_084', 'fcParam_085', 'fcParam_086', 'fcParam_087', 'fcParam_088',
                       'fcParam_089', 'fcParam_090', 'fcParam_091', 'fcParam_092', 'fcParam_093', 'fcParam_094',
                       'fcParam_095', 'fcParam_096', 'fcParam_097', 'fcParam_098', 'fcParam_099', 'fcParam_100',
                       'fcParam_101', 'fcParam_102', 'fcParam_103', 'fcParam_104', 'fcParam_105', 'fcParam_106',
                       'fcParam_107', 'fcParam_108', 'fcParam_109', 'fcParam_110', 'fcParam_111', 'fcParam_112',
                       'fcParam_113', 'fcParam_114', 'fcParam_115', 'fcParam_116', 'fcParam_117', 'fcParam_118',
                       'fcParam_119', 'fcParam_120', 'fcParam_121', 'fcParam_122', 'fcParam_123', 'fcParam_124',
                       'fcParam_125', 'fcParam_126', 'fcParam_127', 'fcParam_128', 'fcParam_129', 'fcParam_130',
                       'fcParam_131', 'fcParam_132', 'fcParam_133', 'fcParam_134', 'fcParam_135', 'fcParam_136',
                       'fcParam_137', 'fcParam_138', 'fcParam_139', 'fcParam_140', 'fcParam_141', 'fcParam_142',
                       'fcParam_143', 'fcParam_144', 'fcParam_145', 'fcParam_146', 'fcParam_147', 'fcParam_148',
                       'fcParam_149', 'fcParam_150', 'fcParam_151', 'fcParam_152', 'fcParam_153', 'fcParam_154',
                       'fcParam_155', 'fcParam_156', 'fcParam_157', 'fcParam_158', 'fcParam_159', 'fcParam_160',
                       'fcParam_161', 'fcParam_162', 'fcParam_163', 'fcParam_164', 'fcParam_165', 'fcParam_166',
                       'fcParam_167', 'fcParam_168', 'fcParam_169', 'fcParam_170', 'fcParam_171', 'fcParam_172',
                       'fcParam_173', 'fcParam_174', 'fcParam_175', 'fcParam_176', 'fcParam_177', 'fcParam_178',
                       'fcParam_179', 'fcParam_180', 'fcParam_181', 'fcParam_182', 'fcParam_183', 'fcParam_184',
                       'fcParam_185', 'fcParam_186', 'fcParam_187', 'fcParam_188', 'fcParam_189', 'fcParam_190',
                       'fcParam_191', 'fcParam_192', 'fcParam_193', 'fcParam_194', 'fcParam_195', 'fcParam_196',
                       'fcParam_197', 'fcParam_198', 'fcParam_199', 'fcParam_200']

    bpy.ops.armature.select_all(action='DESELECT')
    for mergebone in merge_bone_list:
        if mergebone in name_list:
            bpy.data.armatures[ArmatureName].edit_bones.active = bpy.data.armatures[ArmatureName].edit_bones[
                mergebone]
            bpy.ops.object.select_pattern(pattern=mergebone, case_sensitive=False, extend=True)

    armature = bpy.context.object

    # Find which bones to work on and put their name and their parent in a list
    parenting_list = {}
    for bone in bpy.context.selected_editable_bones:
        parent = bone.parent
        while parent and parent.parent and parent in bpy.context.selected_editable_bones:
            parent = parent.parent
        if not parent:
            continue
        parenting_list[bone.name] = parent.name

    # Merge all the bones in the parenting list
    merge_weights(armature, parenting_list)
    bpy.ops.armature.select_all(action='DESELECT')


class MHWildssnapbone(bpy.types.Operator):
    bl_idname = "mbt.mhwilds_snapbone"
    bl_label = "absorb bones"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not context.selected_objects:
            return False
        # if len(context.selected_objects) != 2:
        #     return False
        # 检查所有选中的对象是否都是骨骼
        for obj in context.selected_objects:
            if obj.type != "ARMATURE":
                return False
        # 如果所有选中的对象都是骨骼，则返回True
        return True

    def execute(self, context):
        enumValue = bpy.context.scene.mbt_toolpanel.MHWildsBoneList
        file_name, file_extension = os.path.splitext(os.path.basename(enumValue))

        preset_module = importlib.import_module(f"..file.MHWilds.bonenamelist.{file_name}", package=__name__)
        fixed_name_list = preset_module.snap_bone_fixed_name_list
        rename_name_list = preset_module.rename_vg_fixed_name_list

        # 需要修正位置的骨骼
        fix_neck_bone = ['Neck_1', 'HeadRX_HJ_01', 'Neck_1_HJ_00']
        fix_spine2_bone = ['Spine_2', 'Spine_2_HJ_00']
        fix_shin_bone = ['L_Shin', 'R_Shin']
        fix_instep_bone = ['L_Instep', 'R_Instep']

        #若选中的骨架多于两个，则报错
        if len(context.selected_objects) > 2:
            showErrorMessageBox(
                "There are too many skeletons selected. Please select only two skeletons.")
        else:
            #吸附骨骼
            bpy.ops.object.mode_set(mode='OBJECT')

            #区分选中的两个骨架中哪个是外部骨架，哪个是MHWilds骨架
            armature_mhwilds = None
            armature_other = None
            for obj in bpy.context.selected_objects:
                if obj.type == 'ARMATURE' and obj.get("MBT_Armature_Type") == "MHWilds":
                    armature_mhwilds = obj
                else:
                    if armature_other is None:
                        armature_other = obj
            #判定选中的两个骨架中，是否同时存在外部骨架和游戏骨架
            both_exist = armature_mhwilds is not None and armature_other is not None
            #若不同时存在，则报错
            if not both_exist:
                showErrorMessageBox(
                    "The selected skeletons doesn't contain both the external skeleton and MHWilds skeleton.")
            else:
                #获取并保存复制骨架中所有骨骼的名称
                name_other = [bone.name for bone in armature_other.data.bones]
                #用字典中的几个骨骼名来判定选择的字典是否匹配当前选中的外部骨架
                if rename_name_list[0][0] in name_other and rename_name_list[1][0] in name_other and rename_name_list[2][0] in name_other and rename_name_list[4][0] in name_other and rename_name_list[5][0] in name_other and rename_name_list[6][0] in name_other:
                    #复制一个外部骨架对象出来用于吸附
                    armature_other_copy = armature_other.copy()
                    armature_other_copy.data = armature_other.data.copy()
                    armature_other_copy.name = f"{armature_other.name}_copy"
                    bpy.context.collection.objects.link(armature_other_copy)

                    #激活并选中MHWilds骨架，然后与复制的外部骨架合并在一起
                    bpy.context.view_layer.objects.active = armature_mhwilds
                    bones = bpy.context.active_object.data.bones
                    name_ori = [bone.name for bone in bones]
                    bpy.ops.object.select_all(action='DESELECT')
                    armature_other_copy.select_set(True)
                    armature_mhwilds.select_set(True)
                    bpy.ops.object.join()

                    #获取并保存合并后骨架中所有骨骼的名称
                    ArmatureName = bpy.context.active_object.data.name
                    bones = bpy.context.active_object.data.bones
                    name_in = [bone.name for bone in bones]

                    bpy.ops.object.mode_set(mode='EDIT')
                    for bone_name in fixed_name_list:
                        bone1_name, bone2_name = bone_name
                        #仅当字典中的两列骨骼名都存在于合并后的骨架中时才进行吸附操作
                        if bone1_name in name_in and bone2_name in name_in:
                            bpy.data.armatures[ArmatureName].edit_bones.active = bpy.data.armatures[ArmatureName].edit_bones[
                                bone1_name]
                            bpy.context.object.data.use_mirror_x = False
                            bpy.ops.armature.select_all(action='DESELECT')
                            bpy.ops.object.select_pattern(pattern=bone1_name, case_sensitive=False, extend=True)
                            bpy.ops.object.select_pattern(pattern=bone2_name, case_sensitive=False, extend=True)
                            bpy.context.area.type = 'VIEW_3D'
                            bpy.ops.view3d.snap_selected_to_active()
                            # bpy.context.area.type = 'TEXT_EDITOR'
                            bpy.ops.armature.select_all(action='DESELECT')

                    # 修正骨骼，Neck_1应当位于Head与Neck_0的中点
                    if 'Head' in name_in and 'Neck_0' in name_in:
                        bone1 = bpy.data.armatures[ArmatureName].edit_bones['Head']
                        bone2 = bpy.data.armatures[ArmatureName].edit_bones['Neck_0']

                    # if bone1 and bone2:
                        center_x = (bone1.head.x + bone2.head.x) / 2
                        center_y = (bone1.head.y + bone2.head.y) / 2
                        center_z = (bone1.head.z + bone2.head.z) / 2

                        center_point = (center_x, center_y, center_z)

                        for fnb in fix_neck_bone:
                            bone = bpy.data.armatures[ArmatureName].edit_bones[fnb]
                            original_length = (bone.tail - bone.head).length
                            direction = (bone.tail - bone.head).normalized()
                            bone.head = center_point
                            bone.tail = bone.head + direction * original_length

                    # 修正骨骼，若mmd模型骨架没有Upper Chest骨骼，则Spine_2移动到Spine_1与Neck_0的中点
                    if 'Upper Chest' not in name_in:
                        bone1 = bpy.data.armatures[ArmatureName].edit_bones['Spine_1']
                        bone2 = bpy.data.armatures[ArmatureName].edit_bones['Neck_0']

                        if bone1 and bone2:
                            center_x = (bone1.head.x + bone2.head.x) / 2
                            center_y = (bone1.head.y + bone2.head.y) / 2
                            center_z = (bone1.head.z + bone2.head.z) / 2

                            center_point = (center_x, center_y, center_z)

                        for fs2b in fix_spine2_bone:
                            bone = bpy.data.armatures[ArmatureName].edit_bones[fs2b]
                            original_length = (bone.tail - bone.head).length
                            direction = (bone.tail - bone.head).normalized()
                            bone.head = center_point
                            bone.tail = bone.head + direction * original_length

                    # 修正骨骼，Instep应位于Foot与Toe的中点，额外修正Z轴坐标与Toe平齐，即在脚底
                    if 'L_Foot' in name_in and 'L_Toe' in name_in:
                        bone1 = bpy.data.armatures[ArmatureName].edit_bones['L_Foot']
                        bone2 = bpy.data.armatures[ArmatureName].edit_bones['L_Toe']

                    # if bone1 and bone2:
                        center_x = (bone1.head.x + bone2.head.x) / 2
                        center_y = (bone1.head.y + bone2.head.y) / 2
                        center_z = bone2.head.z

                        center_point = (center_x, center_y, center_z)

                        bone = bpy.data.armatures[ArmatureName].edit_bones[fix_instep_bone[0]]
                        original_length = (bone.tail - bone.head).length
                        direction = (bone.tail - bone.head).normalized()
                        bone.head = center_point
                        bone.tail = bone.head + direction * original_length

                    if 'R_Foot' in name_in and 'R_Toe' in name_in:
                        bone1 = bpy.data.armatures[ArmatureName].edit_bones['R_Foot']
                        bone2 = bpy.data.armatures[ArmatureName].edit_bones['R_Toe']

                    # if bone1 and bone2:
                        center_x = (bone1.head.x + bone2.head.x) / 2
                        center_y = (bone1.head.y + bone2.head.y) / 2
                        center_z = bone2.head.z

                        center_point = (center_x, center_y, center_z)

                        bone = bpy.data.armatures[ArmatureName].edit_bones[fix_instep_bone[1]]
                        original_length = (bone.tail - bone.head).length
                        direction = (bone.tail - bone.head).normalized()
                        bone.head = center_point
                        bone.tail = bone.head + direction * original_length

                    # 修正骨骼，Shin应当位于Knee的正下方距离0.01的位置
                    for fshb in fix_shin_bone:
                        if fshb in name_in:
                            bone = bpy.data.armatures[ArmatureName].edit_bones[fshb]
                            bone.head.z = bone.head.z - 0.01
                            bone.tail.z = bone.tail.z - 0.01

                    for bone_name in name_in:
                        if bone_name not in name_ori:
                            bpy.data.armatures[ArmatureName].edit_bones.active = bpy.data.armatures[ArmatureName].edit_bones[bone_name]
                            bpy.ops.armature.delete()

                    if bpy.context.scene.mbt_toolpanel. mhwilds_merge_facial_bones == True:
                        Merge_MHWilds_Facial_Bones(ArmatureName, name_ori)

                    bpy.ops.object.mode_set(mode='OBJECT')
                #若选择的字典不匹配当前选中的外部骨架，则报错
                else:
                    showErrorMessageBox(
                        "The selected dictionary may not match the currently selected external skeleton. Please select the correct dictionary.")

        self.report({'INFO'}, 'adsorption completed')
        return {'FINISHED'}



class MHWildsrenamevg(bpy.types.Operator):
    bl_idname = "mbt.mhwilds_rename_vg"
    bl_label = "rename vertex group"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects is not None:
            for obj in bpy.context.selected_objects:
                return obj.type == "MESH"

    def execute(self, context):
        enumValue = bpy.context.scene.mbt_toolpanel.MHWildsBoneList
        file_name, file_extension = os.path.splitext(os.path.basename(enumValue))

        preset_module = importlib.import_module(f"..file.MHWilds.bonenamelist.{file_name}", package=__name__)
        fixed_name_list = preset_module.rename_vg_fixed_name_list

        for obj in bpy.context.selected_objects:
            v_groups = obj.vertex_groups

            if fixed_name_list[0][0] in v_groups:
                for n in fixed_name_list:
                    if n[0] in v_groups:
                        v_groups[n[0]].name = n[1]
            else:
                for n in fixed_name_list:
                    if n[0] in v_groups:
                        v_groups[n[0]].name = n[1]

        self.report({'INFO'}, 'conversion completed')
        return {'FINISHED'}

#由NSACloud编写
class RenameMeshToREFormat(bpy.types.Operator):
    bl_label = "rename meshes"
    bl_idname = "mbt.rename_mesh_to_reformat"
    bl_options = {'REGISTER', 'UNDO'}
    # bl_description = "Renames selected meshes to RE mesh naming scheme (Example: Group_0_Sub_0__Shirts_Mat)"

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects is not None:
            for obj in bpy.context.selected_objects:
                return obj.type == "MESH"

    def execute(self, context):
        groupIndexDict = dict()
        selection = context.selected_objects
        for selectedObj in selection:

            if "Group_" in selectedObj.name:
                try:
                    groupID = int(selectedObj.name.split("Group_")[1].split("_")[0])
                except:
                    pass
            else:
                print("Could not parse group ID in {selectedObj.name}, setting to 0")
                groupID = 0
            if groupID not in groupIndexDict:
                groupIndexDict[groupID] = 0
            if len(selectedObj.data.materials) > 0:
                materialName = selectedObj.data.materials[0].name.split(".", 1)[0].strip()
            else:
                materialName = "NO_MATERIAL"
            selectedObj.name = f"Group_{str(groupID)}_Sub_{str(groupIndexDict[groupID])}__{materialName}"
            groupIndexDict[groupID] += 1


        self.report({"INFO"}, "renamed completed")
        return {'FINISHED'}


def copy_bone_matrices(armature_a_name, armature_b_name):
    # 获取骨架对象
    armature_a = bpy.data.objects[armature_a_name]
    armature_b = bpy.data.objects[armature_b_name]

    # 切换到姿态模式
    bpy.context.view_layer.objects.active = armature_a
    bpy.ops.object.mode_set(mode='POSE')

    # 创建一个字典来存储骨骼名称和矩阵
    bone_matrices = {}

    # 遍历骨架 A 的所有姿态骨骼
    for bone in armature_a.pose.bones:
        # 获取骨骼的矩阵
        bone_matrix = copy.deepcopy(bone.matrix)
        bone_matrices[bone.name] = bone_matrix
        # print(f"骨骼: {bone.name}, 矩阵: {bone_matrix}")

    bpy.ops.object.mode_set(mode='OBJECT')

    # 切换到骨架 B
    bpy.context.view_layer.objects.active = armature_b
    bpy.ops.object.mode_set(mode='POSE')

    # 遍历骨架 B 的所有姿态骨骼
    for bone in armature_b.pose.bones:
        if bone.name in bone_matrices:
            # 如果骨骼名称匹配，则将矩阵赋值给该骨骼
            bone.matrix = bone_matrices[bone.name]
            bpy.context.view_layer.update()
            # print(f"将骨骼 {bone.name} 的矩阵赋值为: {bone_matrices[bone.name]}")

    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.armature_apply(selected=False)
    bpy.ops.pose.select_all(action='DESELECT')

    # 切换回对象模式
    bpy.ops.object.mode_set(mode='OBJECT')
    # print("骨架 B 的骨骼矩阵已更新。")


FemaleFbxskelMesh = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]), "operators/file/MHWilds/model/ch03_000_9000.fbxskel.7")
class Generatefbxskel(bpy.types.Operator):
    bl_idname = "mbt.generate_fbxskel"
    bl_label = "generate fbxskel"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects is not None and len(bpy.context.selected_objects) == 1:
            for obj in bpy.context.selected_objects:
                return obj.type == "ARMATURE"

    def execute(self, context):
        fixed_location_list = [
            ['L_Hand', 'L_Wep_Sub'],
            ['L_Hand', 'L_Wep'],
            ['R_Hand', 'R_Wep_Sub'],
            ['R_Hand', 'R_Wep'],
            ['R_Forearm', 'R_Shield'],
            ['L_UpperArm', 'L_UpperArm_HJ_00'],
            ['R_UpperArm', 'R_UpperArm_HJ_00'],
            ['L_UpperArm', 'L_UpperArmTwist_HJ_00'],
            ['R_UpperArm', 'R_UpperArmTwist_HJ_00'],
            ['L_UpperArm', 'L_UpperArmDouble_HJ_00'],
            ['R_UpperArm', 'R_UpperArmDouble_HJ_00'],
            ['L_Forearm', 'L_ForearmDouble_HJ_00'],
            ['R_Forearm', 'R_ForearmDouble_HJ_00'],
            ['L_Forearm', 'L_Forearm_HJ_00'],
            ['R_Forearm', 'R_Forearm_HJ_00'],
            # ['L_Thigh', 'L_ThighTwist_HJ_00'],
            # ['R_Thigh', 'R_ThighTwist_HJ_00'],
            ['L_Knee', 'L_KneeDouble_HJ_00'],
            ['R_Knee', 'R_KneeDouble_HJ_00'],
        ]
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = bpy.context.active_object
        ArmatureName0 = obj.name

        if obj.type == 'ARMATURE' and obj.get("MBT_Armature_Type") == "MHWilds":
            bpy.ops.object.select_all(action='DESELECT')

            # bpy.ops.import_scene.fbx(filepath=FemaleFbxskelMesh, use_custom_props=True, force_connect_children=False)
            ArmatureObj = load_fbxskel(FemaleFbxskelMesh, collection=None, fix_rotation=True)
            ArmatureObj.select_set(True)
            # ArmatureObj = bpy.context.active_object
            ArmatureName1 = ArmatureObj.name
            ArmatureName = ArmatureObj.data.name
            bpy.ops.object.mode_set(mode='EDIT')
            # bpy.data.armatures[ArmatureName].edit_bones.active = bpy.data.armatures[ArmatureName].edit_bones["COG"]
            # bpy.context.active_bone.use_connect = False
            for bone in ArmatureObj.data.edit_bones:
                bone.length = 0.1
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

            copy_bone_matrices(ArmatureName0, ArmatureName1)

            ArmatureName = bpy.context.active_object.data.name
            obj = bpy.context.active_object.data.bones
            bpy.ops.object.mode_set(mode='EDIT')

            for n in fixed_location_list:
                bpy.data.armatures[ArmatureName].edit_bones.active = bpy.data.armatures[ArmatureName].edit_bones[n[0]]
                bpy.context.object.data.use_mirror_x = False
                bpy.ops.armature.select_all(action='DESELECT')
                bpy.ops.object.select_pattern(pattern=n[0], case_sensitive=False, extend=True)
                bpy.ops.object.select_pattern(pattern=n[1], case_sensitive=False, extend=True)
                bpy.context.area.type = 'VIEW_3D'
                bpy.ops.view3d.snap_selected_to_active()
                # bpy.context.area.type = 'TEXT_EDITOR'
                bpy.ops.armature.select_all(action='DESELECT')
                # print(n[0],n[1])
            bpy.ops.object.mode_set(mode='OBJECT')

        else:
            showErrorMessageBox(
                        "Please select the MHWilds skeleton generated by batch tool to generate fbxskel.")


        self.report({'INFO'}, 'generation completed')
        return {'FINISHED'}


class Exportfbxskel(bpy.types.Operator, ExportHelper):
    bl_idname = "mbt.export_fbxskel"
    bl_label = 'export fbxskel'
    bl_options = {'PRESET', "REGISTER", "UNDO"}
    filename_ext = ".7"
    # filter_glob: bpy.props.StringProperty(default="*.fbxskel", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects is not None and len(bpy.context.selected_objects) == 1:
            for obj in bpy.context.selected_objects:
                return obj.type == "ARMATURE"

    def invoke(self, context, event):
        fbxskel_armature = bpy.context.active_object
        if ".fbxskel" in fbxskel_armature.name:
            self.filepath = fbxskel_armature.name.split(".fbxskel")[0] + ".fbxskel.7"
            print(self.filepath)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        beware = False
        try:
            bone_infos, beware_export = export_fbxskel(selected_objects)
            data, beware_write = write_fbxskel(bone_infos)
            with open(self.filepath, "wb") as file_out:
                file_out.write(data)
            beware = beware_export or beware_write
        except Exception as e:
            self.report({"ERROR"}, "Could not export fbxskel, reason = " + str(e))
            import traceback
            traceback.print_exc()
            return {"CANCELLED"}
        if beware:
            logger.warning("Export to " + self.filepath + " done, but warning were generated: make sure everything went correctly by checking the system console, found in Window->Toggle System Console")
            self.report({"WARNING"}, "Export done, but warning were generated: make sure everything went correctly by checking the system console, found in Window->Toggle System Console")
        else:
            logger.info("Export to " + self.filepath + " completed! ")
            self.report({"INFO"}, "export completed")
        return {"FINISHED"}