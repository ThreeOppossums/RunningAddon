bl_info = {
    "name": "RunningAddon",
    "author": "ThreeOppossums",
    "version": (1, 0),
    "blender": (4, 5, 0),
    "location": "View3D > N-Panel / Properties > Scene",
    "description": "The Running Addon - Single File Version",
    "category": "Animation",
}

import bpy
from bpy_extras import view3d_utils
import os
import re
from mathutils import Vector
import math


# --- GLOBAL VARIABLES ---
filepath = ""
animation_names = []
print(animation_names)

try:
    with open(os.path.join(bpy.path.abspath(filepath), "Animation_Names.txt"), 'r', encoding='utf-8') as file:
        animation_names = file.read().splitlines()
except Exception as e:
    try:
        with open(os.path.join(bpy.path.abspath(bpy.context.scene.filepath), "Animation_Names.txt"), 'r', encoding='utf-8') as file:
            animation_names = file.read().splitlines()
    except Exception as e:
        print({'ERROR'}, f"Could not get File Animation Names. Please refresh your Filepath.")


# --- FUNCTIONS (GLOBAL) ---
def get_files():
    global animation_names 
    global filepath  
    scene = bpy.context.scene
    if not scene.filepath:
        return []
    Notes_txt_path = bpy.path.abspath("//Notes.txt")
    
    if not os.path.exists(Notes_txt_path):
        with open(Notes_txt_path, 'w', encoding='utf-8') as f: f.write("")

    with open(Notes_txt_path, 'r', encoding='utf-8') as file:
        Notes_txt = file.read().splitlines()
    try:
        if len(Notes_txt) > 0:
            Notes_txt[0] = "Path_to_Folder;" + scene.filepath
        else:
            Notes_txt.append("Path_to_Folder;" + scene.filepath)
    except Exception as e:
        Notes_txt = [scene.filepath] 
    
    filepath = Notes_txt[0]
    
    with open(Notes_txt_path, 'w', encoding='utf-8') as file:
        for line in Notes_txt:
            file.write(f"{line}\n")

    path = os.path.join(bpy.path.abspath(filepath), "Animation_Names.txt")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file:
            animation_names = file.read().splitlines()
    return animation_names


def get_mouse_3d_position(self, context, event):
    print("called get_mouse_ed_position")
    region = context.region
    rv3d = context.space_data.region_3d
    coord = (event.mouse_region_x, event.mouse_region_y)

    view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    depsgraph = context.evaluated_depsgraph_get()
    
    success, location, normal, index, obj, matrix = context.scene.ray_cast(
        depsgraph, ray_origin, view_vector
    )

    if success:
        return location
    
    return None

