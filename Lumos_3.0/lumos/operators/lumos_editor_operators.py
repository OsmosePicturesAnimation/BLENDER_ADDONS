import bpy

from bpy.types import Panel, Menu, PropertyGroup, Operator
from bpy.props import EnumProperty, StringProperty, BoolProperty, PointerProperty

class LUMOS_EDITOR_OT_PopUpMenu(Operator):
    """Open a popup menu Light Editor"""
    bl_label = "Lumos : Light Editor"
    bl_idname = "lumos_editor.popupmenu"
    bl_description = "Ouvre un menu popup afin de facilité la modification des lights de la scène"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}
                    
    def draw(self, context):
        lumos = context.window_manager.lumos
        view_layer = context.view_layer
        layout = self.layout
        
        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.label(text = "LIGHT EDITOR :", icon = "OUTLINER_OB_LIGHT")
        row = layout.row()

        row = layout.row(align=True)
        row.prop(lumos, "search_filter", icon='VIEWZOOM', text="")
        row.separator(factor=5.0)
        row.alignment ='RIGHT'
        row.label(text="Filter by light type :  ")
        row.prop(lumos, "all_light_filter", text="", icon='DOT')
        row.prop(lumos, "point_light_filter", text="", icon='LIGHT_POINT')
        row.prop(lumos, "sun_light_filter", text="", icon='LIGHT_SUN')
        row.prop(lumos, "spot_light_filter", text="", icon='LIGHT_SPOT')
        row.prop(lumos, "area_light_filter", text="", icon='LIGHT_AREA')

        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Filters :")
        row.prop(lumos, "color_filter", text="Color")
        row.prop(lumos, "energy_filter", text="Energy")
        row.prop(lumos, "max_bounces_filter", text="Max Bounces")
        row.prop(lumos, "specular_filter", text="Specular")
        row.prop(lumos, "lightgroup_filter", text="Light Group")
        row.prop(lumos, "radius_filter", text="Radius")
        row.prop(lumos, "angle_filter", text="Angle")
        row.prop(lumos, "shape_filter", text="Shape")
        row.prop(lumos, "size_filter", text="Size")
        
#######################################################################         
############################ PRESET ALL ###############################
#######################################################################
        if lumos.point_light_filter or lumos.sun_light_filter or lumos.spot_light_filter or lumos.area_light_filter:
            lumos.all_light_filter = False
        else:
            lumos.all_light_filter = True

        if lumos.all_light_filter:   
            for lgt in context.scene.objects:
                if lgt.type == 'LIGHT':
                    if lumos.searcher(lumos.search_filter, lgt.name):
                        row = layout.row(align = True)
                        
                        row.alignment = 'CENTER'
                        row.prop(lgt, "name", text="", emboss = False)
                        
                        row.prop(lgt.data, "type", text="")
                        row.separator(factor=1.0)
                        
                        if lumos.color_filter == 1:
                            row.prop(lgt.data, "color", text="")
                            row.separator(factor=2.0)

                        if lumos.energy_filter == 1:          
                            row.prop(lgt.data, "energy", text="")
                            row.separator(factor=1.0)

                        if lumos.max_bounces_filter == 1:          
                            row.prop(lgt.data.cycles, "max_bounces", text="")
                            row.separator(factor=1.0)
                        
                        if lumos.specular_filter == 1:
                            row.prop(lgt.data, "specular_factor", text="Specular")
                            row.separator(factor=2.0)

                        if lumos.lightgroup_filter == 1:
                                row.prop_search(lgt, "lightgroup", view_layer, "lightgroups", text="Light Group", results_are_suggestions=True)
                                # row.enabled = bool(lgt.lightgroup) and not any(lgp.name == lgt.lightgroup for lgp in view_layer.lightgroups)
                                # row.operator("scene.view_layer_add_lightgroup", icon='ADD', text="").name = lgt.lightgroup
                                row.separator(factor=2.0)
                            
                        if lgt.data.type in {'POINT', 'SPOT'}:
                            if lumos.radius_filter == 1:
                                row.prop(lgt.data, "shadow_soft_size", text="Radius")
                                
                            if lgt.data.type =='SPOT':
                                if lumos.size_filter == 1:
                                    row.separator(factor=1.0)
                                    row.prop(lgt.data, "spot_size", text="Size")
                                    row.separator(factor=1.0)
                                    row.prop(lgt.data, "spot_blend", text="Blend", slider=True)
                                    row.separator(factor=1.0)
                                    row.prop(lgt.data, "show_cone")
            
                        elif lgt.data.type == 'SUN':
                            if lumos.angle_filter == 1:
                                row.prop(lgt.data, "angle")
                                
                        elif lgt.data.type == 'AREA':
                            if lumos.shape_filter == 1:
                                row.prop(lgt.data, "shape", text="")
                                row.separator(factor=1.0)
                                
                            if lgt.data.shape in {'SQUARE', 'DISK'}:
                                if lumos.size_filter == 1:
                                    row.prop(lgt.data, "size")
                                    row.separator(factor=1.0)
                                    
                            elif lgt.data.shape in {'RECTANGLE', 'ELLIPSE'}:
                                if lumos.size_filter == 1:
                                    row.prop(lgt.data, "size", text="Size X")
                                    row.separator(factor=1.0)
                                    row.prop(lgt.data, "size_y", text="Size Y")
                                    row.separator(factor=1.0)

