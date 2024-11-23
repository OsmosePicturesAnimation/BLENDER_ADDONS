import bpy
import colorsys
import bgl
import os

from mathutils import Vector
from bpy_extras import view3d_utils
from bpy.types import Panel, Menu, PropertyGroup, Operator, UIList, WorkSpaceTool
from bpy.props import EnumProperty, PointerProperty, StringProperty, BoolProperty
from pathlib import Path

#####################   AJOUTER LIGHT   ###################
class LUMOS_MANAGER_OT_AddLight(Operator):
    bl_idname = 'lumos_manager.add_light'
    bl_label = 'Add light'
    bl_description = "Add a new light"
    bl_options = {'UNDO'}
    
    type_: StringProperty()
    
    def execute(self,context):

        lumos = context.window_manager.lumos
        scn = context.scene

        #Créé la collection des lights si elle n'existe pas encore
        if scn.lumos_light_collection is None:
            light_coll = bpy.data.collections.get('LIGHTS')
            if light_coll is None:
                light_coll = bpy.data.collections.new("LIGHTS")
                scn.collection.children.link(light_coll)
                
            scn.lumos_light_collection = light_coll
        else:
            scn.lumos_light_collection = bpy.data.collections.get(bpy.context.scene.lumos_light_collection.name)
            
        # Créé la light
        loc = (0, 0, 0)
        if lumos.light_origin == 'CURSOR':
            loc = scn.cursor.location
        light_data = bpy.data.lights.new(name=f"{self.type_}".capitalize(), type=self.type_)
        light_object = bpy.data.objects.new(name=light_data.name, object_data=light_data)
        scn.lumos_light_collection.objects.link(light_object)
        bpy.context.view_layer.objects.active = light_object
        light_object.location = loc
        return{'FINISHED'}
        
#####################   DELETE LIGHT   ###################
class LUMOS_MANAGER_OT_DeleteLight(Operator):
    bl_idname = 'lumos_manager.delete_light'
    bl_label = 'Delete Light'
    bl_description = "Delete the Light"
    bl_options = {'UNDO'}

    light_name: bpy.props.StringProperty()

    def execute(self,context):
        # lumos = context.window_manager.lumos
                
        light = bpy.data.lights.get(self.light_name)
        bpy.data.lights.remove(light, do_unlink=True)
        for block in bpy.data.lights:
            if block.users == 0:
                bpy.data.lights.remove(block)

        # lumos.target_enabled = False
        return{'FINISHED'}
    
#####################   SELECT LIGHT  ###################
class LUMOS_MANAGER_OT_SelectLight(Operator):
    bl_idname = 'lumos_manager.select_light'
    bl_label = 'Select Light'
    bl_description = "Select the Light"
    bl_options = {'UNDO'}

    light: bpy.props.StringProperty()

    def execute(self,context):

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects[self.light].select_set(True)
        context.view_layer.objects.active = bpy.context.scene.objects[self.light]

        return{'FINISHED'}
    
   
#####################   LOOK THROUGH LIGHT  ###################
class LUMOS_MANAGER_OT_LookThoughLight(Operator):
    bl_idname = 'lumos_manager.lookthrough_light'
    bl_label = 'Look Though Light'
    bl_description = "Look through the Light"
    bl_options = {'UNDO'}

    light: bpy.props.StringProperty()
    
    def execute(self,context):

        area_3d = [area for area in context.screen.areas if area.type == 'VIEW_3D']
        
        if area_3d[0].spaces[0].region_3d.view_perspective != 'CAMERA':
            context.scene.camera = bpy.context.scene.objects[self.light]
            bpy.ops.view3d.view_camera()
            context.space_data.lock_camera = True
            
        else:
            if self.light != context.scene.camera.name:
                context.scene.camera = bpy.context.scene.objects[self.light]
            else:
                bpy.ops.view3d.view_camera()
                context.space_data.lock_camera = False
            
        
        return{'FINISHED'}
    
    
#####################   HIDE LIGHT  ###################
class LUMOS_MANAGER_OT_Light_Visibility(Operator):
    bl_idname = 'lumos_manager.light_visibility'
    bl_label = 'Light Visibility'
    bl_description = "Toggle light visibility"
    bl_options = {'UNDO'}

    light: bpy.props.StringProperty()

    def execute(self,context):
        
        light = bpy.context.scene.objects.get(self.light)
        light.hide_viewport = not light.hide_viewport
       
        return{'FINISHED'}
    
    