def show_message(message = "", title = "Info", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def update_class_selection(self, context):
    scene = context.scene
    class_name = ""
    armature = scene.armature_object_main
    armature_name = armature.name.lower()
    if "scout" in armature_name:
        class_name = "SCOUT"
    elif "soldier" in armature_name:
        class_name = "SOLDIER"
    elif "pyro" in armature_name:
        class_name = "PYRO"
    elif "demo" in armature_name:
        class_name = "DEMO"
    elif "heavy" in armature_name:
        class_name = "HEAVY"
    elif "engineer" in armature_name:
        class_name = "ENGINEER"
    elif "medic" in armature_name:
        class_name = "MEDIC"
    elif "sniper" in armature_name:
        class_name = "SNIPER"
    elif "spy" in armature_name:
        class_name = "SPY"
    else:
        class_name = "UNDEFINED"
    scene.class_name = class_name
    return class_name
                
# --- OPERATORS ---

# --> GLobal

class OBJECT_OT_info_button(bpy.types.Operator):
    bl_idname = "object.info_button"
    bl_label = f"Press for inormation"
    def execute(self, context):
        Info = "Please set your Framerate to 24 so every animation works with its intended speed. Also please set your Units to 'Metric', so that the Addon can calculate the range as intended."
        show_message(Info, "Info", 'INFO')
        return {'FINISHED'}

# --> Dev

class SCENE_OT_set_animation_name(bpy.types.Operator):
    bl_idname = "scene.set_animation_name"
    bl_label = "Set Name"
    animation_name: bpy.props.StringProperty()
    def execute(self, context):
        context.scene.animation_name = self.animation_name
        return {'FINISHED'}
    
# --> Main
class SCENE_OT_set_path_name(bpy.types.Operator):
    bl_idname = "scene.set_path_name"
    bl_label = "Set Path Name"
    path_name: bpy.props.StringProperty()

    def execute(self, context):
        clean_name = self.path_name.replace("Path_", "")
        context.scene.path_name_for_create = clean_name
        return {'FINISHED'}

    
# --- BUTTONS ---

# --> Dev

# --> Main
class OBJECT_OT_refresh_animation_names(bpy.types.Operator):
    bl_idname = "object.refresh_animation_names"
    bl_label = "update animation names"
    bl_description = "update animation names"
    
    def execute(self, context):
        get_files()
        return {'FINISHED'}

class OBJECT_OT_select_position(bpy.types.Operator):
    bl_idname = "object.select_positions"
    bl_label = "Select pathway"
    bl_description = "Creates marker (empties) for the path"
    placed_markers = []
    sub_collection = ""
    
    @staticmethod
    def sort_markers(obj):
        name = obj.name.lower()
        if "start" in name: return (0, name)
        elif "end" in name: return (2, name)
        else: return (1, name)
    
    def invoke(self, context, event):
        scene = context.scene
        self.placed_markers = []
        path_name = scene.path_name_for_create
        
        if path_name:
            existing_markers = [
                obj for obj in scene.objects 
                if obj.name.startswith(path_name) and obj.name.endswith("_marker")]
            
            if existing_markers:
                existing_markers.sort(key=self.sort_markers)
                
                for marker in existing_markers:
                    self.placed_markers.append(marker)
                
                last_marker = self.placed_markers[-1]
                markers_count = len(self.placed_markers) - 1
                last_marker.name = f"{path_name}_{markers_count}_marker"
                
                self.report({'INFO'}, f"Loaded {len(existing_markers)} existing markers.")
        
        self.create_position_markers_collection(context)
        self.create_sub_collection(context) 
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def create_position_markers_collection(self, context):
        collection_name = "Position_Markers"
        if collection_name not in bpy.data.collections:
            new_col = bpy.data.collections.new(collection_name)
            context.scene.collection.children.link(new_col)
        return bpy.data.collections.get(collection_name)

    def create_sub_collection(self, context):
        scene = context.scene
        path_name = scene.path_name_for_create
        if not path_name:
             self.report({'INFO'}, f"Pleace select a pathname.")
             return {'CANCELLED'}
        scene = context.scene
        if scene.armature_object_main:
            name = f"{path_name}_collection"
            self.sub_collection = name
            if name not in bpy.data.collections:

                new_sub = bpy.data.collections.new(name)
                parent_col = bpy.data.collections.get("Position_Markers")
                if parent_col:
                    if name not in parent_col.children:
                        parent_col.children.link(new_sub)
                else:
                    if name not in scene.collection.children:
                        scene.collection.children.link(new_sub)
            return bpy.data.collections.get(name)
        return None

    def modal(self, context, event):
        scene = context.scene
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        path_name = scene.pathname
        if not path_name:
            self.report({'INFO'}, f"Pleace select a pathname.")
            return {'CANCELLED'}
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            position = get_mouse_3d_position(self, context, event)
                       
            if position:
                marker_type = "start" if not self.placed_markers else str(len(self.placed_markers))
                full_name = f"{path_name}_{marker_type}_marker"

                new_marker = self.create_marker(context, position, full_name)
                self.placed_markers.append(new_marker)

                self.report({'INFO'}, f"Placed Marker: {marker_type}")

            return {'RUNNING_MODAL'}

        if event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            if self.placed_markers:
                last_obj = self.placed_markers.pop()
                if last_obj:
                    bpy.data.objects.remove(last_obj, do_unlink=True)
                    self.report({'INFO'}, "Removed last marker")
            return {'RUNNING_MODAL'}
        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            if self.placed_markers and len(self.placed_markers) >= 2:
                end_marker = self.placed_markers[-1]
                end_marker.name = f"{path_name}_end_marker"
                self.report({'INFO'}, "Finished")
                return {'FINISHED'}
            if self.placed_markers and len(self.placed_markers) < 2:
                self.report({'WARNING'}, "Place at least two markers!")
                return {'FINISHED'}

            self.report({'WARNING'}, "No Markers Placed!")
            return {'RUNNING_MODAL'}
        if event.type == 'ESC' and event.value == 'PRESS':
            if self.placed_markers:
                for element in self.placed_markers:
                    bpy.data.objects.remove(element, do_unlink=True)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}
    
    def create_marker(self, context, position, marker_name):
        print("called create_marker")
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=position, scale=(1, 1, 1))
        obj = context.active_object
        obj.name = marker_name
        target_col = bpy.data.collections.get(self.sub_collection)
        if not target_col:
            target_col = bpy.data.collections.get("Position_Markers")

        if target_col:
            if obj.name not in target_col.objects:
                target_col.objects.link(obj)
                for c in obj.users_collection:
                    if c != target_col:
                        c.objects.unlink(obj)
        return obj
    
    def execute(self, context):
        return self.invoke(context, None)