#######################################################################         
########################### PRESET POINT ##############################
#######################################################################

        if lumos.point_light_filter:   
            for lgt in bpy.context.scene.objects:
                if lgt.type == 'LIGHT':
                    if lgt.data.type == 'POINT':
                        if lumos.searcher(lumos.search_filter, lgt.name):
                            row = layout.row(align = True)
                            
                            row.alignment = 'CENTER'
                            row.prop(lgt, "name", text="", emboss = False)
                            
                            row.alignment = 'CENTER'
                            row.prop(lgt.data, "type", text="")
                            row.separator(factor=1.0)
                            
                            if lumos.color_filter == 1:
                                row.prop(lgt.data, "color", text="")
                                row.separator(factor=2.0)
                            
                            if lumos.energy_filter == 1:          
                                row.prop(lgt.data, "energy", text="")
                                row.separator(factor=1.0)

                            if lumos.max_bounces_filter == 1:          
                                row.prop(lgt.data.cycles, "max_bounces", text="")
                                row.separator(factor=1.0)
                            
                            if lumos.specular_filter == 1:
                                row.prop(lgt.data, "specular_factor", text="Specular")
                                row.separator(factor=2.0)

                            if lumos.lightgroup_filter == 1:
                                row.prop_search(lgt, "lightgroup", view_layer, "lightgroups", text="Light Group", results_are_suggestions=True)
                                # row.enabled = bool(lgt.lightgroup) and not any(lgp.name == lgt.lightgroup for lgp in view_layer.lightgroups)
                                # row.operator("scene.view_layer_add_lightgroup", icon='ADD', text="").name = lgt.lightgroup
                                row.separator(factor=2.0)
                                
                            if lumos.radius_filter == 1:
                                row.prop(lgt.data, "shadow_soft_size", text="Radius")
                                
#######################################################################         
############################ PRESET SUN ###############################
#######################################################################

        if lumos.sun_light_filter:   
            for lgt in bpy.context.scene.objects:
                if lgt.type == 'LIGHT':
                    if lgt.data.type == 'SUN':
                        if lumos.searcher(lumos.search_filter, lgt.name):
                            row = layout.row(align = True)
                            
                            row.alignment = 'CENTER'
                            row.prop(lgt, "name", text="", emboss = False)
                            
                            row.alignment = 'CENTER'
                            row.prop(lgt.data, "type", text="")
                            row.separator(factor=1.0)
                            
                            if lumos.color_filter == 1:
                                row.prop(lgt.data, "color", text="")
                                row.separator(factor=2.0)
                            
                            if lumos.energy_filter == 1:          
                                row.prop(lgt.data, "energy", text="")
                                row.separator(factor=1.0)

                            if lumos.max_bounces_filter == 1:          
                                row.prop(lgt.data.cycles, "max_bounces", text="")
                                row.separator(factor=1.0)
                            
                            if lumos.specular_filter == 1:
                                row.prop(lgt.data, "specular_factor", text="Specular")
                                row.separator(factor=2.0)

                            if lumos.lightgroup_filter == 1:
                                row.prop_search(lgt, "lightgroup", view_layer, "lightgroups", text="Light Group", results_are_suggestions=True)
                                # row.enabled = bool(lgt.lightgroup) and not any(lgp.name == lgt.lightgroup for lgp in view_layer.lightgroups)
                                # row.operator("scene.view_layer_add_lightgroup", icon='ADD', text="").name = lgt.lightgroup
                                row.separator(factor=2.0)
                            
                            if lumos.angle_filter == 1:
                                row.prop(lgt.data, "angle")