class LUMOS_MANAGER_OT_All_Light_Visibility(Operator):
    bl_idname = 'lumos_manager.all_light_visibility'
    bl_label = 'Toggle lights visibility'
    bl_options = {'UNDO'}
    
    visible: BoolProperty(default = True)

    def execute(self,context):
        for obj in context.scene.objects:
            if obj.type == 'LIGHT':
                obj.hide_viewport = self.visible
       
        return{'FINISHED'}
    
#####################   ISOLATE LIGHT  ###################
class LUMOS_MANAGER_OT_IsolateLight(Operator):
    bl_idname = 'lumos_manager.isolate_light'
    bl_label = 'Isolate Light'
    bl_description = "Isolate the Light"
    bl_options = {'UNDO'}

    light: bpy.props.StringProperty()

    def execute(self,context):
        
        bpy.ops.lumos_manager.all_light_visibility()
        bpy.ops.lumos_manager.light_visibility(light=self.light)
        bpy.context.scene.objects[self.light].select_set(True)
        context.view_layer.objects.active = bpy.context.scene.objects[self.light]
        return{'FINISHED'}

####################################################################################################
#####################  MODAL RAYCATS FUNCTION TO PLACE LIGHT BASED ON THE NORMAL ###################

class LUMOS_MANAGER_OT_Light_Normals_Position(bpy.types.Operator):
    bl_idname = "lumos_manager.light_normals_modal"
    bl_label = "Position The Light Based On Normals"
    bl_options = {'REGISTER', 'UNDO'}
    
    _timer = None

    def __init__(self):
        self._handle = None
        self.mouse_pos = (0, 0)

    def modal(self, context, event):
        if context.active_object.type == 'LIGHT':
            if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
                return {'PASS_THROUGH'}
            elif event.type == 'MOUSEMOVE':
                self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
                self.execute(context)
            elif event.type == "E":
                bpy.ops.lumos_manager.light_modify_intensity_modal('INVOKE_DEFAULT')
                return self.cancel(context)
            elif event.type == "C":
                bpy.ops.lumos_manager.light_modify_color_modal('INVOKE_DEFAULT')
                return self.cancel(context)
            elif event.type == "F":
                bpy.ops.lumos_manager.light_modify_local_z_position_modal('INVOKE_DEFAULT')
                return self.cancel(context)
            elif event.type in {'ESC', 'LEFTMOUSE', 'ONE', 'THREE', 'FOUR'} and event.value == 'RELEASE':
                return self.cancel(context)

            return {'RUNNING_MODAL'}
        else:
            return self.cancel(context)

    def invoke(self, context, event):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        if context.space_data.type == 'VIEW_3D' and context.active_object and context.active_object.type == 'LIGHT':
            context.window.cursor_modal_set('CROSSHAIR')
            wm.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No light object selected or not in View3D space")
            return {'CANCELLED'}

    def execute(self, context):
        if not context.active_object or context.active_object.type != 'LIGHT':
            return {'CANCELLED'}

        region = context.region
        rv3d = context.region_data
        coord = self.mouse_pos
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        depsgraph = context.evaluated_depsgraph_get()
        result, location, normal, index, obj, matrix = context.scene.ray_cast(
            depsgraph, ray_origin, view_vector
        )

        if result:
            distance = 4
            light = context.active_object
            light.location = location + normal * distance
            light.rotation_euler = normal.to_track_quat('Z', 'Y').to_euler()

        return {'FINISHED'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        context.window.cursor_modal_restore()
        return {'CANCELLED'}    

#####################  MODAL RAYCATS FUNCTION TO PLACE LIGHT BASED ON ITS REFLECTION ###################

class LUMOS_MANAGER_OT_Light_Reflection_Position(bpy.types.Operator):
    bl_idname = "lumos_manager.light_reflection_modal"
    bl_label = "Position The Light Based On Its Reflection"
    bl_options = {'REGISTER', 'UNDO'}

    _timer = None

    def __init__(self):
        self._handle = None
        self.mouse_pos = (0, 0)  # Position de la souris
        self.initial_distance = None

    def modal(self, context, event):
        if context.active_object.type == 'LIGHT':
            if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
                return {'PASS_THROUGH'}
            elif event.type == 'MOUSEMOVE':
                self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
                self.execute(context)
            elif event.type == "E":
                bpy.ops.lumos_manager.light_modify_intensity_modal('INVOKE_DEFAULT')
                return self.cancel(context)
            elif event.type == "C":
                bpy.ops.lumos_manager.light_modify_color_modal('INVOKE_DEFAULT')
                return self.cancel(context)
            elif event.type == "F":
                bpy.ops.lumos_manager.light_modify_local_z_position_modal('INVOKE_DEFAULT')
                return self.cancel(context)
            elif event.type in {'ESC', 'LEFTMOUSE', 'ONE', 'TWO', 'FOUR'} and event.value == 'RELEASE':
                return self.cancel(context)

            return {'RUNNING_MODAL'}
        else:
            return self.cancel(context)
        

    def invoke(self, context, event):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        if context.space_data.type == 'VIEW_3D' and context.active_object and context.active_object.type == 'LIGHT':
            context.window.cursor_modal_set('CROSSHAIR')
            wm.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No light object selected or not in View3D space")
            return {'CANCELLED'}
        
    def execute(self, context):
        if not context.active_object or context.active_object.type != 'LIGHT':
            return {'CANCELLED'}

        region = context.region
        rv3d = context.region_data
        coord = self.mouse_pos
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        depsgraph = context.evaluated_depsgraph_get()
        result, location, normal, index, obj, matrix = context.scene.ray_cast(depsgraph, ray_origin, view_vector)

        if result:
            light = context.active_object
            distance = 4
            incident_vec = (ray_origin - location).normalized()
            reflection_vec = incident_vec.reflect(normal)
            light.location = location - reflection_vec * distance
            light.rotation_euler = (-reflection_vec).to_track_quat('Z', 'Y').to_euler()

        return {'FINISHED'}
    
    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        context.window.cursor_modal_restore()
        return {'CANCELLED'}   


#####################  MODAL RAYCATS FUNCTION TO PLACE LIGHT BASED ON THE SHADOW OR THE TARGETED OBJECT ###################
        ############# FIRST WE USE A MODAL OPERATOR TO CAST A TARGET #############

class LUMOS_MANAGER_OT_Light_Target_Position(bpy.types.Operator):
    bl_idname = "lumos_manager.light_target_modal"
    bl_label = "Position A Target For The Shadow Modal"
    bl_options = {'REGISTER', 'UNDO'}

    _timer = None

    def __init__(self):
        self._handle = None
        self.mouse_pos = (0, 0)
        self._light_object = None

    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        elif event.type == 'MOUSEMOVE':
            self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            self.create_target(context, event)
            bpy.ops.lumos_manager.light_shadow_modal('INVOKE_DEFAULT')
            return self.cancel(context)
        elif event.type in {'ESC', 'ONE', 'TWO', 'THREE'} and event.value == 'PRESS':
            return self.cancel(context)
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window.cursor_modal_set('CROSSHAIR')
        wm.modal_handler_add(self)
        self._light_object = context.active_object
        return {'RUNNING_MODAL'}

    def create_target(self, context, event):
        region = context.region
        rv3d = context.region_data
        coord = (event.mouse_region_x, event.mouse_region_y)
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        depsgraph = context.evaluated_depsgraph_get()
        result, location, normal, index, obj, matrix = context.scene.ray_cast(depsgraph, ray_origin, view_vector)

        if result:
            empty_name = f"tmp_shadow_target_{self._light_object.name}"
            bpy.ops.object.empty_add(type='SPHERE', location=location)
            empty = context.active_object
            empty.name = empty_name
            empty.show_name = True
            empty.scale = (0.2, 0.2, 0.2)  # Set the size of the empty to 0.1
            empty.select_set(False)
            context.scene.reference_empty = empty

            # Reselect the light
            context.view_layer.objects.active = self._light_object
            self._light_object.select_set(True)

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        context.window.cursor_modal_restore()
        return {'CANCELLED'}

class LUMOS_MANAGER_OT_Light_Shadow_Position(bpy.types.Operator):
    bl_idname = "lumos_manager.light_shadow_modal"
    bl_label = "Position The Light Based On The Target Object's Shadow"
    bl_options = {'REGISTER', 'UNDO'}

    _timer = None
    _light_object = None
    _reference_object = None

    def __init__(self):
        self._handle = None
        self.mouse_pos = (0, 0)

    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        if context.active_object == self._light_object and context.active_object.type == 'LIGHT':
            if event.type == 'MOUSEMOVE':
                self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
                self.execute(context)
            elif event.type == "E":
                bpy.ops.lumos_manager.light_modify_intensity_modal('INVOKE_DEFAULT')
                return self.cancel(context)
            elif event.type == "C":
                bpy.ops.lumos_manager.light_modify_color_modal('INVOKE_DEFAULT')
                return self.cancel(context)
            elif event.type == "F":
                bpy.ops.lumos_manager.light_modify_local_z_position_modal('INVOKE_DEFAULT')
                return self.cancel(context)
            elif event.type in {'ESC', 'LEFTMOUSE', 'ONE', 'TWO', 'THREE'} and event.value == 'PRESS':
                return self.cancel(context)
            return {'RUNNING_MODAL'}
        else:
            return self.cancel(context)

    def invoke(self, context, event):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        context.window.cursor_modal_set('CROSSHAIR')
        wm.modal_handler_add(self)
        self._light_object = context.active_object
        self._reference_object = context.scene.reference_empty
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self._light_object or not self._reference_object:
            return {'CANCELLED'}

        region = context.region
        rv3d = context.region_data
        coord = self.mouse_pos
        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        depsgraph = context.evaluated_depsgraph_get()
        result, location, normal, index, obj, matrix = context.scene.ray_cast(depsgraph, ray_origin, view_vector)

        if result:
            self.place_light(context, location, normal)
        return {'FINISHED'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        context.window.cursor_modal_restore()

        if self._reference_object:
            bpy.context.scene.objects.remove(self._reference_object, do_unlink=True)
            context.scene.reference_empty = None

        return {'CANCELLED'}

    def place_light(self, context, shadow_location, normal):
        light = self._light_object
        reference_object = self._reference_object

        if not reference_object:
            return

        direction_to_shadow = reference_object.location - shadow_location
        direction_to_shadow.normalize()

        distance = 4
        light_position = reference_object.location + direction_to_shadow * distance
        light.location = light_position

        direction_to_shadow = light.location - shadow_location
        light.rotation_mode = 'QUATERNION'
        light.rotation_quaternion = direction_to_shadow.to_track_quat('Z', 'Y')
        light.rotation_mode = 'XYZ'

#####################  OPERATOR TO SWITCH LIGHT EDIT MODE WITH KEYMAPS ###################

class LUMOS_MANAGER_OT_Light_Edit_Mode_Switcher(Operator):
    bl_idname = 'lumos_manager.light_edit_mode_switcher'
    bl_label = 'Lumos : Switch Light Edit Mode'
    bl_description = "Operator to switch light edit mode with keymaps"
    bl_options = {'UNDO'}

    def update_mode(self, context):
        bpy.context.window_manager.lumos.light_position_mode_enum = self.mode

    mode: bpy.props.EnumProperty(
        items=[
            ('EDIT', 'Edit', ''),
            ('NORMALS', 'Normals', ''),
            ('REFLECTION', 'Reflection', ''),
            ('SHADOW', 'Shadow', '')
        ],
        default = 'EDIT',
        update = update_mode
    )

    def execute(self,context):

        lumos = context.window_manager.lumos
        
        # Vérifier qu'une lumière est sélectionnée
        if not context.object or context.object.type != 'LIGHT':
            self.report({'ERROR'}, "No light is selected")
            return {'CANCELLED'}

        self.update_mode(context)
        lumos.light_position_mode_enum = self.mode
        # self.update_mode(context)
        self.report({'INFO'}, f"Light Position Mode set to: {self.mode}")
        return{'FINISHED'}

#####################  OPERATOR TO MANAGE MODAL THROUGH THE TOOL ###################

class LUMOS_MANAGER_OT_Light_Edit_Manager(Operator):
    bl_idname = 'lumos_manager.light_position_modal_manager'
    bl_label = 'Tool to Manage Light Edit Mode'
    bl_description = "You must select a light before activating the tool"
    bl_options = {'UNDO'}

    def execute(self,context):
        lumos = context.window_manager.lumos

        if context.active_object and context.active_object.type == 'LIGHT':
            if lumos.light_position_mode_enum == "EDIT":
                pass
                self.report({'INFO'}, "Edit Mode: Press LEFTCLICK, E, F or C")

            elif lumos.light_position_mode_enum == "NORMALS":
                bpy.ops.lumos_manager.light_normals_modal('INVOKE_DEFAULT')
                self.report({'INFO'}, "Normals Mode: Pres LEFTCLICK, E, F or C")

            elif lumos.light_position_mode_enum == "REFLECTION":
                bpy.ops.lumos_manager.light_reflection_modal('INVOKE_DEFAULT')
                self.report({'INFO'}, "Reflection Mode, Press LEFTCLICK, E, F or C")
            
            elif lumos.light_position_mode_enum == "SHADOW":
                bpy.ops.lumos_manager.light_target_modal('INVOKE_DEFAULT')
                self.report({'INFO'}, "Shadow Mode: Press LEFTCLICK, E, F or C")
            else:
                self.report({'ERROR'}, "At least one light and/or on mode must be selected !")
            return{'FINISHED'}
        else:
             bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
             self.report({'ERROR'}, "YOU HAVE TO SELECT A LIGHT TO USE LIGHT EDIT TOOLS BACK TO SELECT BOX")
        return{'FINISHED'}
    
######################## TOOL LIGHT EDIT (INTERFACE) ###############################

class LUMOS_MANAGER_TL_3DVIEW_Lumos_Light_Edit_Tool(WorkSpaceTool):
    bl_space_type = 'VIEW_3D'
    bl_context_mode = 'OBJECT'
    bl_idname = "lumos_manager.light_edit tool"
    bl_label = "Lumos : Light Edit Tool"
    bl_description = "Tool to position light based on reflection"
    # bl_icon = "ops.generic.select"
    # bl_icon = "ops.light.edit"
    # bl_icon =os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "icons", "/ops.light.edit.dat"))
    bl_icon =str((Path(__file__).parent.parent / "icons" / "ops.light.edit").resolve())
    bl_widget = None
    bl_keymap = (
        ("lumos_manager.light_position_modal_manager", {"type": 'LEFTMOUSE', "value": 'PRESS'}, None),
        ("lumos_manager.light_modify_intensity_modal", {"type": 'E', "value": 'PRESS'}, None),
        ("lumos_manager.light_modify_color_modal", {"type": 'C', "value": 'PRESS'}, None),
        ("lumos_manager.light_modify_local_z_position_modal", {"type": 'F', "value": 'PRESS'}, None),
    )

    def draw_settings(context, layout, tool):
        lumos = context.window_manager.lumos
        if context.active_object and context.active_object.type != 'LIGHT':
            layout.label(text="YOU MUST TO SELECT A LIGHT TO USE LIGHT EDIT TOOLS")
            layout.alert = True
        else:
            layout.prop(lumos, "light_position_mode_enum", expand=True)
            # layout.separator()
            layout.prop(lumos, "preserve_energy")

        


######################## MODIFY INTENSITY TOOL FOR LIGHT EDIT ###############################

class LUMOS_MANAGER_OT_Light_Edit_Modify_Intensity(bpy.types.Operator):
    """Modal Operator To Modify Intensity By Moving Horizontaly"""
    bl_idname = "lumos_manager.light_modify_intensity_modal"
    bl_label = "Increase/Decrease Intensity"
    
    def __init__(self):
        self.start_mouse_x = 0
        self.initial_intensity = 0
        self.incremented_value = 10
    
    def modal(self, context, event):
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
                return {'PASS_THROUGH'}
        # incremented_value_list = [0.01, 0.1, 0.25, 0.5, 1, 10, 100, 10e00]
        elif event.type == 'MOUSEMOVE':
            delta_x = event.mouse_x - self.start_mouse_x
            # Adjust the intensity based on mouse movement
            context.object.data.energy = self.initial_intensity + delta_x * self.incremented_value
            return {'RUNNING_MODAL'}
        elif event.type == "WHEELUPMOUSE":
            self.incremented_value = self.incremented_value * 10
            return {'RUNNING_MODAL'}
        elif event.type == "WHEELDOWNMOUSE":
            self.incremented_value = self.incremented_value / 10
            return {'RUNNING_MODAL'}
        elif event.type =='LEFTMOUSE':
            context.window.cursor_modal_restore()
            return {'CANCELLED'}
        elif event.type in {'ESC', 'RIGHTMOUSE'}:
            context.window.cursor_modal_restore()
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object and context.object.type == 'LIGHT':
            self.start_mouse_x = event.mouse_x
            self.initial_intensity = context.object.data.energy
            context.window.cursor_modal_set('MOVE_X')
            context.window_manager.modal_handler_add(self)
            self.report({'INFO'}, "Move horizontally to modify the intensy")
            return {'RUNNING_MODAL'}
        else:
            context.window.cursor_modal_restore()
            self.report({'WARNING'}, "No active light object found")
            return {'CANCELLED'}
        

######################## MODIFY COLOR TOOL FOR LIGHT EDIT ###############################

class LUMOS_MANAGER_OT_Light_Edit_Modify_Color(bpy.types.Operator):
    """Modal Operator To Modify Color By Moving Horizontaly"""
    bl_idname = "lumos_manager.light_modify_color_modal"
    bl_label = "Modify Color Hue"

    def __init__(self):
        self.start_mouse_x = 0
        self.start_mouse_y = 0
        self.initial_hue = 0
        self.initial_saturation = 0
        self.incremented_value = 0.001
        self.incremented_saturation = 0.001
        self.lock_x = False
        self.lock_y = False

    def update_cursor(self, context):
        """Update cursor appearance based on the lock state."""
        if self.lock_x:
            context.window.cursor_modal_set("SCROLL_X")
        elif self.lock_y:
            context.window.cursor_modal_set("SCROLL_Y")
        else:
            context.window.cursor_modal_set("SCROLL_XY")
    
    def modal(self, context, event):
        wm = context.window_manager

        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
                return {'PASS_THROUGH'}
        
         # Toggle locking/unlocking based on key press
        if event.type == 'X' and event.value == 'PRESS':
            if self.lock_x:
                # Unlock X if already locked, returning to default mode
                self.lock_x = False
            else:
                # Lock X and unlock Y if X was pressed after Y
                self.lock_x = True
                self.lock_y = False
            self.update_cursor(context)

        elif event.type == 'Y' and event.value == 'PRESS':
            if self.lock_y:
                # Unlock Y if already locked, returning to default mode
                self.lock_y = False
            else:
                # Lock Y and unlock X if Y was pressed after X
                self.lock_y = True
                self.lock_x = False
            self.update_cursor(context)

        elif event.type == 'MOUSEMOVE':
            # Only calculate deltas for unlocked axes
            delta_x = (event.mouse_x - self.start_mouse_x) if not self.lock_y else 0
            delta_y = (event.mouse_y - self.start_mouse_y) if not self.lock_x else 0

            
            new_hue = (self.initial_hue + delta_x * self.incremented_value) % 1.0
            new_saturation = min(max(self.initial_saturation + delta_y * self.incremented_saturation, 0.0), 1.0)

            # Convert HSV back to RGB
            rgb = colorsys.hsv_to_rgb(new_hue, new_saturation, self.initial_value)
            context.object.data.color = rgb
            return {'RUNNING_MODAL'}
        
        elif event.type =='LEFTMOUSE':
            context.window.cursor_modal_restore()
            wm.lumos_gizmo_active = False # Restore the custom gizmo state
            if context.area and context.area.type == 'VIEW_3D':
                context.area.tag_redraw()  # Forcer le rafraîchissement de la vue

            return {'FINISHED'}
        
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.window.cursor_modal_restore()
            wm.lumos_gizmo_active = False # Restore the custom gizmo state
            if context.area and context.area.type == 'VIEW_3D':
                context.area.tag_redraw()  # Forcer le rafraîchissement de la vue
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        wm = context.window_manager

        if context.object and context.object.type == 'LIGHT':
            # Initiate the custom gizmo state
            wm.lumos_gizmo_active = True

            self.start_mouse_x = event.mouse_x
            self.start_mouse_y = event.mouse_y
            
            rgb = context.object.data.color
            hsv = colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])
            self.initial_hue, self.initial_saturation, self.initial_value = hsv
            
            bpy.ops.wm.tool_set_by_id(name="LUMOS_GIZMOGROUP_circle")
            context.window.cursor_modal_set('SCROLL_XY')
            wm.modal_handler_add(self)
            self.report({'INFO'}, "Horizontal modify Hue, Vertical modify Saturation")
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "No active light object found")
            return {'CANCELLED'}
        