class OBJECT_OT_attempt_pos_rot_fix(bpy.types.Operator):
    bl_idname = "object.attempt_pos_rot_fix"
    bl_label = "attempt fix"
    
    def execute(self,context):
        scene = context.scene
        classes_for_two = ['scout', 'soldier', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy']
        selected_class = scene.class_name
        if scene.use_own_fixdata == True:
            return self.fix_self(context)
        if selected_class.lower() in classes_for_two:
            return self.fix_rotation_two(context)
        if selected_class.lower() == 'pyro':
            return self.fix_rotation_one(context)
        return {'CANCELLED'}
        
    def fix_self(self, context):
        scene = context.scene
        x = scene.datax
        y = scene.datay
        z = scene.dataz
        armature = scene.armature_object_main
        
        pre_change = armature.rotation_mode
        if armature.rotation_mode != 'XYZ':
            armature.rotation_mode = 'XYZ'
        armature.rotation_euler.x = math.radians(int(x))
        armature.rotation_euler.y = math.radians(int(y))
        armature.rotation_euler.z = math.radians(int(z))
        armature.rotation_mode = pre_change
        return {'FINISHED'}
    
    def fix_rotation_one(self, context): #pyro
        scene = context.scene
        armature = scene.armature_object_main
        
        pre_change = armature.rotation_mode
        if armature.rotation_mode != 'XYZ':
            armature.rotation_mode = 'XYZ'
        armature.rotation_euler.x = math.radians(-90)
        armature.rotation_euler.y = math.radians(0)
        armature.rotation_euler.z = math.radians(-90)
        armature.rotation_mode = pre_change
        return {'FINISHED'}
    
    def fix_rotation_two(self, context): #scout_soldier
        scene = context.scene
        armature = scene.armature_object_main
        
        pre_change = armature.rotation_mode
        if armature.rotation_mode != 'XYZ':
            armature.rotation_mode = 'XYZ'
        armature.rotation_euler.x = math.radians(0)
        armature.rotation_euler.y = math.radians(0)
        armature.rotation_euler.z = math.radians(-90)
        armature.rotation_mode = pre_change
        return {'FINISHED'}

# --> General
    
class OBJECT_OT_refresh_button(bpy.types.Operator):
    bl_idname = "object.refresh_button"
    bl_label = "Refresh"
    def execute(self, context):
        get_files()
        self.report({'INFO'}, "Updated animation_names")
        return {'FINISHED'}


# --- MAIN FUNCTIONS ---

# --> Dev

class OBJECT_OT_animation_to_file(bpy.types.Operator):
    bl_idname = "object.animation_to_file"
    bl_label = "animation to file"
    bl_description = "Create a folder and a txt file at the selected path"
    bl_options = {'REGISTER', 'UNDO'}
    
    def add_animation_name_to_list(self, context):
        scene = context.scene
        new_name = scene.animation_name
        if not new_name:
            return
        folder_location = bpy.path.abspath(scene.filepath)
        txt_file_path = os.path.join(folder_location, "Animation_Names.txt")
        existing_names = []
        if os.path.exists(txt_file_path):
            with open(txt_file_path, 'r', encoding='utf-8') as file:
                existing_names = file.read().splitlines()
        if new_name not in existing_names:
            existing_names.append(new_name)
            existing_names.sort()
            get_files()
            try:
                with open(txt_file_path, 'w', encoding='utf-8') as file:
                    for element in existing_names:
                        file.write(element + "\n")
                self.report({'INFO'}, f"Name '{new_name}' succesfully added.")
            except Exception as e:
                self.report({'ERROR'}, f"Error at writing name: {e}")
        else:
            self.report({'INFO'}, f"name '{new_name}' already in the list.")

    
    def execute(self, context):
        scene = bpy.context.scene
        get_files()
        
        armature = context.scene.armature_object
        if armature and armature.type == 'ARMATURE':
            bones = [bone.name for bone in armature.data.bones]
            if bones:
                start_frame = context.scene.first_frame_input
                end_frame = context.scene.last_frame_input
                return self.create_path(context, start_frame, end_frame, bones)
            else:
                self.report({'ERROR'}, "could not locate bones of armature")
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "No valid armature selected")
            return {'CANCELLED'}

    def create_path(self, context, start_frame, end_frame, bones):
        scene = bpy.context.scene
        animation_name = scene.animation_name

        if animation_name not in animation_names:
            self.add_animation_name_to_list(context)

        animation_name_split = animation_name.split('_')
        
        category = animation_name_split[0]
        name = animation_name_split[1]
        class_name = ""

        arm_obj_name = scene.armature_object.name.lower()

        if "scout" in arm_obj_name:
            class_name = "scout"
        elif "soldier" in arm_obj_name:
            class_name = "soldier"
        elif "pyro" in arm_obj_name:
            class_name = "pyro"
        elif "demo" in arm_obj_name:
            class_name = "demo"
        elif "heavy" in arm_obj_name:
            class_name = "heavy"
        elif "engineer" in arm_obj_name:
            class_name = "engineer"
        elif "medic" in arm_obj_name:
            class_name = "medic"
        elif "sniper" in arm_obj_name:
            class_name = "sniper"
        elif "spy" in arm_obj_name:
            class_name = "spy"
        else:
            class_name = "undefined"

        folder_location = scene.filepath
        if not folder_location:
            self.report({'ERROR'}, "No folder path specified. Please specify a path")
            return {'CANCELLED'}

        current_path = folder_location
        for folder in [category, class_name, name, "bones"]:
            current_path = os.path.join(current_path, folder)
            if not os.path.exists(current_path):
                try:
                    os.makedirs(current_path)
                    self.report({'INFO'}, f"Folder created: {current_path}")
                except Exception as e:
                    self.report({'ERROR'}, f"Could not create folder: {e}")
                    return {'CANCELLED'}
        INFO_txt_path = os.path.join(folder_location, category, class_name, name)
        return self.create_INFO(context, start_frame, end_frame, bones, current_path, INFO_txt_path)
    
    def create_INFO(self, context, start_frame, end_frame, bones, current_path, INFO_txt_path):
        scene = bpy.context.scene
        armature = scene.armature_object
        frame_start = scene.first_frame_input
        frame_end = scene.last_frame_input
        
        scene.frame_set(start_frame)
        context.view_layer.update()
        pos_start_frame = armature.location.copy()
        
        scene.frame_set(end_frame)
        context.view_layer.update()
        pos_end_frame = armature.location.copy()
        
        diff_x = abs(pos_end_frame.x - pos_start_frame.x)
        diff_y = abs(pos_end_frame.y - pos_start_frame.y)
        diff_z = abs(pos_end_frame.z - pos_start_frame.z)
        
        max_diff = max(diff_x, diff_y, diff_z)
        
        if max_diff == diff_x:
            MOVERANGE = "MOVERANGEDEBUG" + " " + str(pos_end_frame.x - pos_start_frame.x)
        elif max_diff == diff_y:
            MOVERANGE = "MOVERANGEDEBUG" + " " + str(pos_end_frame.y - pos_start_frame.y)
        else:
            MOVERANGE = "MOVERANGEDEBUG" + " " + str(pos_end_frame.z - pos_start_frame.z)
        
        FRAMERANGE = "FRAMERANGE" + " " + str(frame_end - frame_start + 1)
        FRAMERATE = "FRAMERATE" + " " + str(scene.render.fps)
        DIMENSIONX = "DIMENSIONX" + " " + str(armature.dimensions.x)
        DIMENSIONY = "DIMENSIONY" + " " + str(armature.dimensions.y)
        DIMENSIONZ = "DIMENSIONZ" + " " + str(armature.dimensions.z)
        
        INFO_txt = []
        INFO_txt.append(MOVERANGE)
        INFO_txt.append(FRAMERANGE)
        INFO_txt.append(FRAMERATE)
        INFO_txt.append(DIMENSIONX)
        INFO_txt.append(DIMENSIONY)
        INFO_txt.append(DIMENSIONZ)
        
        framerange = end_frame - start_frame + 1
        
        scene.frame_set(start_frame)
        context.view_layer.update()
        pos_prev = armature.location.copy()
        
        for i in range(framerange):
            current_f = start_frame + i
            scene.frame_set(current_f)
            context.view_layer.update()
            pos_current = armature.location.copy()
            
            if i == 0:
                MOVERANGE = "MOVERANGE STARTFRAME"
            else:
                diff = pos_current - pos_prev
                diff_abs = [abs(diff.x), abs(diff.y), abs(diff.z)]
                max_diff = max(diff_abs)
            
                if max_diff == diff_abs[0]: 
                    MOVERANGE = f"MOVERANGE {diff.x:.15f}"
                elif max_diff == diff_abs[1]: 
                    MOVERANGE = f"MOVERANGE {diff.y:.15f}"
                else:
                    MOVERANGE = f"MOVERANGE {diff.z:.15f}"
            
            INFO_txt.append(MOVERANGE)
            pos_prev = pos_current.copy()
        
        txt_file_path = os.path.join(INFO_txt_path, "INFO.txt")
        
        try:
            with open(txt_file_path, 'w', encoding='utf-8') as file:
                for element in INFO_txt:
                    file.write(element + "\n")
            self.report({'INFO'}, "Wrote Data to INFO.txt")
        except Exception as e:
            self.report({'ERROR'}, f"Error: {e}")
        
        framerange = FRAMERANGE
        return self.write_bones_to_file(context, start_frame, end_frame, bones, current_path, framerange)
    
    
    def write_bones_to_file(self, context, start_frame, end_frame, bone_names, current_path, framerange):
        scene = context.scene
        armature = scene.armature_object

        for bone_name in bone_names:
            bone_file_DATA = []
        
            if bone_name not in armature.pose.bones:
                self.report({'ERROR'}, f"Bone {bone_name} nicht gefunden!")
                continue
        
            bone = armature.pose.bones[bone_name]

            for i, f in enumerate(range(start_frame, end_frame + 1)):
                scene.frame_set(f)
            
                loc_x = f"LOCATIONX {bone.location.x:.15f}"
                loc_y = f"LOCATIONY {bone.location.y:.15f}"
                loc_z = f"LOCATIONZ {bone.location.z:.15f}"

                if bone.rotation_mode != 'QUATERNION':
                    bone.rotation_mode = 'QUATERNION'

                rot_w = f"ROTATIONW {bone.rotation_quaternion.w:.15f}"
                rot_x = f"ROTATIONX {bone.rotation_quaternion.x:.15f}"
                rot_y = f"ROTATIONY {bone.rotation_quaternion.y:.15f}"
                rot_z = f"ROTATIONZ {bone.rotation_quaternion.z:.15f}"
                
                frame_write = i + 1
                bone_file_DATA.append(f"FRAME {frame_write}")
                bone_file_DATA.append(loc_x)
                bone_file_DATA.append(loc_y)
                bone_file_DATA.append(loc_z)
                bone_file_DATA.append(rot_w)
                bone_file_DATA.append(rot_x)
                bone_file_DATA.append(rot_y)
                bone_file_DATA.append(rot_z)
                bone_file_DATA.append("")

            file_name = f"{bone_name.upper()}_DATA.txt"
            full_file_path = os.path.join(current_path, file_name)

            try:
                with open(full_file_path, 'w', encoding='utf-8') as f_out:
                    for line in bone_file_DATA:
                        f_out.write(line + "\n")
                self.report({'INFO'}, f"Saved: {file_name}")
            except Exception as e:
                self.report({'ERROR'}, f"Write Error: {e}")

        return {'FINISHED'}
        
        
        
