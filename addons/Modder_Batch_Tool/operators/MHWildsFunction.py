import bpy
import pathlib
import importlib
import os
import math
import re
import copy
from mathutils import Vector, Euler, Matrix

from ..config import __addon_name__
from ..preference.AddonPreferences import MBTAddonPreferences


def set_bone_scale(armature_name, scale_value):
    armature = bpy.data.objects.get(armature_name)
    if armature and armature.type == 'ARMATURE':
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in armature.data.edit_bones:
            bone.length = scale_value
        bpy.ops.object.mode_set(mode='OBJECT')

FemaleMesh = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]), "operators/file/MHWilds/MHWilds_Female.fbx")
class importMHWildsfmesh(bpy.types.Operator):
    bl_idname = "mbt.import_mhwilds_fmesh"
    bl_label = "female mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.import_scene.fbx(filepath=FemaleMesh, use_custom_props=True, force_connect_children=False)
        ArmatureObj = bpy.context.active_object
        ArmatureName = ArmatureObj.data.name
        bpy.ops.object.mode_set(mode='EDIT')
        # bpy.data.armatures[ArmatureName].edit_bones.active = bpy.data.armatures[ArmatureName].edit_bones["COG"]
        # bpy.context.active_bone.use_connect = False
        # bpy.data.armatures[ArmatureName].edit_bones.active = bpy.data.armatures[ArmatureName].edit_bones["root"]
        # bpy.context.active_bone.tail.z = 0.01
        for bone in ArmatureObj.data.edit_bones:
            bone.length = 0.1
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        self.report({'INFO'}, 'Import mesh completed')
        return {'FINISHED'}


class MHWildstpose(bpy.types.Operator):
    bl_idname = "mbt.mhwilds_tpose"
    bl_label = "convert to t-pose"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects is not None:
            for obj in bpy.context.selected_objects:
                return obj.type == "ARMATURE"

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
                     'L_Foot_HJ_00', 'L_Calf_HJ_00', 'L_Shin_HJ_00', 'L_Shin_HJ_01', 'L_Knee_HJ_00', 'L_KneeRX_HJ_00',
                     'L_ThighTwist_HJ_01', 'L_ThighTwist_HJ_02', 'R_Thigh', 'R_Knee', 'R_Shin', 'R_Foot', 'R_Instep',
                     'R_Toe', 'R_Foot_HJ_00', 'R_Calf_HJ_00', 'R_Shin_HJ_00', 'R_Shin_HJ_01', 'R_KneeRX_HJ_00',
                     'R_Knee_HJ_00', 'R_ThighTwist_HJ_01', 'R_ThighTwist_HJ_02', 'L_ThighRZ_HJ_00', 'L_ThighRZ_HJ_01',
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

        self.report({'INFO'}, 'conversion completed')
        return {'FINISHED'}


