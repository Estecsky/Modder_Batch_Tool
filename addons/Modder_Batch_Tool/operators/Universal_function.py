import bpy
import bmesh

def _Clean_Vertex_By_Weight():
    def check_each_vertex_group_max_weight(obj):
        gid_to_maxw = {}
        # 让统计字典内的顶点组的初始值为0
        for g in obj.vertex_groups:
            gid_to_maxw[g.index] = 0
        # 循环网格体的每一个顶点，统计每个顶点组的最大权重
        for v in obj.data.vertices:
            for g in v.groups:
                gid = g.group
                w = obj.vertex_groups[gid].weight(v.index)
                if (gid_to_maxw.get(gid) is None or w > gid_to_maxw[gid]):
                    gid_to_maxw[gid] = w
        return gid_to_maxw

    # 获得对象
    for obj in bpy.context.selected_objects:
        # 获得对象的 每个顶点组到最大权重的字典
        gid_to_maxw = check_each_vertex_group_max_weight(obj)
        # 让字典的值按大到小排序，这是为了从大到小逐个删除时，删除序号大的不会影响序号小。
        wait_to_del_gids = []
        for gid, maxw in gid_to_maxw.items():
            if maxw <= 0:
                wait_to_del_gids.append(gid)
        # 让顶点组编号从大到小排序，这先删除编号大的不会对编号小的造成影响
        wait_to_del_gids = sorted(wait_to_del_gids)[::-1]
        # print(f'Delete vertex group index list {wait_to_del_gids}')
        # 逐个删除空顶点组
        for gid in wait_to_del_gids:
            obj.vertex_groups.remove(obj.vertex_groups[gid])
    # print('Success')

class CleanZeroVG(bpy.types.Operator):
    bl_idname = "mbt.clean_zero_vg"
    bl_label = "clean zero weight vg"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects is not None:
            for obj in bpy.context.selected_objects:
                return bool(obj.type == "MESH")

    def execute(self, context):
        _Clean_Vertex_By_Weight()
        self.report({'INFO'}, 'clean completed')
        return {'FINISHED'}


class SeparateByMaterials(bpy.types.Operator):
    bl_idname = "mbt.separate_by_materials"
    bl_label = "separate by materials"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = bpy.context.active_object
        return obj is not None and obj.type == "MESH"

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='MATERIAL')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.mbt.clean_zero_vg()

        for obj in bpy.context.selected_objects:
            if obj.type == "MESH":
                mat_name = obj.active_material.name if obj.active_material else obj.name
                obj.name = mat_name
                # print(mat_name)

        self.report({'INFO'}, 'separate completed')
        return {'FINISHED'}


class RemoveShapeKeys(bpy.types.Operator):
    bl_idname = "mbt.remove_shapekeys"
    bl_label = "remove all shape keys"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        for obj in bpy.context.selected_objects:
            return obj.type == "MESH"

    def execute(self, context):
        meshes_sel_name = sorted([o.name for o in bpy.context.selected_objects if o.type == "MESH"])
        for n in meshes_sel_name:
            bpy.context.view_layer.objects.active = bpy.data.objects[n]
            obj = bpy.context.active_object
            if obj.data.shape_keys:
                bpy.ops.object.shape_key_remove(all=True)
        bpy.context.view_layer.objects.active = bpy.data.objects[meshes_sel_name[0]]
        self.report({'INFO'}, 'remove completed')
        return {'FINISHED'}


class UnifyUVs(bpy.types.Operator):
    bl_idname = "mbt.unify_uvs"
    bl_label = "unify UVs"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects is not None:
            for obj in bpy.context.selected_objects:
                return obj.type == "MESH"

    def execute(self, context):
        meshes_sel_name = sorted([o.name for o in bpy.context.selected_objects if o.type == "MESH"])

        for n in meshes_sel_name:
            bpy.context.view_layer.objects.active = bpy.data.objects[n]
            activemesh = bpy.context.active_object

            for i in range(len(activemesh.data.uv_layers)):
                if i == 0:
                    activemesh.data.uv_layers[0].name = "UVMap"
                    continue
                else:
                    activemesh.data.uv_layers.active = activemesh.data.uv_layers[len(activemesh.data.uv_layers) - 1]
                    bpy.ops.mesh.uv_texture_remove()
                    activemesh.data.uv_layers[0].name = "UVMap"

        bpy.context.view_layer.objects.active = bpy.data.objects[meshes_sel_name[0]]
        self.report({'INFO'}, 'unify completed')
        return {'FINISHED'}