# --> Main
class OBJECT_OT_create_path(bpy.types.Operator):
    bl_idname = "object.create_path"
    bl_label = "Create Path"
    bl_description = "Creates path"
    bl_options = {'REGISTER', 'UNDO'}

    class_name = ""
    category = ""
    type = ""
    path_to_animation = ""
    
    @staticmethod
    def sort_markers(obj):
        name = obj.name.lower()
        if "start" in name: return (0, name)
        elif "end" in name: return (2, name)
        else: return (1, name)

    def execute(self, context):
        return self.get_marker_positions(context)
    

    def get_marker_positions(self, context):
        scene = context.scene
        path_name = scene.path_name_for_create
        
        col_markers = [col for col in bpy.data.collections if path_name.lower() in col.name.lower()]
        if not col_markers:
            self.report({'ERROR'}, f"Didn't find pathmarkers {path_name}")
            return {'CANCELLED'}

        markers = [obj for obj in col_markers[0].objects if obj.type == 'EMPTY']
        markers.sort(key=self.sort_markers)
        
        if len(markers) < 2:
            self.report({'ERROR'}, "Not enogh markers found!")
            return {'CANCELLED'}

        return self.calculate_distances(context, markers)
    
    def calculate_distances(self, context, markers):
        distances_list = []
        summed_distance = 0
        
        for i in range(len(markers)-1):
            loc1 = markers[i].matrix_world.to_translation()
            loc2 = markers[i+1].matrix_world.to_translation()
            distance = (loc2 - loc1).length
            summed_distance += distance
            distances_list.append(distance)
            
        return self.create_lines(context, distances_list, summed_distance, markers)
    
    def create_lines(self, context, distances_list, summed_distance, markers):
        scene = context.scene
        path_name = scene.path_name_for_create
        registry = scene.Curves_Items
        new_storage = registry.add()
        new_storage.name = path_name
        
        for i, dist in enumerate(distances_list):
            vec = markers[i+1].location - markers[i].location
            item = new_storage.data_list.add()
            item.value = f"LINE {i} {dist} {vec.x};{vec.y};{vec.z}"
            
        return self.create_point_on_lines(context, distances_list, summed_distance, markers)
        
    def create_point_on_lines(self, context, distances_list, summed_distance, markers):
        scene = context.scene
        curve_type = scene.curve_type
        curve_factor = scene.curve_slider / 10
        
        if curve_factor == 0 and curve_type == "BEZIER":
            curve_factor = 0.01
        
        curve_points = []
        for i in range(1, len(markers) - 1):
            curr = markers[i].location
            prev = markers[i-1].location
            nxt = markers[i+1].location
            
            p1 = curr + (prev - curr).normalized() * curve_factor
            p2 = curr + (nxt - curr).normalized() * curve_factor
            curve_points.extend([p1, p2])
            
        return self.generate_curve(context, curve_points, markers)

    def generate_curve(self, context, curve_points, markers):
        scene = context.scene
        path_name = scene.path_name_for_create
        col_name = "RunningAddonPaths"
        if col_name not in bpy.data.collections:
            path_col = bpy.data.collections.new(col_name)
            scene.collection.children.link(path_col)
        else:
            path_col = bpy.data.collections[col_name]

        points = [markers[0].location] + curve_points + [markers[-1].location]
        
        curve_data = bpy.data.curves.new(name=f"Data_{path_name}", type='CURVE')
        curve_data.dimensions = '3D'

        if scene.curve_type == "BEZIER":
            spline = curve_data.splines.new(type='BEZIER')
            spline.bezier_points.add(len(points) - 1)
            for i, pos in enumerate(points):
                bp = spline.bezier_points[i]
                bp.co = pos
                bp.handle_left_type = bp.handle_right_type = 'AUTO'
        else:
            spline = curve_data.splines.new(type='POLY')
            spline.points.add(len(points) - 1)
            for i, pt in enumerate(points):
                spline.points[i].co = (pt.x, pt.y, pt.z, 1.0)

        obj_name = f"Path_{path_name}"
        if obj_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)
            
        new_curve = bpy.data.objects.new(obj_name, curve_data)
        path_col.objects.link(new_curve)
            
        self.report({'INFO'}, f"succesfully created path '{path_name}'")
        
        return {'FINISHED'}
        


