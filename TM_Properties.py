from pprint import pprint
from typing import List
import bpy
import re
import bpy.utils.previews
from bpy.props import *
from bpy.types import (
    Panel,
    Operator,
    AddonPreferences,
    PropertyGroup
)

from .TM_Functions import * 




errorEnumProps      = [("ERROR", "ERROR", "ERROR", "ERROR", 0)]
matPhysics          = errorEnumProps
matLinks            = errorEnumProps




def isNadeoIniValid()->bool:
    if isGameTypeManiaPlanet():     return bpy.context.scene.tm_props.ST_nadeoIniFile_MP
    if isGameTypeTrackmania2020():  return bpy.context.scene.tm_props.ST_nadeoIniFile_TM
        

def getGameTypes()->list:
    return [
        ("ManiaPlanet",     "ManiaPlanet",      "ManiaPlanet",      getIcon("maniaplanet"), 0),
        ("Trackmania2020",  "Trackmania2020",   "Trackmania2020",   getIcon("trackmania2020"), 1),
    ]


def gameTypeGotUpdated()->None:
    """reset important variables to fit new gameType environment"""
    isNadeoImporterInstalled()
    resetNadeoIniSettings()

    global matLinks, matPhysics, nadeoLibMaterials
    matLinks   = errorEnumProps
    matPhysics = errorEnumProps
    nadeoLibParser(refresh=True)

    tm_props     = bpy.context.scene.tm_props
    colIsStadium = tm_props.LI_materialCollection.lower() == "stadium"

    if isGameTypeTrackmania2020() and not colIsStadium:
        tm_props.LI_materialCollection = "Stadium"

    return None


def getGameTextureZipFileNames()->list:
    envis = [
        "Stadium",
        "Valley",
        "Canyon",
        "Lagoon",
        "Shootmania",
    ]
    return [(e,e,e) for e in envis]


def getExportTypes()->list:
    return[
        ("EXPORT",          "Export only",          "Export only",                      "EXPORT", 0),
        ("EXPORT_CONVERT",  "Export and Convert",   "Export fbx and convert to gbx",    "CON_FOLLOWPATH", 1),
        ("CONVERT",         "Convert only",         "Convert only",                     "FILE_REFRESH", 2),
    ]


def getExportFolderTypes(self,context)->list:
    return[
        ("Base",       "Base",         "Base folder(/Items",           "HOME",                  0),
        ("Stadium",    "Stadium",      "Base folder(/Items/Stadium",   getIcon("ENVI_STADIUM"), 1),
        ("Valley",     "Valley",       "Base folder(/Items/Valley",    getIcon("ENVI_VALLEY"),  2),
        ("Canyon",     "Canyon",       "Base folder(/Items/Canyon",    getIcon("ENVI_CANYON"),  3),
        ("Lagoon",     "Lagoon",       "Base folder(/Items/Lagoon",    getIcon("ENVI_LAGOON"),  4),
        ("Shootmania", "Shootmania",   "Base folder(/Items/Storm",     getIcon("ENVI_STORM"),   5),
        ("Custom",     "Custom",       "Custom folder",                "FILE_FOLDER",           6),
    ]



def getExportWhichObjects()->list:
    return[
        ("SELECTED",    "Selected", "Selected objects(their collection) only",  "RESTRICT_SELECT_OFF",  0),
        ("VISIBLE",     "Visible",  "Visible objects(their collection) only",   "HIDE_OFF",             1),
    ]


def getExportObjTypes(self, context) -> list:
    return [
        (   'MESH_LIGHT_EMPTY', "All object types",     "Normal meshes, lights and empties",                "SCENE_DATA",   0),
        (   'MESH_LIGHT',       "Mesh, Light",          "Normal meshes, lights, no empties",                "LIGHT_SUN",    1),
        (   'MESH_EMPTY',       "Mesh, Empty",          "Normal meshes, empties(_socket_START), no lights", "EMPTY_ARROWS", 2),
    ]






def updateGridAndLevi(self, context) -> None:
    tm_props = bpy.context.scene.mp_props
    syncX = tm_props.NU_xml_gridAndLeviX
    syncY = tm_props.NU_xml_gridAndLeviY
    tm_props.NU_xml_gridX = syncX
    tm_props.NU_xml_gridY = syncY
    tm_props.NU_xml_leviX = syncX
    tm_props.NU_xml_leviY = syncY


