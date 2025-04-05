from .addons.Modder_Batch_Tool import register as addon_register, unregister as addon_unregister

bl_info = {
    "name": 'Modder Batch Tool',
    "author": '诸葛不太亮',
    "blender": (2, 93, 0),
    "version": (1, 3, 1),
    "description": 'Utility tools to do a lot of repetitive operations automatically.',
    "warning": '',
    "wiki_url": 'https://github.com/chikichikibangbang/Modder_Batch_Tool',
    "tracker_url": 'https://github.com/chikichikibangbang/Modder_Batch_Tool/issues',
    "support": 'COMMUNITY',
    "category": '3D View'
}

def register():
    addon_register()

def unregister():
    addon_unregister()

    