class MHWildssnapbone(bpy.types.Operator):
    bl_idname = "mbt.mhwilds_snapbone"
    bl_label = "absorb bones"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects is not None:
            for obj in bpy.context.selected_objects:
                return obj.type == "ARMATURE"

    def execute(self, context):
        enumValue = bpy.context.scene.mbt_toolpanel.MHWildsBoneList
        file_name, file_extension = os.path.splitext(os.path.basename(enumValue))

        preset_module = importlib.import_module(f"..file.MHWilds.bonenamelist.{file_name}", package=__name__)
        fixed_name_list = preset_module.snap_bone_fixed_name_list

        # 需要修正位置的骨骼
        fix_neck_bone = ['Neck_1', 'HeadRX_HJ_01', 'Neck_1_HJ_00']
        fix_spine2_bone = ['Spine_2', 'Spine_2_HJ_00']
        fix_shin_bone = ['L_Shin', 'R_Shin']
        fix_instep_bone = ['L_Instep', 'R_Instep']

        # 吸附骨骼
        obj0 = bpy.context.active_object.data.bones
        name_save = []
        for i in range(len(obj0)):
            name_save.append(obj0[i].name)

        bpy.ops.object.join()
        ArmatureName = bpy.context.active_object.data.name
        obj = bpy.context.active_object.data.bones

        name_in = []
        for i in range(len(obj)):
            name_in.append(obj[i].name)

        if fixed_name_list[0][0] in name_in:
            for n in fixed_name_list:
                if n[0] not in name_in:
                    continue
                elif n[1] not in name_in:
                    continue
                else:
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.data.armatures[ArmatureName].edit_bones.active = bpy.data.armatures[ArmatureName].edit_bones[
                        n[0]]
                    bpy.context.object.data.use_mirror_x = False
                    bpy.ops.armature.select_all(action='DESELECT')
                    bpy.ops.object.select_pattern(pattern=n[0], case_sensitive=False, extend=True)
                    bpy.ops.object.select_pattern(pattern=n[1], case_sensitive=False, extend=True)
                    bpy.context.area.type = 'VIEW_3D'
                    bpy.ops.view3d.snap_selected_to_active()
                    # bpy.context.area.type = 'TEXT_EDITOR'
                    bpy.ops.armature.select_all(action='DESELECT')

        # 修正骨骼，Neck_1应当位于Head与Neck_0的中点
        bone1 = bpy.data.armatures[ArmatureName].edit_bones['Head']
        bone2 = bpy.data.armatures[ArmatureName].edit_bones['Neck_0']

        if bone1 and bone2:
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

        # 修正骨骼，若mmd模型骨架不没有Upper Chest骨骼，则Spine_2移动到Spine_1与Neck_0的中点
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
        bone1 = bpy.data.armatures[ArmatureName].edit_bones['L_Foot']
        bone2 = bpy.data.armatures[ArmatureName].edit_bones['L_Toe']

        if bone1 and bone2:
            center_x = (bone1.head.x + bone2.head.x) / 2
            center_y = (bone1.head.y + bone2.head.y) / 2
            center_z = bone2.head.z

            center_point = (center_x, center_y, center_z)

        bone = bpy.data.armatures[ArmatureName].edit_bones[fix_instep_bone[0]]
        original_length = (bone.tail - bone.head).length
        direction = (bone.tail - bone.head).normalized()
        bone.head = center_point
        bone.tail = bone.head + direction * original_length

        bone1 = bpy.data.armatures[ArmatureName].edit_bones['R_Foot']
        bone2 = bpy.data.armatures[ArmatureName].edit_bones['R_Toe']

        if bone1 and bone2:
            center_x = (bone1.head.x + bone2.head.x) / 2
            center_y = (bone1.head.y + bone2.head.y) / 2
            center_z = bone2.head.z

            center_point = (center_x, center_y, center_z)

        bone = bpy.data.armatures[ArmatureName].edit_bones[fix_instep_bone[1]]
        original_length = (bone.tail - bone.head).length
        direction = (bone.tail - bone.head).normalized()
        bone.head = center_point
        bone.tail = bone.head + direction * original_length

        # 修正骨骼，Shin应当位于Knee的正下方距离0.03的位置
        for fshb in fix_shin_bone:
            bone = bpy.data.armatures[ArmatureName].edit_bones[fshb]
            bone.head.z = bone.head.z - 0.03
            bone.tail.z = bone.tail.z - 0.03

        for i in range(len(obj)):
            if name_in[i] in name_save:
                continue
            else:
                bpy.data.armatures[ArmatureName].edit_bones.active = bpy.data.armatures[ArmatureName].edit_bones[
                    name_in[i]]
                bpy.ops.armature.delete()

        bpy.ops.object.mode_set(mode='OBJECT')

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


FemaleFbxskelMesh = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]), "operators/file/MHWilds/MHWilds_Female_Fbxskel.fbx")
class MHWildsfbxskel(bpy.types.Operator):
    bl_idname = "mbt.mhwilds_fbxskel"
    bl_label = "generate fbxskel"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects is not None:
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
            ['L_Thigh', 'L_ThighTwist_HJ_00'],
            ['R_Thigh', 'R_ThighTwist_HJ_00'],
            ['L_Knee', 'L_KneeDouble_HJ_00'],
            ['R_Knee', 'R_KneeDouble_HJ_00'],
        ]
        ArmatureName0 = bpy.context.active_object.name

        bpy.ops.import_scene.fbx(filepath=FemaleFbxskelMesh, use_custom_props=True, force_connect_children=False)
        ArmatureObj = bpy.context.active_object
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

        self.report({'INFO'}, 'generation completed')
        return {'FINISHED'}
