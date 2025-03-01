
import json
import bpy
import re

from bpy.types import (
    Panel,
    Operator,
)

from ..operators.OT_Settings import TM_OT_Settings_OpenMessageBox
from ..utils.Functions  import *
from ..utils.Constants  import * 




class TM_PT_Materials(Panel):
    bl_label = "Materials"
    bl_idname = "OBJECT_PT_TM_Materials"
    locals().update( PANEL_CLASS_COMMON_DEFAULT_PROPS )

    @classmethod
    def poll(self, context):
        return is_selected_nadeoini_file_name_ok()

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon=ICON_MATERIAL)
    
    def draw_header_preset(self, context):
        layout = self.layout
        tm_props = get_global_props()
        row = layout.row(align=True)
    
        col = row.column(align=True)
        op = col.operator("view3d.tm_open_messagebox", text="", icon=ICON_QUESTION)
        op.link = ""
        op.title = "Material Infos"
        op.infos = TM_OT_Settings_OpenMessageBox.get_text(
            "Here you can configure your materials",
            "-> Materials need to be created or updated with the addon",
            "-> Materials can have any name, TM_ or MP_ will be added automatically to differ from other materials",
            "-> Materials can have optionally a custom physic, if not set, default will be used",
            "-> Some Materials can be colored (TM2020 only)",
            "-> Some Materials can have a second physic called 'Gameplay' (TM2020 only)",
            "-> Materials need to be linked to an existing material created by nadeo",
            "----> Those materials are pre defined in the NadeoImporerMaterialLib.txt file",
            "-> Materials can have custom, non game, textures (Maniaplanet only)",
        ) 


    def draw(self, context):

        layout   = self.layout
        tm_props = get_global_props()

        action      = tm_props.LI_materialAction
        mat_name     = tm_props.ST_materialAddName
        mat_name_old  = tm_props.ST_selectedExistingMaterial

        action_is_update = action == "UPDATE"
    
        use_physicsId   = tm_props.CB_materialUsePhysicsId
        use_gameplayId  = tm_props.CB_materialUseGameplayId

        #uncomment it during development if you need to generate new assets library file
        #box = layout.box()
        #row = box.row()
        #row.operator("view3d.tm_createassetlib", text=f"Create {tm_props.LI_gameType} Assets Library", icon="ADD")


        # choose action & mat name
        layout.row().prop(tm_props, "LI_materialAction", expand=True)

        if action_is_update:
            layout.row().prop_search(tm_props, "ST_selectedExistingMaterial", bpy.data, "materials") 
    
        matcol = layout.column(align=True)
        matcol.prop(tm_props, "ST_materialAddName")

        # row = layout.row()
        # row.enabled = True if not tm_props.CB_converting else False
        # row.prop(tm_props, "LI_gameType", text="Game")





        if is_game_maniaplanet():
            matcol.prop(tm_props, "LI_materialCollection", text="Collection")
            
            enable = True if use_physicsId else False
            icon   = ICON_CHECKED if enable else ICON_UNCHECKED

            row = matcol.row(align=True)
            col = row.column()
            col.enabled = enable
            col.prop(tm_props, "LI_materialPhysicsId", text="Physics")
            col = row.column()
            col.prop(tm_props, "CB_materialUsePhysicsId", text="", toggle=True, icon=ICON_CHECKED)
            
            layout.separator(factor=UI_SPACER_FACTOR)

            # choose custom tex or linked mat
            
            src_col = layout.column(align=True)
            row = src_col.row(align=True)
            row.prop(tm_props, "LI_materialChooseSource", expand=True)
            
            using_custom_texture = tm_props.LI_materialChooseSource == "CUSTOM"

            # basetexture
            if using_custom_texture:
                row = src_col.row(align=True)
                row.alert = True if "/Items/" not in fix_slash(tm_props.ST_materialBaseTexture) else False
                row.prop(tm_props, "ST_materialBaseTexture", text="Location")
                row.operator("view3d.tm_clearbasetexture", icon=ICON_CANCEL, text="")

                if row.alert:
                    row=src_col.row()
                    row.alert = True
                    row.label(text=".dds file in Documents/Maniaplanet/Items/")

                # model
                row = src_col.row()
                row.prop(tm_props, "LI_materialModel")
            

            # link
            else:
                row = src_col.row()
                row.prop_search(
                    tm_props, "ST_selectedLinkedMat", # value of selection
                    context.scene, "tm_props_linkedMaterials", # list to search in 
                    icon=ICON_LINKED,
                    text="Link") 




        elif is_game_trackmania2020():
            # physics id
            enable = True if use_physicsId else False

            # TODO disable physicsid based on customxxx materials ??
            row = matcol.row(align=True)
            col = row.column()
            col.enabled = enable
            col.prop(tm_props, "LI_materialPhysicsId", text="Physics")
            col = row.column()
            col.prop(tm_props, "CB_materialUsePhysicsId", text="", toggle=True, icon=ICON_CHECKED)

            selected_mat = tm_props.ST_selectedLinkedMat

            # gameplay id
            if selected_mat in LINKED_MATERIALS_COMPATIBLE_WITH_GAMEPLAY_ID:
                row = matcol.row(align=True)
                col = row.column()
                col.enabled = use_gameplayId
                col.prop(tm_props, "LI_materialGameplayId", text="Gameplay")
                col = row.column()
                col.prop(tm_props, "CB_materialUseGameplayId", text="", toggle=True, icon=ICON_CHECKED)
            # else:
            #     row = matcol.row(align=True)
            #     row.label(text="Gameplay:")
            #     row.label(text="Material not supported")
                
            # custom color for materials starts with "custom"
            mat_uses_custom_color = selected_mat.lower().startswith("custom")

            row = matcol.row(align=True)
            row.alert = mat_uses_custom_color
            col = row.column()
            col.scale_x = .55
            col.label(text="Color")
            col = row.column()
            col.prop(tm_props, "NU_materialCustomColor", text="")
            if action_is_update:
                row.operator("view3d.tm_revertcustomcolor", icon=ICON_UPDATE, text="")
            
            # Link
            row = matcol.row()
            row.prop_search(
                tm_props, "ST_selectedLinkedMat", # value of selection
                context.scene, "tm_props_linkedMaterials", # list to search in 
                icon=ICON_LINKED,
                text="Link") 


        row = layout.row()
        row.scale_y = 1.5

        if action_is_update:
            row.operator("view3d.tm_updatematerial", text=f"Update {mat_name_old}", icon=ICON_UPDATE)

        else:
            row.operator("view3d.tm_creatematerial", text=f"Create {mat_name}",    icon=ICON_ADD)


        layout.separator(factor=UI_SPACER_FACTOR)


            
        

