# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# bl_info = {
#     "name": "Lumos",
#     "author": "Quentin 'Eqkoss' Sanhes",
#     "description" : "Light manager & editor. Easy to use, be more focus on your lighting job. Simplify your work and come with extra features ",
#     "version": (3, 0, 0),
#     "blender": (4, 1, 0),
#     "location": "3D View >> N-Panel >> Lumos",	
#     "category": "Lighting",
#     "warning": ""}

### Special thanks to Pistiwique, Jordan and the BlenderLounge Community for the HUGE help ###
import bpy

# from . import auto_reaload #Custom script to automatically reaload the addon
from bpy.types import Panel, Menu, PropertyGroup, Operator, WorkSpaceTool
from bpy.props import EnumProperty, StringProperty, BoolProperty, PointerProperty

from .lumos_preferences import LUMOS_PREFERENCES, assign_custom_keymaps, remove_custom_keymaps, remove_default_keymaps
from .lumos_properties import LUMOS_Properties
from .lumos_gizmo import *
from .operators import lumos_editor_operators, lumos_manager_operators
from .panels import lumos_editor_panels, lumos_manager_panels

def is_locked(obj):
    return all((all(obj.lock_location), all(obj.lock_rotation), all(obj.lock_scale)))

def get_lock_transforms(self):
    ob = bpy.context.scene.objects.get(self.name)
    return is_locked(ob)

def set_lock_transforms(self, value):
    ob = bpy.context.scene.objects.get(self.name)
    for attr in ("lock_location", "lock_rotation", "lock_scale"):
        setattr(ob, attr, (value, value, value))
        
def is_selected(self):
    ob = bpy.context.scene.objects.get(self.name)
    return ob.select_get()

def set_selection(self, value):
    ob = bpy.context.scene.objects.get(self.name)
    ob.select_set(state=value)

def menu_func(self, context):
    self.layout.operator(lumos_manager_operators.LUMOS_MANAGER_OT_Light_Edit_Modify_LocalZPosition.bl_idname)
    self.layout.operator(lumos_manager_operators.LUMOS_MANAGER_OT_Light_Edit_Modify_Color.bl_idname)
    self.layout.operator(lumos_manager_operators.LUMOS_MANAGER_OT_Light_Edit_Modify_Intensity.bl_idname) 

CLASSES = [
    LUMOS_Properties,
    LUMOS_PREFERENCES,
    lumos_gizmo.LUMOS_GZ_Light_Color,
    lumos_editor_operators.LUMOS_EDITOR_OT_PopUpMenu,
    lumos_manager_operators.LUMOS_MANAGER_OT_AddLight,
    lumos_manager_operators.LUMOS_MANAGER_OT_DeleteLight,
    lumos_manager_operators.LUMOS_MANAGER_OT_SelectLight,
    lumos_manager_operators.LUMOS_MANAGER_OT_LookThoughLight,
    lumos_manager_operators.LUMOS_MANAGER_OT_Light_Visibility,
    lumos_manager_operators.LUMOS_MANAGER_OT_All_Light_Visibility,
    lumos_manager_operators.LUMOS_MANAGER_OT_IsolateLight,
    # lumos_manager_operators.LUMOS_MANAGER_OT_Create_Target,
    # lumos_manager_operators.LUMOS_MANAGER_OT_Delete_Target,
    lumos_manager_operators.LUMOS_MANAGER_OT_Light_Normals_Position,
    lumos_manager_operators.LUMOS_MANAGER_OT_Light_Reflection_Position,
    lumos_manager_operators.LUMOS_MANAGER_OT_Light_Target_Position,
    lumos_manager_operators.LUMOS_MANAGER_OT_Light_Shadow_Position,
    lumos_manager_operators.LUMOS_MANAGER_OT_Light_Edit_Mode_Switcher,
    lumos_manager_operators.LUMOS_MANAGER_OT_Light_Edit_Manager,
    lumos_manager_operators.LUMOS_MANAGER_OT_Light_Edit_Modify_Intensity,
    lumos_manager_operators.LUMOS_MANAGER_OT_Light_Edit_Modify_Color,
    lumos_manager_operators.LUMOS_MANAGER_OT_Light_Edit_Modify_LocalZPosition,
    lumos_manager_operators.LUMOS_MANAGER_OT_Light_Edit_Tool_Toggle,
    lumos_editor_panels.LUMOS_EDITOR_PT_PopUpMenu,
    lumos_manager_panels.LUMOS_MANAGER_PT_3DVIEW_Lumos_Manager,
    lumos_manager_panels.LUMOS_MANAGER_UL_Ui_list,
    lumos_manager_panels.LUMOS_MANAGER_PT_3DVIEW_Lumos_Manager_Modificator,
    lumos_manager_panels.LUMOS_MANAGER_VIEW3D_MT_PIE_Light
]

TOOLS = [
    lumos_manager_operators.LUMOS_MANAGER_TL_3DVIEW_Lumos_Light_Edit_Tool,
]

# auto_reaload.init() #Fonction to call the reaload


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    
    for tls in TOOLS:
        bpy.utils.register_tool(tls)

    bpy.types.WindowManager.lumos = PointerProperty(type=LUMOS_Properties)
    bpy.types.WindowManager.lumos_gizmo_active = bpy.props.BoolProperty(name="Lumos Gizmo Active", default=False)


    # Add keymaps based on preferences
    prefs = bpy.context.preferences.addons[__package__].preferences
    assign_custom_keymaps(prefs.use_keymaps_bool)

    bpy.types.Light.lumos_lock_light = BoolProperty(default=False, get=get_lock_transforms, set=set_lock_transforms, name="Lock light", description="Lock light : location, rotation & scale")
    bpy.types.Light.lumos_selection = BoolProperty(default=False, get=is_selected, set=set_selection)
    bpy.types.Scene.lumos_light_collection = bpy.props.PointerProperty(type=bpy.types.Collection, name="Lights Collection", description="Select in which collection the lights will be created")
    # bpy.types.Scene.lumos_target_collection = bpy.props.PointerProperty(type=bpy.types.Collection, name="Targets Collection", description="Select in which collection the targetss will be created")
    bpy.types.Scene.lumos_lights_idx = bpy.props.IntProperty()
    bpy.types.Scene.reference_empty = bpy.props.PointerProperty(
        name="Reference Empty",
        type=bpy.types.Object,
        description="Empty object used as reference for placing light"
    )
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    for cls in CLASSES:
        bpy.utils.unregister_class(cls)

    for tls in TOOLS:
        bpy.utils.unregister_tool(tls)

    # Remove keymaps
    remove_custom_keymaps()
    remove_default_keymaps()

    bpy.types.VIEW3D_MT_object.remove(menu_func)

    del bpy.types.WindowManager.lumos
    del bpy.types.WindowManager.lumos_gizmo_active
    del bpy.types.Scene.lumos_lights_idx
    del bpy.types.Scene.reference_empty


if __name__ == "__main__":
	register()