class SplitSeamEdge(bpy.types.Operator):
    bl_idname = 'mbt.split_seam_edge'
    bl_label = "split seam edge"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects is not None:
            for obj in bpy.context.selected_objects:
                return obj.type == "MESH"

    def execute(self, context):
        meshes_sel_name = sorted([o.name for o in bpy.context.selected_objects if o.type == "MESH"])

        for n in meshes_sel_name:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.view_layer.objects.active = bpy.data.objects[n]
            obj = bpy.context.active_object

            # 分离缝合边
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.uv.seams_from_islands(mark_seams=True)
            bpy.context.tool_settings.mesh_select_mode = (False, True, False)
            bpy.ops.mesh.select_all(action='DESELECT')

            bpy.ops.object.mode_set(mode='OBJECT')
            for edge in obj.data.edges:
                if edge.use_seam:
                    edge.select = True
                    # bpy.ops.object.mode_set(mode='EDIT')
                    # bpy.ops.mesh.edge_split(type='EDGE')
                    # bpy.ops.object.mode_set(mode='OBJECT')

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.edge_split(type='EDGE')

            # bpy.ops.mesh.select_all(action='SELECT')
            # bpy.ops.mesh.delete_loose()
            # bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

            # 分离重叠点
            uv_layers = obj.data.uv_layers.active
            uv_coords = {}
            for poly in obj.data.polygons:
                loop_start = poly.loop_start
                loop_end = loop_start + poly.loop_total
                i = 0
                for loop_index in range(loop_start, loop_end):
                    uv_co = uv_layers.data[loop_index].uv
                    if poly.vertices[i] in uv_coords and uv_coords[poly.vertices[i]] != uv_co:
                        obj.data.vertices[poly.vertices[i]].select = True
                    else:
                        uv_coords[poly.vertices[i]] = uv_co
                    i += 1

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.edge_split(type='VERT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

            # 分离锐边
            bpy.ops.object.mode_set(mode='EDIT')
            bm = bmesh.from_edit_mesh(obj.data)
            for e in bm.edges:
                if not e.smooth:
                    e.select = True
            bpy.ops.mesh.edge_split(type='EDGE')
            bpy.ops.mesh.select_all(action='DESELECT')
            bmesh.update_edit_mesh(obj.data)

            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete_loose()
            bpy.ops.mesh.select_all(action='DESELECT')

            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.context.view_layer.objects.active = bpy.data.objects[meshes_sel_name[0]]
        self.report({'INFO'}, 'split completed')
        return {'FINISHED'}


class NormalizeLimit8wtVG(bpy.types.Operator):
    bl_idname = "mbt.normalize_limit_8wt_vg"
    bl_label = "normalize and limit to 8wt"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects is not None:
            for obj in bpy.context.selected_objects:
                return obj.type == "MESH"

    def execute(self, context):
        meshes_sel_name = sorted([o.name for o in bpy.context.selected_objects if o.type == "MESH"])
        # print(meshes_sel_name)

        bpy.ops.mbt.clean_zero_vg()
        for n in meshes_sel_name:
            bpy.context.view_layer.objects.active = bpy.data.objects[n]
            bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
            bpy.ops.object.vertex_group_lock(action='UNLOCK', mask='ALL')
            bpy.ops.object.vertex_group_normalize_all(lock_active=False)
            bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.001)
            bpy.ops.object.vertex_group_limit_total(limit=8)
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.context.view_layer.objects.active = bpy.data.objects[meshes_sel_name[0]]
        self.report({'INFO'}, 'conversion completed')
        return {'FINISHED'}

class NormalizeLimit6wtVG(bpy.types.Operator):
    bl_idname = "mbt.normalize_limit_6wt_vg"
    bl_label = "normalize and limit to 6wt"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects is not None:
            for obj in bpy.context.selected_objects:
                return obj.type == "MESH"

    def execute(self, context):
        meshes_sel_name = sorted([o.name for o in bpy.context.selected_objects if o.type == "MESH"])
        # print(meshes_sel_name)

        bpy.ops.mbt.clean_zero_vg()
        for n in meshes_sel_name:
            bpy.context.view_layer.objects.active = bpy.data.objects[n]
            bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
            bpy.ops.object.vertex_group_lock(action='UNLOCK', mask='ALL')
            bpy.ops.object.vertex_group_normalize_all(lock_active=False)
            bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.001)
            bpy.ops.object.vertex_group_limit_total(limit=6)
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.context.view_layer.objects.active = bpy.data.objects[meshes_sel_name[0]]
        self.report({'INFO'}, 'conversion completed')
        return {'FINISHED'}

class NormalizeLimit4wtVG(bpy.types.Operator):
    bl_idname = "mbt.normalize_limit_4wt_vg"
    bl_label = "normalize and limit to 4wt"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if bpy.context.selected_objects is not None:
            for obj in bpy.context.selected_objects:
                return obj.type == "MESH"

    def execute(self, context):
        meshes_sel_name = sorted([o.name for o in bpy.context.selected_objects if o.type == "MESH"])
        # print(meshes_sel_name)

        bpy.ops.mbt.clean_zero_vg()
        for n in meshes_sel_name:
            bpy.context.view_layer.objects.active = bpy.data.objects[n]
            bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
            bpy.ops.object.vertex_group_lock(action='UNLOCK', mask='ALL')
            bpy.ops.object.vertex_group_normalize_all(lock_active=False)
            bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.001)
            bpy.ops.object.vertex_group_limit_total(limit=4)
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.context.view_layer.objects.active = bpy.data.objects[meshes_sel_name[0]]
        self.report({'INFO'}, 'conversion completed')
        return {'FINISHED'}