class OBJECT_OT_create_animation(bpy.types.Operator):
    bl_idname = "object.create_animation"
    bl_label = "Create Animation"
    bl_description = "Creates a path for your animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    path_to_animation = ""
    current_path = ""
    path_to_animaion = ""
    
    def execute(self, context):
        self.path_to_animation, self.current_path = self.get_animation_context(context)
        return self.animate_along_path(context)
    
    def get_animation_context(self, context):
        scene = context.scene
        armature = scene.armature_object_main
        filepath = scene.filepath
        
        if not armature:
            self.report({'ERROR'}, "No armature selected!")
            return {'CANCELLED'}

        if not scene.path_name_for_create:
            self.report({'ERROR'}, "Please enter a valid pathname")
            return {'CANCELLED'}
        
        path_name = scene.pathname
        arm_obj_name = armature.name.lower()
        animation_name = scene.animation_name
        animation_name_split = animation_name.split('_')
        
        filepath = scene.filepath
        category = animation_name_split[0].lower() if len(animation_name_split) > 0 else "undefined"
        type = animation_name_split[1].upper() if len(animation_name_split) > 1 else "undefined"

        class_name = scene.class_name.lower()
        
        path_to_animation = os.path.abspath(os.path.join(filepath, category, class_name, type))
        current_path = os.path.abspath(os.path.join(path_to_animation, "bones"))
        
        return (path_to_animation, current_path)
        
    def animate_along_path(self, context):
        scene = context.scene
        frame_start = scene.start_frame_input
        frame_end = scene.end_frame_input

        if scene.create_movement == False:
            return self.validate_animation_files(context, frame_start, frame_end)
        
        scene = context.scene
        INFO_content = []
        movement_ranges = []
        path_name = scene.path_name_for_create
        armature = scene.armature_object_main
        movement_ranges_extracted = []
        curve_obj = bpy.data.objects.get(f"Path_{path_name}")
        spline = curve_obj.data.splines[0]
        move_type = scene.move_type
        
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = curve_obj
        bpy.ops.object.mode_set(mode='OBJECT')
        curve = bpy.data.objects.get(f"Path_{path_name}")
        
        try: 
            with open(os.path.abspath(os.path.join(self.path_to_animation, "INFO.txt")), 'r', encoding="utf-8") as file:
                INFO_content = file.read().splitlines()
        except Exception as e:
            self.report({'ERROR'}, str(e))
            
        movement_ranges = [line.strip() for line in INFO_content if "MOVERANGE" in line]
        for element in movement_ranges:
            try:
                range_value = element.split()[1]
                movement_ranges_extracted.append(float(range_value))
            except ValueError:
                continue
        
        if frame_end == 0 or frame_end == 1 or frame_end == frame_start:
            if movement_ranges_extracted:
                mean_range = sum(movement_ranges_extracted) / len(movement_ranges_extracted)
                path_length = self.get_path_length(context, spline, curve)
                frame_end = frame_start + path_length / mean_range
        
        if frame_start < 0:
            frame_start = frame_start * -1
        if frame_end < 0:
            frame_end = frame_end * -1
        
        armature.location = (0, 0, 0)
        armature.rotation_euler = (0, 0, 0)
        for con in armature.constraints:
            if con.type == 'FOLLOW_PATH':
                armature.constraints.remove(con)
                
        if armature.animation_data and armature.animation_data.action:
            bpy.data.actions.remove(armature.animation_data.action)
                
        armature_constraint = armature.constraints.new(type='FOLLOW_PATH')
        armature_constraint.target = curve
        armature_constraint.forward_axis = 'TRACK_NEGATIVE_Y'
        armature_constraint.up_axis = 'UP_Z'
        armature_constraint.use_curve_follow = True
        armature_constraint.use_fixed_location = True
        context.view_layer.objects.active = armature
        bpy.ops.constraint.followpath_path_animate(constraint=armature_constraint.name, owner='OBJECT')
        armature_constraint.offset_factor = 0.0 
        armature_constraint.keyframe_insert(data_path="offset_factor", frame=frame_start)
        armature_constraint.offset_factor = 1.0
        armature_constraint.keyframe_insert(data_path="offset_factor", frame=frame_end)
        
        data_path = f'constraints["{armature_constraint.name}"].offset_factor'
        for fcurve in armature.animation_data.action.fcurves:
            if fcurve.data_path == data_path:
                for point in fcurve.keyframe_points:
                    if move_type == "BEZIER":
                        point.interpolation = 'BEZIER'
                    else:
                        point.interpolation = 'LINEAR'
                        
        scene.frame_set(scene.start_frame_input)
        return self.validate_animation_files(context, frame_start, frame_end)
        
    def get_path_length(self, context, spline, curve): 
        curve_length = spline.calc_length()
        curve_length_absolute = curve_length * curve.scale.x
        return curve_length_absolute
    
    def validate_animation_files(self, context, frame_start, frame_end):
        scene = context.scene
        if scene.create_animations == False:
            return {'FINISHED'}
        
        armature = context.scene.armature_object_main
        bones_number = len(armature.data.bones)
        
        if not os.path.exists(self.current_path):
            self.report({'ERROR'}, f"Path nout found {self.current_path}")
            #self.report({'INFO'}, f"Skipping creating armature movement.")
            #return {'FINISHED'}
            
        bones_files = os.listdir(self.current_path)
        if len(bones_files) < bones_number:
            self.report({'ERROR'}, f"Not enough Data found. Needing: {bones_number}, Found: {len(bones_files)}")
            #self.report({'INFO'}, f"Skipping creating armature movement.")
            #return {'FINISHED'}
        return self.get_sequence_length(context, frame_start, frame_end)
    
    def get_sequence_length(self, context, frame_start, frame_end):
        INFO_content = []
        scene = context.scene
        
        current_path = os.path.abspath(os.path.join(self.path_to_animation, "INFO.txt"))
        
        try:
            with open(current_path, 'r', encoding="utf-8") as file:
                INFO_content = file.read().splitlines()
        except Exception as e:
            self.report({'ERROR'}, {e})
            #return {'CANCELLED'}
        FRAMERANGE = None
        for line in INFO_content:
            element = line.strip().split()
            if not element:
                continue
            if element[0].upper() == "FRAMERANGE":
                FRAMERANGE = int(element[1])
                break
        if FRAMERANGE is None:
            self.report({'ERROR'}, f"Didn't find entry for FRAMERANGE in INFO.txt.Please check your files.")
        
        return self.create_animations(context, frame_start, frame_end, FRAMERANGE)

    def create_animations(self, context, frame_start, frame_end, FRAMERANGE):
        scene = context.scene
        armature = scene.armature_object_main
    
        if not armature or armature.type != 'ARMATURE':
            return {'CANCELLED'}

        bone_data_cache = {}
    
        for bone in armature.pose.bones:
            file_name = f"{bone.name.upper()}_DATA.txt"
            bonedata_path = os.path.join(self.current_path, file_name)
        
            if os.path.exists(bonedata_path):
                try:
                    with open(bonedata_path, 'r', encoding="utf-8") as file:
                        bone_data_cache[bone.name] = file.read().splitlines()
                except Exception as e:
                    self.report({'WARNING'}, f"Error reading {file_name}: {e}")
        if not bone_data_cache:
            return {'CANCELLED'}
        
        current_file_position = 1
        
        for i, f in enumerate(range(int(frame_start), int(frame_end) + 1)):
            scene.frame_set(f)
            
            if current_file_position > FRAMERANGE:
                    current_file_position = 1
            
            for bone_name, content in bone_data_cache.items():
                bone = armature.pose.bones[bone_name]
                
                search_target = f"FRAME {current_file_position}"
                list_pos = -1
                for idx, line in enumerate(content):
                    if line.strip() == search_target:
                        list_pos = idx
                        break
                if list_pos == -1:
                    continue
                    
                try:
                    loc_x = float(content[list_pos + 1].split()[1])
                    loc_y = float(content[list_pos + 2].split()[1])
                    loc_z = float(content[list_pos + 3].split()[1])
                
                    rot_w = float(content[list_pos + 4].split()[1])
                    rot_x = float(content[list_pos + 5].split()[1])
                    rot_y = float(content[list_pos + 6].split()[1])
                    rot_z = float(content[list_pos + 7].split()[1])
                
                    if bone.rotation_mode != 'QUATERNION':
                        bone.rotation_mode = 'QUATERNION'
                
                    bone.location = (loc_x, loc_y, loc_z)
                    bone.rotation_quaternion = (rot_w, rot_x, rot_y, rot_z)
                
                    bone.keyframe_insert(data_path="location", frame=f)
                    bone.keyframe_insert(data_path="rotation_quaternion", frame=f)
                
                except (ValueError, IndexError):
                    continue
                
            current_file_position += 1
            
        scene.frame_set(scene.start_frame_input)
        return {'FINISHED'}
            