def getWayPointVariations() -> list:
    return [
        ("Start",       "Start",        "Use this waypoint type as fallback", getIcon("WP_START"),          0),
        ("Finish",      "Finish",       "Use this waypoint type as fallback", getIcon("WP_FINISH"),         1),
        ("StartFinish", "StartFinish",  "Use this waypoint type as fallback", getIcon("WP_STARTFINISH"),    2),
        ("Checkpoint",  "Checkpoint",   "Use this waypoint type as fallback", getIcon("WP_CHECKPOINT"),     3),
    ]
     

def getItemXMLCollections() -> list:
    return [
        ("Stadium", "Stadium",  "", getIcon("ENVI_STADIUM"),    1),
        ("Canyon",  "Canyon",   "", getIcon("ENVI_CANYON"),     2),
        ("Valley",  "Valley",   "", getIcon("ENVI_VALLEY"),     3),
        ("Lagoon",  "Lagoon",   "", getIcon("ENVI_LAGOON"),     4),
        ("Storm",   "Storm",    "", getIcon("ENVI_STORM"),      5),
        ("Common",  "Common",   "", getIcon("ENVI_COMMON"),     6),
        ("SMCommon","SMCommon", "", getIcon("ENVI_COMMON"),     7),
    ]


def getItemXMLType() -> list:
    return [    
        ("StaticObject","StaticObject","StaticObject",  "KEYFRAME",     0), 
        ("DynaObject",  "DynaObject",   "DynaObject",   "KEYFRAME_HLT", 1) 
    ]


def getMeshXMLType() -> list:
    return [    
        ("Static",  "Static",   "Static",   "KEYFRAME",     0), 
        ("Dynamic", "Dynamic",  "Dynamic",  "KEYFRAME_HLT", 1) 
    ]







def getMaterials(self, context):
    mats = bpy.data.materials
    return [(mat.name, mat.name, mat.name) for mat in mats if mat.name.lower() != "dots stroke"]


def updateMaterialSettings(self, context):
    tm_props    = context.scene.tm_props
    matToUpdate = bpy.data.materials[tm_props.LI_materials]

    assignments = [
        ("tm_props.ST_materialAddName"      , "matToUpdate.name"),
        ("tm_props.LI_materialCollection"   , "matToUpdate.environment"),
        ("tm_props.LI_materialPhysicId"     , "matToUpdate.physicsId"),
        ("tm_props.LI_materialModel"        , "matToUpdate.model"),
        ("tm_props.LI_materialLink"         , "matToUpdate.link"),
        ("tm_props.ST_materialBaseTexture"  , "matToUpdate.baseTexture"),
        ("tm_props.NU_materialColor"        , "matToUpdate.surfaceColor"),
        # ("tm_props.LI_materialIsFromLib"    , "matToUpdate.isFromLib"),
    ]

    for assignment in assignments:
        variable   = assignment[0]
        value      = assignment[1]
        assignment = f"{variable} = {value}" #"""tm_props.ST_materialAddName = matToUpdate.name"""
        try:
            exec(assignment)
        except TypeError:
            pass



def getMaterialModelTypes()->list:
    models = ["TDSN", "TDOSN", "TDOBSN", "TDSNI", "TDSNI_NIGHT", "TIAdd"]
    return [(m, m, m) for m in models]


def getMaterialCollectionTypes()->list:
    collections = ["Stadium", "Canyon", "Valley", "Lagoon", "Storm", "Common"]
    return [(c, c, c) for c in collections]


def getMaterialActions()->list:
    return [
        ("CREATE", "Create", "Create", "ADD",           0),
        ("UPDATE", "Update", "Update", "FILE_REFRESH",  1),
        # ("CHECK",  "Check",  "Check",  "QUESTION",      2),
    ]


