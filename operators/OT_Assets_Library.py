
import bpy
import uuid
import time
from pathlib import Path

from bpy.types import (
    Operator,
    Material,
)

from ..utils.Materials import create_material_nodes

from ..utils.Functions          import *
from ..operators.OT_Materials   import *
from ..utils.Constants          import * 

class TM_OT_Materials_Create_Asset_Lib(Operator):
    bl_idname = "view3d.tm_createassetlib"
    bl_label = "create assets library"
    bl_description = "Create assets library, ignores previously created materials with the same name"
   
    def execute(self, context):
        if save_blend_file():
            createAssetsLib()
        else:
            show_report_popup("FILE NOT SAVED!", ["Save your blend file!"], "ERROR")

        return {"FINISHED"}



def createAssetsLib() -> None:
    #currentFile = bpy.data.filepath

    # clear all possible data
    for bpy_data_iter in (
            bpy.data.objects,
            bpy.data.meshes,
            bpy.data.cameras,
            bpy.data.materials,
            bpy.data.cameras,
            bpy.data.armatures,
            bpy.data.collections,
            bpy.data.curves,
            bpy.data.images,
    ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data, do_unlink=True)

    createAssetsCatalogFile(get_game_doc_path_items_assets())
    
    fileName = ""
    if is_game_trackmania2020():
        fileName = get_global_props().LI_gameType+"_assets.blend"
        generate2020Assets()
    elif is_game_maniaplanet():
        fileName = get_global_props().LI_gameType+"_assets.blend"
        generateMPAssets()  

    # save as new blend file for assets libraray
    create_folder_if_necessary(get_game_doc_path_items_assets())
    if not save_blend_file_as(fix_slash(get_game_doc_path_items_assets()+"/"+fileName)):
        show_report_popup("Can not create new blend file", ["Something went wrong during creation of a new blend file"], "ERROR")

    # reopen original file
    # bpy.ops.wm.open_mainfile(filepath=currentFile)
    return

def generate2020Assets() -> None:
    getOrCreateCatalog(get_game_doc_path_items_assets(), get_global_props().LI_gameType)
    getOrCreateCatalog(get_game_doc_path_items_assets(), get_global_props().LI_gameType+"/Stadium")
    getOrCreateCatalog(get_game_doc_path_items_assets(), get_global_props().LI_gameType+"/Stadium/Materials")


    for key in MATERIALS_MAP_TM2020:
        matNameNew = "TM_"+key+"_asset" 
        if matNameNew in bpy.data.materials:
            continue

        color = (0.0,0.319,0.855)
        if "Color" in MATERIALS_MAP_TM2020[key]:
            color = hex_to_rgb(MATERIALS_MAP_TM2020[key]["Color"])   
        mat = createMaterialAsset(matNameNew, key, color)

        if mat.use_nodes:
            if (
                "IsSign" not in MATERIALS_MAP_TM2020[key] and
                "tex_D" in mat.node_tree.nodes and
                mat.node_tree.nodes["tex_D"].image and
                mat.node_tree.nodes["tex_D"].image.filepath
            ):
                bpy.ops.ed.lib_id_load_custom_preview(
                    {"id": mat}, 
                    filepath=mat.node_tree.nodes["tex_D"].image.filepath
                )
            elif (
                "tex_I" in mat.node_tree.nodes and
                mat.node_tree.nodes["tex_I"].image and
                mat.node_tree.nodes["tex_I"].image.filepath
            ):
                bpy.ops.ed.lib_id_load_custom_preview(
                    {"id": mat}, 
                    filepath=mat.node_tree.nodes["tex_I"].image.filepath
                )
            else:
                # short delay to let materials become registered
                # otherwise preview is not generating
                time.sleep(0.05)
                bpy.ops.ed.lib_id_generate_preview({"id": mat})

        mat.asset_mark()

        catName = "Rest"
        if "Category" in MATERIALS_MAP_TM2020[key]:
            catName = MATERIALS_MAP_TM2020[key]["Category"]
            print(catName)
        uid = getOrCreateCatalog(get_game_doc_path_items_assets(), get_global_props().LI_gameType+"/Stadium/Materials/"+catName)
        if uid:
            mat.asset_data.catalog_id = uid



def generateMPAssets() -> None:
    for col in getMaterialCollectionTypes():
        if col[0] == "Common":
            continue
        
        getOrCreateCatalog(get_game_doc_path_items_assets(), get_global_props().LI_gameType)
        catalogUUID = getOrCreateCatalog(get_game_doc_path_items_assets(), get_global_props().LI_gameType+"/"+col[0]+"/Materials")

        get_global_props().LI_materialCollection = col[0]
        gameTypeGotUpdated()

        matList = get_linked_materials()
        for matItem in matList:
            matNameNew = f"MP_{get_global_props().LI_materialCollection}_{matItem.name}_asset"
            if matNameNew in bpy.data.materials:
                continue

            mat = createMaterialAsset(matNameNew, matItem.name, (0,0,0))
            if mat.use_nodes:
                if (
                    "tex_D" in mat.node_tree.nodes and
                    mat.node_tree.nodes["tex_D"].image and
                    mat.node_tree.nodes["tex_D"].image.filepath
                ):
                    bpy.ops.ed.lib_id_load_custom_preview(
                        {"id": mat}, 
                        filepath=mat.node_tree.nodes["tex_D"].image.filepath
                    )
                elif (
                    "tex_I" in mat.node_tree.nodes and
                    mat.node_tree.nodes["tex_I"].image and
                    mat.node_tree.nodes["tex_I"].image.filepath
                ):
                    bpy.ops.ed.lib_id_load_custom_preview(
                        {"id": mat}, 
                        filepath=mat.node_tree.nodes["tex_I"].image.filepath
                    )
                else:
                    # short delay to let materials become registered
                    # otherwise preview is not generating
                    time.sleep(0.05)
                    bpy.ops.ed.lib_id_generate_preview({"id": mat})

                mat.asset_mark()
                mat.asset_data.catalog_id = catalogUUID

    return



def createMaterialAsset(name: str, link: str, color: tuple[float, float, float]) -> Material:
    MAT = bpy.data.materials.new(name=name)

    MAT.gameType      = get_global_props().LI_gameType
    MAT.environment   = get_global_props().LI_materialCollection
    MAT.usePhysicsId  = False
    MAT.useGameplayId = False
    MAT.model         = "TDSN"
    MAT.link          = link
    MAT.baseTexture   = ""
    MAT.name          = name
    MAT.surfaceColor  = color
    
    create_material_nodes(MAT)
    
    return MAT
        


def createAssetsCatalogFile(path: str) -> None:
    pathToAssets = os.path.join(path, "blender_assets.cats.txt")
    if not os.path.exists(pathToAssets):
        f = open(pathToAssets, "x")
        f.write("VERSION 1\n\n")
        f.close()



def getCatalogsList(path: str) -> dict:
    catList = {}
    with open(os.path.join(path, "blender_assets.cats.txt")) as f:
        for line in f.readlines():
            if line.startswith(("#", "VERSION", "\n")):
                continue
            
            parts = line.split(":")
            catList[parts[1]] = parts[0]

    return catList



# returns catalog UUID
def getOrCreateCatalog(path: str, name: str) -> str:
    catList = getCatalogsList(path)
    if name in catList:
        return catList[name]
    else:
        with open(os.path.join(path, "blender_assets.cats.txt"), "a") as f:
            uid = uuid.uuid4()
            f.write(f"{uid}:{name}:{name.replace('/', '-', -1)}\n")
            return f"{uid}"