# --- MENU ---
class ANIMATION_MT_select_menu(bpy.types.Menu):
    bl_label = "Animations"
    bl_idname = "ANIMATION_MT_select_menu"
    def draw(self, context):
        layout = self.layout
        for option in animation_names:
            op = layout.operator("scene.set_animation_name", text=option)
            op.animation_name = option
            
class PATH_MT_select_menu(bpy.types.Menu):
    bl_label = "Paths"
    bl_idname = "PATH_MT_select_menu"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        paths = [obj.name for obj in scene.objects if obj.name.startswith("Path_")]
        paths_cleared =[]
        for path in paths:
            paths_cleared.append(path.replace("Path_", ""))
            
        if not paths:
            layout.label(text="No Paths found")
            return

        for name in paths_cleared:
            op = layout.operator("scene.set_path_name", text=name)
            op.path_name = name



# --- PANELS ---

# --> Global

class SCENE_PT_addon_panel(bpy.types.Panel):
    bl_label = "Running Addon Settings"
    bl_idname = "SCENE_PT_addon_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.label(text="General Settings", icon='SETTINGS')
        layout.prop(scene, "filepath", text="Path")
        layout.operator("object.refresh_button", text="Refresh animation names", icon='FILE_REFRESH')
        layout.separator()
        layout.prop(scene, "show_dev", text="Enable Devtools")
        
        
