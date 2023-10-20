import math
import bpy, bmesh
import subprocess
from typing import List

from ..utils.Constants import ADDON_ITEM_FILEPATH_CAR_TRACKMANIA2020_STADIUM, EDITORTRAILS_OBJECT_NAME

from ..operators.OT_Items_Export import close_convert_panel

from ..utils.Functions import (
    debug,
    deselect_all_objects,
    editmode,
    get_addon_assets_path,
    objectmode,
    select_obj,
    set_active_object
)


def focus_blender() -> bool:
    try:
        subprocess.Popen([
            get_addon_assets_path() + "/convert_report/focus_blender.bat",
            "blender"
        ])
        return True
    
    except Exception as err:
        return False

    finally:
        close_convert_panel()



class EditorTrail:
    path_x: float
    path_y: float
    path_z: float
    
    velo_x: float
    velo_y: float
    velo_z: float

    quat_x: float
    quat_y: float
    quat_z: float
    quat_w: float

    time: float


def zxy_to_xyz(vec: List[float]) -> List[float]:
    return [vec[2], vec[0], vec[1]]



def update_editortrails(trails: List[EditorTrail]) -> bool:
    can_run = bpy.context.mode == "OBJECT"
    if can_run:
        debug("update editortrails")
        return _update_editortrails(trails)
    
    # bpy.ops.??() or in editmode will crash blender, fix things before:
    def timed_update_editortrails():
        debug("update editortrails timed")
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        _update_editortrails(trails)
        return None
    
    # should have correct access to bpy.context & bpy.ops
    bpy.app.timers.register(timed_update_editortrails, first_interval=1)

    return True
        

def _update_editortrails(trails: List[EditorTrail]) -> bool:
    curve = bpy.data.curves.get(EDITORTRAILS_OBJECT_NAME, None)
    if curve:
        bpy.data.curves.remove(curve)

    coords_list = []

    for i, trail in enumerate(trails):
        coords_list.append(
            zxy_to_xyz([
                trail.path_x,
                trail.path_y,
                trail.path_z,
            ])
        )

    curve = bpy.data.curves.new(EDITORTRAILS_OBJECT_NAME, 'CURVE')
    curve.dimensions = '3D'

    spline = curve.splines.new(type='NURBS')
    spline.points.add(len(coords_list) - 1) 

    for point, new_coord in zip(spline.points, coords_list):
        point.co = (new_coord + [1.0])  # (add nurbs 

    obj = bpy.data.objects.new(EDITORTRAILS_OBJECT_NAME, curve)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj

    deselect_all_objects()
    
    
    # animate car
    def animate():
        add_trail_car_animation(trails)
    bpy.app.timers.register(animate, first_interval=1)

    return True


def add_trail_car_animation(trails: List[EditorTrail]) -> None:
    bpy.ops.import_scene.fbx(filepath=ADDON_ITEM_FILEPATH_CAR_TRACKMANIA2020_STADIUM)
    
    bpy.context.scene.render.fps = 60 * 100

    obj = bpy.context.selected_objects[0]
    obj.rotation_euler = [
        math.radians(90),
        0,
        math.radians(90),
    ]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    obj.rotation_mode = "QUATERNION" 
    # obj.rotation_mode = "ZXY"

    for i, trail in enumerate(trails):
        obj.location = zxy_to_xyz([
            trail.path_x, 
            trail.path_y, 
            trail.path_z
        ])
        obj.rotation_quaternion = [        
            trail.quat_w,
            trail.quat_x,
            -trail.quat_y,
            trail.quat_z,
        ]

        


        frame = int(trail.time * 100)
        bpy.context.scene.frame_end = frame
        debug(f"{frame} - q={[trail.quat_x, trail.quat_y, trail.quat_z, trail.quat_w]} - quat={obj.rotation_quaternion}")
        
        obj.keyframe_insert(data_path="location", frame=frame)
        obj.keyframe_insert(data_path="rotation_quaternion", frame=frame) 
