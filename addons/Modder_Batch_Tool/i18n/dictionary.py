from ....common.i18n.dictionary import preprocess_dictionary

dictionary = {

    "zh_CN": {
        # Preferences
        ("*", "View3D > Tool Shelf > Modder's Batch Tool"): "3D视图 > 侧栏 > Modder's Batch Tool面板",
        ("*", "Utility tools to do a lot of repetitive operations automatically"): "可以自动做大量重复工作的实用工具",

        # Show Panel Settings
        ("*", "Show Panel Settings"): "展示面板设置",

        # Universal Function
        ("*", "Universal Function"): "通用功能",
        ("Operator", "separate by materials"): "按材质分离",
        ("Operator", "clean zero weight vg"): "清除空顶点组",

        # Universal translation
        ("*",
         "Make sure you select armature below first and then the game armature in the object mode"): "先选中以下骨架，再选中游戏骨架，最后点击吸附骨架",
        ("*", "batch rename vertax groups"): "批量更改顶点组名",
        ("*", "Batch absorb bones (only support t-pose)"): "批量吸附骨骼位置（仅支持t-pose）",
        ("Operator", "absorb bones"): "吸附骨骼",
        ("Operator", "rename vertex group"): "重命名顶点组",
        ("*", "Batch normalize and limit weight to 8wt"): "批量规格化权重并设置总限值为8",
        ("*", "Batch normalize and limit weight to 6wt"): "批量规格化权重并设置总限值为6",
        ("*", "Batch normalize and limit weight to 4wt"): "批量规格化权重并设置总限值为4",
        ("Operator", "normalize and limit to 8wt"): "规格化权重并设置总限值为8",
        ("Operator", "normalize and limit to 6wt"): "规格化权重并设置总限值为6",
        ("Operator", "normalize and limit to 4wt"): "规格化权重并设置总限值为4",

        ("*", "Batch split seam edge"): "批量分离缝合边",
        ("Operator", "split seam edge"): "分离缝合边",
        ("*", "Batch delete unnecessary UVs and unify UV names"): "批量删除多余的UV通道并统一UV名称",
        ("Operator", "unify UVs"): "统一UV通道",
        ("Operator", "remove all shape keys"): "删除全部形态键",
        ("*", "Convert to t-pose"): "转换为t-pose",
        ("Operator", "convert to t-pose"): "转换为t-pose",

        # Image Combiner
        ("*", "Image Combiner"): "贴图合并",
        ("*",
         "this modified combiner doesn't combine materials, so you can still seperate by materials"): "此魔改版插件并不合并材质，所以你仍可以按材质分离",
        ("*", "materials to combine:"): "要参与合并的材质",
        ("Operator", "Update Material List"): "更新材质列表",
        ("Operator", "Generate Material List"): "生成材质列表",
        ("*", "Properties:"): "特性",
        ("*", "Combined image size"): "合并贴图尺寸",
        ("*", "Power of 2"): "2的整数幂",
        ("Operator", "Save Combined Image"): "保存合并贴图",
        ("*", "Combine Images"): "合并贴图",

        # Credits
        ("*", "Credits"): "贡献者名单",
        ("*", "Korone"): "诸葛不太亮",
        ("Operator", "QQGroup"): "QQ群",
        ("Operator", "Caimogu"): "踩蘑菇mod论坛",

        # MHRise
        ("*", "import MHRise shadow mesh"): "导入MHRise通用骨架模型",

        # MHWorld
        ("*",
         "make sure you have installed <Easier MHW MOD3 Import_Export> plugin"): "请确保您已经安装《更方便的MOD3导入导出插件》",
        ("*", "import MHWorld basic armature"): "导入MHWorld基本骨架",
        ("Operator", "female armature"): "女性骨架",
        ("Operator", "male armature"): "男性骨架",
        ("*", "batch add empty mod3 meshes with properties"): "批量添加带自定义属性的mod3空模型网格",
        ("Operator", "add empty meshes"): "添加空模型网格",
        ("*", "batch emptied blocklabel"): "批量清空自定义属性的blocklabel",
        ("Operator", "emptied blocklabel"): "清空blocklabel",
        ("*",
         "Note: this function will automatically do all export pre-processing!"): "注意：该功能将自动为mod3模型网格做所有的导出前预处理!",
        ("Operator", "auto export process"): "自动导出预处理",

        # MHWilds
        ("*", "Import MHWilds basic mesh"): "导入MHWilds基本模型",
        ("Operator", "female mesh"): "女性模型",
        ("Operator", "male armature"): "男性骨架",
        ("*", "Batch rename meshes to re format"): "批量重命名网格名为RE格式",
        ("Operator", "rename meshes"): "重命名网格名",
        ("*", "Generate or export fbxskel"): "生成或导出骨架对应的fbxskel",
        ("Operator", "generate fbxskel"): "生成fbxskel",
        ("Operator", "export fbxskel"): "导出fbxskel",



        # GranblueFantasyRelink
        # ("*", "convert gbfr model to tpose"): "将gbfr模型转换为tpose",
        # ("Operator", "convert to tpose"): "转换为tpose",


        # Props
        ("Operator", "Process Settings"): "功能设置",
        ("*", "convert quads to tris"): "面三角化",
        ("*", "split seam edge"): "分离缝合边",
        ("*", "unify UVs"): "统一UV通道",
        ("*", "separate by materials"): "按材质分离",
        ("*", "clean zero weight vg"): "清除空顶点组",
        ("*", "emptied blocklabel"): "清空blocklabel",


    }
}

dictionary = preprocess_dictionary(dictionary)

dictionary["zh_HANS"] = dictionary["zh_CN"]