# --> Dev
        
class VIEW3D_PT_panel_RunningAddonDev(bpy.types.Panel):
    bl_label = "RunningAddon Dev"
    bl_idname = "VIEW3D_PT_running_addon_dev"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RunningAddon(Dev)"

    @classmethod
    def poll(cls, context):
        
        return context.scene.show_dev
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text='Still in development, I do not recommend using the devtools at this point.')
        layout.label(text='They still rely on code tweaks to work.')
        row1 = layout.row()
        row1.label(text="Dev Tools")
        row1.operator("object.info_button", icon='INFO', text="")

        split = layout.split(factor=0.5 )
        split.prop(scene, "first_frame_input")
        split.prop(scene, "last_frame_input")
        
        layout.prop(scene, "armature_object")

        row2 = layout.row()
        row2.prop(scene, "animation_name")
        row2.menu("ANIMATION_MT_select_menu", icon='DOWNARROW_HLT', text="")

        layout.operator("object.animation_to_file", icon='EXPORT')
        

# --> Main
    
class VIEW3D_PT_panel_RunningAddonMain(bpy.types.Panel):
    bl_label = "RunningAddon"
    bl_idname = "VIEW3D_PT_running_addon_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RunningAddon"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        box1 = layout.box()
        row1 = box1.row()
        row1.label(text="Main")
        row1.operator("object.info_button", icon='INFO', text="")
        
        box2 = layout.box()
        box2.label(text="Path:")
        row1 = box2.row()
        row1.prop(scene, "path_name_for_create")
        row1.menu("PATH_MT_select_menu", icon='DOWNARROW_HLT', text="")
        box2.operator("object.select_positions", text="start/end pos")
        box2.prop(scene, "curve_slider", text="curve factor")
        box2.prop(scene, "curve_type", text = "path type")
        box2.operator("object.create_path", text="create path")
        
        box3 = layout.box()
        box3.label(text="General animation settings:")
        box3.prop(scene, "armature_object_main")
        box3.prop(scene, "class_name")
        row1 = box3.row()
        row1.prop(scene, "animation_name")
        row1.menu("ANIMATION_MT_select_menu", icon='DOWNARROW_HLT', text="")
        
        box4 = layout.box()
        box4.label(text="Final animation settings:")
        row1 = box4.row()
        row1.prop(scene, "path_name_for_create")
        row1.menu("PATH_MT_select_menu", icon='DOWNARROW_HLT', text="")
        split = box4.split(factor=0.5 )
        left = split.column()
        left.prop(scene, "start_frame_input")
        right = split.column()
        right.prop(scene, "end_frame_input")
        box4.prop(scene, "move_type", text = "movetype")
        box4.operator("object.create_animation", icon='RENDER_ANIMATION')
        box4.operator("object.attempt_pos_rot_fix", text="attempt fix")
    
        