def getMaterialPhysicIds(self=None, context=None)->list:
    """get physics from nadeoLibParser() and return als list(tuples)"""
    global matPhysics #create global variable to read libfile only once
    
    if len(matPhysics) > 1:
        return matPhysics
    
    #calling getNadeoImporterLIBPath while addon is registering not allowed:
    #AttributeError: "_RestrictedContext" object has no attribute "scene"
    #return tuple "ERROR" the first few milliseconds to fix it
    #then assign list of physics to matPhysics, to read file only once
    try:    libfile =  getNadeoImporterLIBPath()
    except  AttributeError:
        return matPhysics
    
    if not libfile.endswith("Lib.txt"):
        return matPhysics
    
    libmats = nadeoLibParser()
    physics = []
    
    for envi in libmats:
        for mat in libmats[envi]:
            mat = libmats[envi][mat]
            phy = mat["PhysicsId"]
            if phy not in physics:
                physics.append(phy)
    
    #some physics are not used by nadeo but exist.
    for missingPhysic in missingPhysicsInLib: 
        if missingPhysic not in physics:
            physics.append(missingPhysic)
    
    physics.sort()
    physicsWithIcons = []
    
    for i, phy in enumerate(physics):
        icon = "FUND" if phy in favPhysicIds else "AUTO"
        physicsWithIcons.append(    (phy, phy, phy, icon, i)  )

    matPhysics = physicsWithIcons
    return matPhysics


def getMaterialLinks(self, context)->List:
    global matLinks

    if matLinks is not errorEnumProps:
        return matLinks


    try:    libfile =  getNadeoImporterLIBPath()
    except  AttributeError:
        return matLinks

    if not libfile.endswith("Lib.txt"):
        return matLinks
    
    materials    = []
    libmats      = nadeoLibParser()
    selectedEnvi = str(context.scene.tm_props.LI_materialCollection).lower()
    i = 0

    for envi in libmats:
        if envi.lower() == selectedEnvi:
            for mat in libmats[envi]:
                if mat not in materials:
                    materials.append((mat, mat, mat))
                    i += 1
            break
    
    materials.sort()
    matLinks = materials
    return matLinks


def getMaterialGameplayIds(self, context)->None:
    return [ (gpi, gpi, gpi) for gpi in tm2020GameplayIds]



#? CB = CheckBox => BoolProperty
#? LI = List     => EnumProperty
#? NU = Number   => IntProperty, FloatProperty
#? ST = String   => StringProperty