#######################################################################         
############################ PRESET SPOT ##############################
#######################################################################

        if lumos.spot_light_filter:   
            for lgt in bpy.context.scene.objects:
                if lgt.type == 'LIGHT':
                    if lgt.data.type == 'SPOT':
                        if lumos.searcher(lumos.search_filter, lgt.name):
                            row = layout.row(align = True)
                            
                            row.alignment = 'CENTER'
                            row.prop(lgt, "name", text="", emboss = False)
                            
                            row.alignment = 'CENTER'
                            row.prop(lgt.data, "type", text="")
                            row.separator(factor=1.0)
                            
                            if lumos.color_filter == 1:
                                row.prop(lgt.data, "color", text="")
                                row.separator(factor=2.0)
                            
                            if lumos.energy_filter == 1:          
                                row.prop(lgt.data, "energy", text="")
                                row.separator(factor=1.0)

                            if lumos.max_bounces_filter == 1:          
                                row.prop(lgt.data.cycles, "max_bounces", text="")
                                row.separator(factor=1.0)
                            
                            if lumos.specular_filter == 1:
                                row.prop(lgt.data, "specular_factor", text="Specular")
                                row.separator(factor=2.0)

                            if lumos.lightgroup_filter == 1:
                                row.prop_search(lgt, "lightgroup", view_layer, "lightgroups", text="Light Group", results_are_suggestions=True)
                                # row.enabled = bool(lgt.lightgroup) and not any(lgp.name == lgt.lightgroup for lgp in view_layer.lightgroups)
                                # row.operator("scene.view_layer_add_lightgroup", icon='ADD', text="").name = lgt.lightgroup
                                row.separator(factor=2.0)
                            
                            if lumos.radius_filter == 1:
                                row.prop(lgt.data, "shadow_soft_size", text="Radius")

                            if lumos.size_filter == 1:
                                row.separator(factor=1.0)
                                row.prop(lgt.data, "spot_size", text="Size")
                                row.separator(factor=1.0)
                                row.prop(lgt.data, "spot_blend", text="Blend", slider=True)
                                row.separator(factor=1.0)
                                row.prop(lgt.data, "show_cone")
                            
#######################################################################         
############################ PRESET AREA ##############################
#######################################################################                    

        if lumos.area_light_filter:   
            for lgt in bpy.context.scene.objects:
                if lgt.type == 'LIGHT':
                    if lgt.data.type =='AREA':
                        if lumos.searcher(lumos.search_filter, lgt.name):
                            row = layout.row(align = True)
                            
                            row.alignment = 'CENTER'
                            row.prop(lgt, "name", text="", emboss = False)
                            
                            row.alignment = 'CENTER'
                            row.prop(lgt.data, "type", text="")
                            row.separator(factor=1.0)
                            
                            if lumos.color_filter == 1:
                                row.prop(lgt.data, "color", text="")
                                row.separator(factor=2.0)
                            
                            if lumos.energy_filter == 1:          
                                row.prop(lgt.data, "energy", text="")
                                row.separator(factor=1.0)

                            if lumos.max_bounces_filter == 1:          
                                row.prop(lgt.data.cycles, "max_bounces", text="")
                                row.separator(factor=1.0)
                            
                            if lumos.specular_filter == 1:
                                row.prop(lgt.data, "specular_factor", text="Specular")
                                row.separator(factor=2.0)

                            if lumos.lightgroup_filter == 1:
                                row.prop_search(lgt, "lightgroup", view_layer, "lightgroups", text="Light Group", results_are_suggestions=True)
                                # row.enabled = bool(lgt.lightgroup) and not any(lgp.name == lgt.lightgroup for lgp in view_layer.lightgroups)
                                # row.operator("scene.view_layer_add_lightgroup", icon='ADD', text="").name = lgt.lightgroup
                                row.separator(factor=2.0)
                            
                            if lumos.shape_filter == 1:
                                row.prop(lgt.data, "shape", text="")
                                row.separator(factor=1.0)
                                
                            if lgt.data.shape in {'SQUARE', 'DISK'}:
                                if lumos.size_filter == 1:
                                    row.prop(lgt.data, "size")
                                    row.separator(factor=1.0)
                                    
                            elif lgt.data.shape in {'RECTANGLE', 'ELLIPSE'}:
                                if lumos.size_filter == 1:
                                    row.prop(lgt.data, "size", text="Size X")
                                    row.separator(factor=1.0)
                                    row.prop(lgt.data, "size_y", text="Size Y")
                                    row.separator(factor=1.0)
        

#######################################################################         
############################# PRESET END ##############################
#######################################################################  
                            
    def execute(self, context):
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        
        return context.window_manager.invoke_popup(self, width=0)