class VIEW3D_PT_RunningAddon_Main_Advanced(bpy.types.Panel):
    bl_label = "Advanced Options"
    bl_idname = "VIEW3D_PT_running_addon_advanced"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RunningAddon(Main)"
    bl_parent_id = "VIEW3D_PT_running_addon_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box1 = layout.box()
        box1.prop(scene, "create_movement", text="create movement")
        box1.prop(scene, "create_animations", text="create animation")
        box1.prop(scene, "use_own_fixdata", text="use own fixdata")
        box1.prop(scene, "datax", text="X")
        box1.prop(scene, "datay", text="Y")
        box1.prop(scene, "dataz", text="Z")

# --- REGISTRATION ---
def armature_filter(self, obj):
    return obj.type == 'ARMATURE'

class DataValue(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty()

class Curves_Items(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    data_list: bpy.props.CollectionProperty(type=DataValue)
    
    
classes = [
    SCENE_PT_addon_panel,
    VIEW3D_PT_panel_RunningAddonDev,
    OBJECT_OT_info_button,
    SCENE_OT_set_animation_name,
    ANIMATION_MT_select_menu,
    OBJECT_OT_animation_to_file,
    OBJECT_OT_refresh_button,
    
    VIEW3D_PT_panel_RunningAddonMain,
    VIEW3D_PT_RunningAddon_Main_Advanced,
    OBJECT_OT_select_position,
    OBJECT_OT_create_path,
    OBJECT_OT_create_animation,
    SCENE_OT_set_path_name,
    PATH_MT_select_menu,
    OBJECT_OT_attempt_pos_rot_fix
]

classes_saves = [
    DataValue,
    Curves_Items  
]


def register_properties():
    bpy.types.Scene.filepath = bpy.props.StringProperty(name="File Path", subtype='DIR_PATH')
    bpy.types.Scene.armature_object = bpy.props.PointerProperty(name="Armature", type=bpy.types.Object, poll=armature_filter)
    bpy.types.Scene.first_frame_input = bpy.props.IntProperty(name="Start", default=1, min=1)
    bpy.types.Scene.last_frame_input = bpy.props.IntProperty(name="End", default=50, min=1)
    bpy.types.Scene.animation_name = bpy.props.StringProperty(name="Animation Name", default="")
    
    bpy.types.Scene.pathname = bpy.props.StringProperty(name="", description="Choose a name for the path", default="Pathname")
    bpy.types.Scene.armature_object_main = bpy.props.PointerProperty(name="Armature", type=bpy.types.Object, poll=armature_filter, update=update_class_selection)
    bpy.types.Scene.start_frame_input = bpy.props.IntProperty(name="Start:", default=1, min=1)
    bpy.types.Scene.end_frame_input = bpy.props.IntProperty(name="End:", default=0, min=1)
    bpy.types.Scene.curve_slider = bpy.props.FloatProperty(name="curve_factor:", description="Only available when path type is set to Beyier!", default=5.0, min=0.0, max=100000.0, soft_max=10.0, precision=1, step=1.0)
    bpy.types.Scene.show_dev = bpy.props.BoolProperty(name="show devtools", description="show tools for saving animation(dev)", default=False)
    bpy.types.Scene.curve_type = bpy.props.EnumProperty(name="path type",description="choose path type",items=[('POLY', "Poly", "straight path", 'LINCURVE', 0),('BEZIER', "Bezier", "smoothed path", 'SMOOTHCURVE', 1),],default='BEZIER')
    bpy.types.Scene.move_type = bpy.props.EnumProperty(name="move type",description="choose move type",items=[('LINE', "Line", "straight movement", 'LINCURVE', 0),('BEZIER', "Bezier", "smoothed path", 'SMOOTHCURVE', 1),],default='LINE')
    bpy.types.Scene.path_name_for_create = bpy.props.StringProperty(name="Path Name", default="")
    bpy.types.Scene.class_name = bpy.props.EnumProperty(name="Class", description="choose class(automated)", items=[('SCOUT', "Scout", ""),('SOLDIER', "Soldier", ""),('PYRO', "Pyro", ""),('DEMO', "Demo", ""),('HEAVY', "Heavy", ""),('ENGINEER', "Engineer", ""),('MEDIC', "Medic", ""),('SNIPER', "Sniper", ""),('SPY', "Spy", ""),('UNDEFINED', "Undefined", "")])
    
    bpy.types.Scene.use_own_fixdata = bpy.props.BoolProperty(name="own data", default=False)
    bpy.types.Scene.datax = bpy.props.StringProperty(name="x", default='0')
    bpy.types.Scene.datay = bpy.props.StringProperty(name="y", default='0')
    bpy.types.Scene.dataz = bpy.props.StringProperty(name="z", default='0')
    
    bpy.types.Scene.create_movement = bpy.props.BoolProperty(name="create movement", default=True)
    bpy.types.Scene.create_animations = bpy.props.BoolProperty(name="create animations", default=True)
    
def unregister_properties():
    del bpy.types.Scene.filepath
    del bpy.types.Scene.armature_object
    del bpy.types.Scene.first_frame_input
    del bpy.types.Scene.last_frame_input
    del bpy.types.Scene.animation_name
    

def register():
    register_properties()
    for cls in classes:
        bpy.utils.register_class(cls)
    for cls in classes_saves:
        bpy.utils.register_class(cls)
    bpy.types.Scene.Curves_Items = bpy.props.CollectionProperty(type=Curves_Items)
    get_files()

def unregister():
    unregister_properties()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()