class TM_Properties_for_Panels(bpy.types.PropertyGroup):
    """general trackmania properties"""
    LI_gameType:            EnumProperty(items=getGameTypes(), name="Game", update=lambda s, c: gameTypeGotUpdated())
    ST_nadeoIniFile_MP:     StringProperty(name="", subtype="FILE_PATH",    update=lambda s, c: isNadeoImporterInstalled("ST_nadeoIniFile_MP"))
    ST_nadeoIniFile_TM:     StringProperty(name="", subtype="FILE_PATH",    update=lambda s, c: isNadeoImporterInstalled("ST_nadeoIniFile_TM"))
    ST_author:              StringProperty(name="Author", default="skyslide")
    CB_nadeoImporter:       BoolProperty("NadeoImporter installed", default=False)
    NU_nadeoImporterDL:     FloatProperty(min=0, max=100, default=0, subtype="PERCENTAGE", update=redrawPanel)
    ST_nadeoImporterDLError:StringProperty(name="Status", default="")

    #export
    LI_exportType:          EnumProperty(items=getExportTypes(),        name="Action", default=1)
    LI_exportFolderType:    EnumProperty(items=getExportFolderTypes,    name="Folder")
    ST_exportFolder_MP:     StringProperty(name="Folder", default="",   subtype="DIR_PATH") #update=lambda self, context: makeItemsPathRelative("ST_exportFolder")
    ST_exportFolder_TM:     StringProperty(name="Folder", default="",   subtype="DIR_PATH") #update=lambda self, context: makeItemsPathRelative("ST_exportFolder")
    LI_exportWhichObjs:     EnumProperty(items=getExportWhichObjects(), name="Export by?")
    LI_exportValidTypes:    EnumProperty(name="Export",      items=getExportObjTypes)
    NU_exportObjScale:      FloatProperty(name="Scale", min=0, soft_max=16)

    #convert
    NU_convertCount:        IntProperty(min=0, max=100000,  default=0, update=redrawPanel)
    NU_convertedRaw:        IntProperty(min=0, max=100000,  default=0, update=redrawPanel)
    NU_converted:           IntProperty(min=0, max=100,     default=0, subtype="PERCENTAGE", update=redrawPanel) 
    NU_convertedSuccess:    IntProperty(min=0, max=100000,  default=0, update=redrawPanel)
    NU_convertedError:      IntProperty(min=0, max=100000,  default=0, update=redrawPanel)
    ST_convertedErrorList:  StringProperty(default="",  update=redrawPanel)
    CB_showConvertPanel:    BoolProperty(default=False, update=redrawPanel)
    CB_stopAllNextConverts: BoolProperty(default=False, update=redrawPanel)
    CB_converting:          BoolProperty(default=False, update=redrawPanel)

    #uvmaps
    CB_uv_genLightMap       : BoolProperty(name="Generate Lightmap",        default=True, update=redrawPanel)
    NU_uv_angleLimitLM      : FloatProperty(name="Angle Limit",             default=r(89.0), min=0, max=r(89.0), subtype="ANGLE")
    NU_uv_islandMarginLM    : FloatProperty(name="Island Margin",           default=0.1, min=0, max=1)
    NU_uv_areaWeightLM      : FloatProperty(name="Area Weight",             default=0.0, min=0, max=1)
    CB_uv_correctAspectLM   : BoolProperty(name="Correct Aspect",           default=True, update=redrawPanel)
    CB_uv_scaleToBoundsLM   : BoolProperty(name="Scale To Bounds",          default=True, update=redrawPanel)
    
    #xml
    CB_xml_syncGridLevi     : BoolProperty(name="Sync Grid & Levi steps",   default=True)
    CB_xml_itemXMLNew       : BoolProperty(name="Use Custom",               default=True)
    CB_xml_genItemXML       : BoolProperty(name="Generate Item XML",        default=True, update=redrawPanel)
    CB_xml_genMeshXML       : BoolProperty(name="Generate Mesh XML",        default=True, update=redrawPanel)
    LI_xml_meshtype         : EnumProperty( name="Type",                    items=getMeshXMLType())
    NU_xml_scale            : FloatProperty(name="Objscales",               default=1.0, min=0, max=256, step=100)
    CB_xml_scale            : BoolProperty( name="Obj Scale",               default=False)
    CB_xml_lightPower       : BoolProperty( name="Lightpower",              default=False)
    NU_xml_lightPower       : FloatProperty(name="Lightpower",              default=1.0, min=0, max=256, step=1)
    CB_xml_lightGlobColor   : BoolProperty(name="Lightcolor",               default=False)
    NU_xml_lightGlobColor   : FloatVectorProperty(name='Lightcolor',        subtype='COLOR', min=0, max=1, step=1000, default=(0.0,0.319,0.855))
    CB_xml_lightGlobDistance: BoolProperty(name="Lightdistance",            default=False)
    NU_xml_lightGlobDistance: FloatProperty(name="Lightdistance",           default=32.0, min=0, max=256, step=1)
    LI_xml_itemtype         : EnumProperty( name="Type",            items=getItemXMLType())
    LI_xml_waypointtype     : EnumProperty( name="Waypoint",        items=getWayPointVariations())
    LI_xml_enviType         : EnumProperty( name="Envi",            items=getItemXMLCollections())
    ST_xml_author           : StringProperty(name="Author",         default="skyslide")
    NU_xml_gridAndLeviX     : FloatProperty(name="Sync X",          default=8.0, min=0, max=256, step=100, update=updateGridAndLevi)
    NU_xml_gridAndLeviY     : FloatProperty(name="Synx Y",          default=8.0, min=0, max=256, step=100, update=updateGridAndLevi)
    NU_xml_gridX            : FloatProperty(name="X Grid",          default=8.0, min=0, max=256, step=100)
    NU_xml_gridXoffset      : FloatProperty(name="X Offset",        default=0.0,  min=0, max=256, step=100)
    NU_xml_gridY            : FloatProperty(name="Y Grid",          default=8.0,  min=0, max=256, step=100)
    NU_xml_gridYoffset      : FloatProperty(name="Y Offset",        default=0.0,  min=0, max=256, step=100)
    NU_xml_leviX            : FloatProperty(name="X Levitation",    default=8.0,  min=0, max=256, step=100)
    NU_xml_leviXoffset      : FloatProperty(name="X Offset",        default=0.0,  min=0, max=256, step=100)
    NU_xml_leviY            : FloatProperty(name="Y Levitation",    default=8.0,  min=0, max=256, step=100)
    NU_xml_leviYoffset      : FloatProperty(name="Y Offset",        default=0.0,  min=0, max=256, step=100)
    CB_xml_ghostMode        : BoolProperty(name="Ghostmode",        default=False)
    CB_xml_autoRot          : BoolProperty(name="Autorot",          default=False)
    CB_xml_oneAxisRot       : BoolProperty(name="OneAxisRot",       default=False)
    CB_xml_notOnItem        : BoolProperty(name="Not on Item",      default=False)
    CB_xml_pivots           : BoolProperty(name="Pivots (ingame Q Key)",default=False)
    CB_xml_pivotSwitch      : BoolProperty(name="Pivot switch",     default=False)
    NU_xml_pivotSnapDis     : FloatProperty(name="Pivot snap distance", default=8.0,  min=0, max=256, step=100)

    #materials
    LI_materials:               EnumProperty(name="Material",       items=getMaterials, update=updateMaterialSettings)
    LI_materialAction:          EnumProperty(name="Material Action",default=0, items=getMaterialActions())
    ST_materialAddName:         StringProperty(name="Name",         default="Matname...")
    LI_materialCollection:      EnumProperty(name="Collection",     items=getMaterialCollectionTypes(), update=lambda s,c: gameTypeGotUpdated())
    CB_materialUsePhysicsId:    BoolProperty(name="Use PhysicsId",  default=False)
    LI_materialPhysicsId:       EnumProperty(name="PhysicId",       items=getMaterialPhysicIds)
    CB_materialUseGameplayId:   BoolProperty(name="Use GameplayId", default=False)
    LI_materialGameplayId:      EnumProperty(name="GameplayId",     items=getMaterialGameplayIds)
    LI_materialModel:           EnumProperty(name="Model",          items=getMaterialModelTypes())
    LI_materialLink:            EnumProperty(name="Link",           items=getMaterialLinks)
    ST_materialBaseTexture:     StringProperty(name="BaseTexture",  default="", subtype="FILE_PATH")
    NU_materialColor:           FloatVectorProperty(name='Surface Color ',  subtype='COLOR', min=0, max=1, step=1000, default=(0.0,0.319,0.855))
    LI_materialIsFromLib:       BoolProperty(name="BaseTexture",    default=True)

    #tetxtures
    LI_DL_TextureEnvi:      EnumProperty(items=getGameTextureZipFileNames(), update=redrawPanel)
    CB_DL_TexturesRunning:  BoolProperty(name="Downloading...", default=False)
    NU_DL_Textures:         FloatProperty(min=0, max=100,   default=0, subtype="PERCENTAGE", update=redrawPanel)
    ST_DL_TexturesErrors:   StringProperty(name="Status",   default="")