######################## MODIFY Z POSITION TOOL FOR LIGHT EDIT ###############################

class LUMOS_MANAGER_OT_Light_Edit_Modify_LocalZPosition(bpy.types.Operator):
    """Modal Operator To Modify Z Position Localy By Moving Horizontaly"""
    bl_idname = "lumos_manager.light_modify_local_z_position_modal"
    bl_label = "Modify Z Local Position"

    def __init__(self):
        self.start_mouse_x = 0
        self.start_location = None
        self.initial_energy = None #Only use when lumos = context.window_manager.lumos is True
        self.initial_distance = None #Only use when lumos = context.window_manager.lumos is True

    def modal(self, context, event):
        lumos = context.window_manager.lumos
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        elif event.type == 'MOUSEMOVE':
            delta_x = event.mouse_x - self.start_mouse_x
            delta_z = delta_x * 0.01  # Adjust the factor as needed
            local_z_vector = context.object.matrix_world.to_quaternion() @ Vector((0, 0, 1))

            new_location = self.start_location + local_z_vector * delta_z
            context.object.location = new_location

            if lumos.preserve_energy:
                # Calculate the new distance and adjust the energy accordingly
                new_distance = (context.object.location - self.hit_location).length
                distance_ratio = (self.initial_distance / new_distance) ** 2
                context.object.data.energy = self.initial_energy / distance_ratio
            return {'RUNNING_MODAL'}
        elif event.type in {'ESC', 'LEFTMOUSE', 'RIGHTMOUSE'}:
            context.window.cursor_modal_restore()
            return {'CANCELLED'}
        
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        lumos = context.window_manager.lumos
        if context.object and context.object.type == 'LIGHT':
            self.start_mouse_x = event.mouse_x
            self.start_location = context.object.location.copy()
            if lumos.preserve_energy:
                self.initial_energy = context.object.data.energy

                # Perform a raycast to find the hit location
                depsgraph = context.evaluated_depsgraph_get()
                direction = context.object.matrix_world.to_quaternion() @ Vector((0, 0, -1))
                result, location, normal, index, obj, matrix = context.scene.ray_cast(depsgraph, context.object.location, direction)
                
                if result:
                    self.hit_location = location
                    self.initial_distance = (context.object.location - self.hit_location).length  # Store the initial distance
                else:
                    self.report({'WARNING'}, "No hit detected for the light ray")
                    return {'CANCELLED'}

            context.window.cursor_modal_set('SCROLL_XY')
            context.window_manager.modal_handler_add(self)
            self.report({'INFO'}, "Move mouse vertically to move light along local Z axis")
            return {'RUNNING_MODAL'}
        else:
            context.window.cursor_modal_restore()
            self.report({'WARNING'}, "No active light object found")
            return {'CANCELLED'}
        

######################## OPERATOR TO CONTROL THE TOOL TOGGLE (L) ###############################

class LUMOS_MANAGER_OT_Light_Edit_Tool_Toggle(bpy.types.Operator):
    """Operator to controle the tool toogle L to activate the tool. L again to choose the previous tool selected"""
    bl_idname = "lumos_manager.light_edit_tool_toggle"
    bl_label = "Controle Light Edit Tool Toggle"

    light: bpy.props.StringProperty()

    def execute(self,context):
        current_mode = bpy.context.mode #Return the current mode (OBJECT, EDIT_MESH, SCULPT, POSE, etc)
        current_tool = bpy.context.workspace.tools.from_space_view3d_mode(current_mode, create=False).idname #Return the current activated tool in the View 3D
        old_tool = current_tool
        if current_tool != 'lumos_manager.light_edit tool':
            bpy.ops.wm.tool_set_by_id(name='lumos_manager.light_edit tool') #Set a tool as active by its name
        elif current_tool == 'lumos_manager.light_edit tool':
            if current_tool != old_tool:
                bpy.ops.wm.tool_set_by_id(name=old_tool)
            else:
                bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
        return{'FINISHED'}