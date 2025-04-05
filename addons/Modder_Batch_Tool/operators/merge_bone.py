#from CATS Plugin
import bpy

def get_objects():
    return bpy.context.view_layer.objects


def set_active(obj, skip_sel=False):
    if not skip_sel:
        select(obj)
        bpy.context.view_layer.objects.active = obj


def select(obj, sel=True):
    if obj is not None:
        hide(obj, False)
        obj.select_set(sel)

def hide(obj, val=True):
    if hasattr(obj, 'hide_set'):
        obj.hide_set(val)
    elif hasattr(obj, 'hide'):
        obj.hide = val

def mix_weights(mesh, vg_from, vg_to, mix_strength=1.0, mix_mode='ADD', mix_set='ALL', delete_old_vg=True):
    """Mix the weights of two vertex groups on the mesh, optionally removing the vertex group named vg_from.
    This function uses the Vertex Weight Mix modifier to efficiently mix vertex group weights.
    """
    # Ensure the correct shape key is active
    mesh.active_shape_key_index = 0
    # Create the Vertex Weight Mix modifier
    mod = mesh.modifiers.new(name="VertexWeightMix_" + vg_from + "_into_" + vg_to, type='VERTEX_WEIGHT_MIX')
    mod.vertex_group_a = vg_to
    mod.vertex_group_b = vg_from
    mod.mix_mode = mix_mode
    mod.mix_set = mix_set  # Use 'ALL' to include all vertices
    mod.mask_constant = mix_strength  # Strength of the mix
    # Apply the modifier to the mesh
    # Depending on your Blender version, you may need to adjust how the modifier is applied.
    if bpy.ops.object.modifier_apply.poll():
        mesh.modifiers.active = mod
        bpy.ops.object.modifier_apply(modifier=mod.name)
    # Optionally remove the source vertex group
    if delete_old_vg:
        vg_from_group = mesh.vertex_groups.get(vg_from)
        if vg_from_group:
            mesh.vertex_groups.remove(vg_from_group)

    # Reset the active shape key index
    mesh.active_shape_key_index = 0

def unselect_all():
    for obj in get_objects():
        select(obj, False)

def switch(new_mode, check_mode=True):
    context = bpy.context
    active = context.view_layer.objects.active
    if check_mode and active and active.mode == new_mode:
        return
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode=new_mode, toggle=False)



def merge_weights(armature, parenting_list):
    # Common.switch('OBJECT')
    # Merge the weights on the meshes
    for mesh in get_meshes_objects(armature_name=armature.name,
                                   visible_only=False):
        set_active(mesh)

        for bone, parent in parenting_list.items():
            if not mesh.vertex_groups.get(bone):
                continue
            if not mesh.vertex_groups.get(parent):
                mesh.vertex_groups.new(name=parent)
            mix_weights(mesh, bone, parent)

    # Select armature
    unselect_all()
    set_active(armature)
    switch('EDIT')

    # Delete merged bones
    if not bpy.context.scene.keep_merged_bones:
        for bone in parenting_list.keys():
            edited_bone = armature.data.edit_bones.get(bone)
            if edited_bone is not None:
                armature.data.edit_bones.remove(edited_bone)

def is_hidden(obj):
    if hasattr(obj, 'hide_get'):
        return obj.hide_get()
    elif hasattr(obj, 'hide'):
        return obj.hide
    return False  # Return a default value if the hide state cannot be determined


def delete(obj):
    if obj.parent:
        for child in obj.children:
            child.parent = obj.parent

    objs = bpy.data.objects
    objs.remove(objs[obj.name], do_unlink=True)


# def is_enum_empty(string):
#     """Returns True only if the tested string is the string that signifies that an EnumProperty is empty.
#
#     Returns False in all other cases."""
#     return _empty_enum_identifier == string



def get_meshes_objects(armature_name=None, mode=0, check=True, visible_only=False):
    context = bpy.context
    # Modes:
    # 0 = With armatures only
    # 1 = Top level only
    # 2 = All meshes
    # 3 = Selected only

    if not armature_name:
        armature = get_armature()
        if armature:
            armature_name = armature.name

    meshes = []

    for ob in get_objects():
        if ob is None:
            continue
        if ob.type != 'MESH':
            continue

        if mode == 0 or mode == 5:
            if ob.parent:
                if ob.parent.type == 'ARMATURE' and ob.parent.name == armature_name:
                    meshes.append(ob)
                elif ob.parent.parent and ob.parent.parent.type == 'ARMATURE' and ob.parent.parent.name == armature_name:
                    meshes.append(ob)

        elif mode == 1:
            if not ob.parent:
                meshes.append(ob)

        elif mode == 2:
            meshes.append(ob)

        elif mode == 3:
            if ob.select_get():
                meshes.append(ob)

    if visible_only:
        for mesh in meshes:
            if is_hidden(mesh):
                meshes.remove(mesh)

    # Check for broken meshes and delete them
    if check:
        current_active = context.view_layer.objects.active
        to_remove = []
        for mesh in meshes:
            selected = mesh.select_get()
            # print(mesh.name, mesh.users)
            set_active(mesh)

            if not context.view_layer.objects.active:
                to_remove.append(mesh)

            if not selected:
                select(mesh, False)

        for mesh in to_remove:
            print('DELETED CORRUPTED MESH:', mesh.name, mesh.users)
            meshes.remove(mesh)
            delete(mesh)

        if current_active:
            set_active(current_active)

    return meshes


def get_armature(armature_name=None):
    if not armature_name:
        armature_name = bpy.context.scene.armature

    # Get all objects in the scene
    objects = get_objects()
    if not objects:
        return None

    # First try to find exact name match
    for obj in objects:
        if obj and obj.type == 'ARMATURE':
            if obj.name == armature_name:
                return obj

    # If no exact match, return first armature if name is empty
    # if is_enum_empty(armature_name):
    #     for obj in objects:
    #         if obj and obj.type == 'ARMATURE':
    #             return obj

    return None