class TM_Properties_Generated(PropertyGroup):
    """trackmania properties generated"""
    ST_matPhysicsId :  StringProperty(name="PhysicsId",         default="Concrete")
    ST_matName :       StringProperty(name="Mat Name",          default="")
    ST_matModel:       StringProperty(name="Mat Model",         default="TDSN")
    ST_matBTex :       StringProperty(name="Mat BaseTexture",   default="StadiumPlatform")
    CB_matBool :       BoolProperty(name="mat name not set yet",default=False)
    

class TM_Properties_Pivots(PropertyGroup):
    """trackmania properties generated for pivots (item xml)"""
    NU_pivotX   : FloatProperty(name="X", default=0.0, min=-1024, max=1024, soft_min=-8, soft_max=8, step=10)
    NU_pivotY   : FloatProperty(name="Y", default=0.0, min=-1024, max=1024, soft_min=-8, soft_max=8, step=10)
    NU_pivotZ   : FloatProperty(name="Z", default=0.0, min=-1024, max=1024, soft_min=-8, soft_max=8, step=10)
    
    
class TM_ItemConvertStatus(PropertyGroup):
    """trackmania properties for the convert progress, status"""
    ST_fbx_toConvert        : StringProperty(name="fbxname", default="")
    CB_fbx_convertFailed    : BoolProperty(name="status",   default=False)
    CB_fbx_convertDone      : BoolProperty(name="status",   default=False)



    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    