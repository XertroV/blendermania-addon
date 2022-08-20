import bpy
import math

from ..utils.Dotnet import (
    DotnetInt3,
    DotnetItem,
    DotnetBlock,
    DotnetVector3,
    run_place_objects_on_map,
    get_block_dir_for_angle,
)
from ..utils.BlenderObjects import duplicate_object_to
from ..utils.Functions import (
    is_file_exist,
    get_global_props,
    set_active_object,
    get_game_doc_path_items,
    is_game_trackmania2020,
)
from ..utils.Constants import (
    MAP_OBJECT_ITEM,
    MAP_OBJECT_BLOCK,
)

def _make_object_name(path: str, type: str) -> str:
    items_path = get_game_doc_path_items()

    prefix = "TM" if is_game_trackmania2020() else "MP"
    short_name = path.replace(items_path, "")
    return f"{prefix}_{type.upper()}: {short_name}"

def get_selected_map_objects() -> list[bpy.types.Object]:
    res:list[bpy.types.Object] = []

    for obj in bpy.context.selected_objects:
        if "tm_map_object_kind" in obj:
            res.append(obj)

    return res

def create_update_map_object():
    tm_props                         = get_global_props()
    map_coll:bpy.types.Collection    = tm_props.PT_map_collection
    object_item:bpy.types.Object     = tm_props.PT_map_object.object_item
    object_type:str                  = tm_props.PT_map_object.object_type
    object_path:str                  = tm_props.PT_map_object.object_path
    items_path                       = get_game_doc_path_items()
    selected_objects                 = get_selected_map_objects()
    
    if not map_coll:
        return "No map collection selected"

    obj_to_update:bpy.types.Object = None

    if items_path in object_path:
        if not is_file_exist(object_path):
            return f"There is no item with path {object_path}. You have to export it first"

    if len(object_path) == 0:
        return f"Name/Path can not be empty"


    # update path on selected objects if there is more than one selected
    if len(selected_objects) > 1:
        for obj in selected_objects:
            obj.name = _make_object_name(object_path, object_type)
            obj["tm_map_object_path"] = object_path

        set_active_object(object_item)
    else:
        # update object if it's already map_object else create a new one
        if object_item and "tm_map_object_kind" in object_item:
            obj_to_update = object_item
        else:
            if not object_item:
                bpy.ops.mesh.primitive_cube_add(size=32, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
                obj_to_update = bpy.context.active_object
            else:
                obj_to_update = duplicate_object_to(object_item, map_coll, True)
        
        obj_to_update.name = _make_object_name(object_path, object_type)
        obj_to_update["tm_map_object_kind"] = object_type
        obj_to_update["tm_map_object_path"] = object_path

        set_active_object(obj_to_update)

def validate_map_collection() -> str:
    tm_props                         = get_global_props()
    map_coll:bpy.types.Collection    = tm_props.PT_map_collection
    items_path                       = get_game_doc_path_items()
    
    if not map_coll:
        return "No map collection!"

    for obj in map_coll.all_objects:
        obj:bpy.types.Object = obj

        if "tm_map_object_kind" not in obj or "tm_map_object_path" not in obj:
            return f"Map collection contains invalid object: {obj.name}"

        if obj["tm_map_object_kind"] == MAP_OBJECT_BLOCK:
            if min(obj.location) < 0:
                return f"Block position can not be negative! Object: {obj.name}"

            if obj.rotation_euler[0] != 0 or obj.rotation_euler[1] != 0:
                return f"Only rotation on Z axis supported! Object: {obj.name}"
            
            if (round(math.degrees(obj.rotation_euler[2]))) % 90 != 0:
                return f"Rotation on Z must be multiple of 90deg! Object: {obj.name}"
        
        if obj["tm_map_object_kind"] == MAP_OBJECT_ITEM:
            if items_path in obj["tm_map_object_path"] and not is_file_exist(obj["tm_map_object_path"]):
                return f"Item with path: {obj['tm_map_object_path']} does not exist. Object name: {obj.name}"

def export_map_collection() -> str:
    err = validate_map_collection()
    if err: return err

    tm_props                         = get_global_props()
    map_coll:bpy.types.Collection    = tm_props.PT_map_collection
    map_path:str                     = tm_props.ST_map_filepath
    use_overwrite:bool               = tm_props.CB_map_use_overwrite
    map_suffix:str                   = tm_props.ST_map_suffix
    clean_blocks:bool                = False#tm_props.CB_map_clean_blocks
    clean_items:bool                 = tm_props.CB_map_clean_items
    items_path                       = get_game_doc_path_items()
    dotnet_items                     = list[DotnetItem]()
    dotnet_blocks                    = list[DotnetBlock]()

    if len(map_suffix.strip()) == 0:
        map_suffix = "_modified"

    for obj in map_coll.all_objects:
        obj:bpy.types.Object = obj

        if obj["tm_map_object_kind"] == MAP_OBJECT_ITEM:
            name = obj["tm_map_object_path"]
            if items_path in name:
                name = "Items/"+name.replace(items_path, "")
            else:
                name = name.replace(".Item", "").replace(".Gbx", "")

            dotnet_items.append(DotnetItem(
                Name=name,
                Path=obj["tm_map_object_path"] if items_path in name else "",
                Position=DotnetVector3(obj.location[1], obj.location[2]+8, obj.location[0]),
                Rotation=DotnetVector3(obj.rotation_euler[2], obj.rotation_euler[1], obj.rotation_euler[0]),
                Pivot=DotnetVector3(0),
            ))
        elif obj["tm_map_object_kind"] == MAP_OBJECT_BLOCK:
            dotnet_blocks.append(DotnetBlock(
                Name=obj["tm_map_object_path"],
            Direction=get_block_dir_for_angle(math.degrees(obj.rotation_euler[2])),
                Position=DotnetInt3(int(int(obj.location[1])/32), int(int(obj.location[2])/32)+9, int(int(obj.location[0])/32)),
            ))

    return run_place_objects_on_map(
        map_path,
        dotnet_blocks,
        dotnet_items,
        use_overwrite,
        map_suffix,
        clean_blocks,
        clean_items,
    )