import bpy

from bpy.types import Panel, Menu, PropertyGroup, Operator
from bpy.props import EnumProperty, StringProperty, BoolProperty, PointerProperty

class LUMOS_EDITOR_PT_PopUpMenu(Panel):
    """Open a popup menu Light Editor"""
    bl_label = "Lumos - Light Editor"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Lumos"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row(align=True)
        row.operator('lumos_editor.popupmenu', text="LIGHT EDITOR", icon='SETTINGS')