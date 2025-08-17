import bpy

from bpy.types import Panel, Menu, PropertyGroup, Operator, UIList, WorkSpaceTool
from bpy.props import EnumProperty, StringProperty, BoolProperty, PointerProperty

def is_locked(obj):
    return all((all(obj.lock_location), all(obj.lock_rotation), all(obj.lock_scale)))

def get_lock_transforms(self):
    ob = [ob for ob in bpy.context.scene.objects if ob.data.name == self.name][0]
    return is_locked(ob)

def set_lock_transforms(self, value):
    ob = [ob for ob in bpy.context.scene.objects if ob.data.name == self.name][0]
    for attr in ("lock_location", "lock_rotation", "lock_scale"):
        setattr(ob, attr, (value, value, value))
        
def is_selected(self):
    ob = [ob for ob in bpy.context.scene.objects if ob.data.name == self.name][0]
    return ob.select_get()

def set_selection(self, value):
    ob = [ob for ob in bpy.context.scene.objects if ob.data.name == self.name][0]
    ob.select_set(state=value)


#####################   PANNEAU DE GESTION  ###################
class LUMOS_MANAGER_PT_3DVIEW_Lumos_Manager(Panel):
    bl_label = "Lumos - Light Manager"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Lumos"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        """
        Pour pouvoir utiliser les properties, on va y acceder via 
        window_manager.
        """
        lumos = context.window_manager.lumos
        scene = context.scene
        lights = [lights for lights in scene.objects if lights.type == "LIGHT"]
        emissive_objects = [obj for obj in scene.objects if obj.type == 'MESH' and lumos.is_emissive_object(obj)]
        selligs = [selligs for selligs in bpy.context.selected_objects if selligs.type == "LIGHT"]
        selemis = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH' and lumos.is_emissive_object(obj)]

        LIGHTS = ('POINT', 'SUN', 'SPOT', 'AREA')
                
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text = "LIGHT CREATOR :", icon = "OUTLINER_OB_LIGHT")
        row.separator()
        row.separator()

        row=layout.row()
        row.prop(scene, "lumos_light_collection")

        # row=layout.row()
        # row.prop(scene, "lumos_target_collection")
        '''
        Originally use the layout.box to hack the interface and only use it to draw a visual 'line separator
        as the layout.separator(type="LINE") seems to not work in panels.
        # row = layout.box()
        # row.separator(type="LINE")
        '''
        
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text = "Choose light origin :", icon = "LIGHT")
        
        row = layout.row(align=True)
        row.prop(lumos, 'light_origin', text="text", expand=True)
        
        # row = layout.row()
        # row.separator()
        # row = layout.row(align=True)
        # row.alignment = 'CENTER'
        # row.prop(lumos, "light_position_mode_enum", expand=True)

        row = layout.row()
        row.separator()
        
        for light in LIGHTS:
            row = layout.row(align=True)
            row.operator('lumos_manager.add_light', text=f"{light.capitalize()} Light", icon=f'LIGHT_{light}').type_=light

        totlig = len(lights)
        sellig = len(selligs)
        totemis = len(emissive_objects)
        selemiscount = len(selemis)

        row = layout.row(align=True)
        row.alignment = 'CENTER'
        row.label(text=f"Lights: {sellig}|{totlig}", icon="LIGHT")
        row.label(text=f"Emissive: {selemiscount}|{totemis}", icon="MATERIAL")
        
        row = layout.row()
        row.operator('lumos_manager.all_light_visibility', text="Show All", icon='HIDE_OFF').visible = False
        row.operator('lumos_manager.all_light_visibility', text="Hide All", icon='HIDE_ON').visible = True

        row = layout.row()
        row.template_list("LUMOS_MANAGER_UL_Ui_list", "", scene, "objects", scene, "lumos_lights_idx")


##################   CREATE AN UL_UI_LIST  ################
class LUMOS_MANAGER_UL_Ui_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        lumos = context.window_manager.lumos
        scene = context.scene
        obj = item
        row = layout.row(align=True)
        
        if obj.type == 'LIGHT':
            # Draw light objects as before
            col_row = row.row(align=True)
            col_row.scale_x = .3
            col_row.prop(obj.data, 'color', text='')
            col_row.separator(factor=2.0)

            row.operator("lumos_manager.lookthrough_light", text="", icon='OUTLINER_OB_CAMERA' if scene.camera == obj else "CAMERA_DATA").light = obj.name
            row.operator("lumos_manager.light_visibility", text="", icon="HIDE_OFF" if not obj.hide_viewport else 'HIDE_ON').light = obj.name
            row.operator("lumos_manager.isolate_light", text="", icon="PMARKER_ACT").light = obj.name
            row.operator("lumos_manager.select_light", text=obj.name).light = obj.name
            row.prop(bpy.data.lights[obj.data.name], 'lumos_lock_light', text="", icon='LOCKED' if is_locked(obj) else 'UNLOCKED')
            row.separator()
            row.operator("lumos_manager.delete_light", text="", icon="PANEL_CLOSE").light_name = obj.data.name
        
        elif obj.type == 'MESH' and lumos.is_emissive_object(obj):
            # Draw emissive objects
            col_row = row.row(align=True)
            col_row.scale_x = .3
            # Direct access to emission color
            emission_inputs = lumos.get_emission_node_inputs(obj)
            if emission_inputs and emission_inputs['color']:
                col_row.prop(emission_inputs['color'], 'default_value', text='')
            col_row.separator(factor=2.0)

            row.operator("lumos_manager.lookthrough_light", text="", icon='OUTLINER_OB_CAMERA' if scene.camera == obj else "CAMERA_DATA").light = obj.name
            row.operator("lumos_manager.light_visibility", text="", icon="HIDE_OFF" if not obj.hide_viewport else 'HIDE_ON').light = obj.name
            row.operator("lumos_manager.isolate_light", text="", icon="PMARKER_ACT").light = obj.name
            row.operator("lumos_manager.select_light", text=obj.name).light = obj.name
            row.prop(obj, 'lumos_lock_object', text="", icon='LOCKED' if is_locked(obj) else 'UNLOCKED')
            row.separator()
            row.operator("lumos_manager.delete_emissive_object", text="", icon="PANEL_CLOSE").object_name = obj.name

        # row.operator("lumos_manager.create_target", text="", icon="CON_TRACKTO").light_name = obj.data.name
        # row.operator('lumos_manager.delete_target', text="", icon="CANCEL").light_name = obj.data.name

        # if lumos.target_enabled is False:
        #     row.operator("lumos_manager.create_target", text="", icon="TRACKING").light_name = obj.data.name
        # else:
        #     row.operator('lumos_manager.delete_target', text="", icon="CANCEL").light_name = obj.data.name

    def filter_items(self, context, data, propname):
        objects = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        # Default return values.
        flt_flags = []
        flt_neworder = []

        # Filtering by name
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, objects, "name",
                                                          reverse=False)
        else:
            flt_flags = [self.bitflag_filter_item] * len(objects)

        if self.use_filter_sort_alpha:
            flt_neworder = helper_funcs.sort_items_by_name(objects, "name")

        # Filter type - include both lights and emissive objects.
        lumos = context.window_manager.lumos
        for idx, obj in enumerate(objects):
            if obj.type != "LIGHT" and not (obj.type == 'MESH' and lumos.is_emissive_object(obj)):
                flt_flags[idx] |= 1 << 0
                flt_flags[idx] &= ~self.bitflag_filter_item

        return flt_flags, flt_neworder

#####################   PANNEAU DE MODIFICATION  ###################
class LUMOS_MANAGER_PT_3DVIEW_Lumos_Manager_Modificator(Panel):
    bl_label = "Light's settings"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Lumos"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        # object = context.object
        layout = self.layout
        # active_object = context.active_object
        view_layer = context.view_layer
        
        # if object == None :    
        #     row = layout.row(align=True)
        #     row.alignment = 'CENTER'
        #     row.label(text = "NO ACTIVE OBJECT DETECTED", icon = "ERROR")
                
        for obj in bpy.context.selected_objects:
            if obj.type == 'LIGHT':
                box = layout.box()
                row = box.row()
                row.alignment = "CENTER"
                row.label(text = obj.name)
                box1 = box.box()
                row = box1.row(align=True)
                row.prop(obj.data, "color")
                row = box1.row(align=True)
                row.prop(obj.data, "energy")
                if context.scene.render.engine == 'CYCLES':
                    if bpy.app.version >= (2, 92, 0):
                        row = box1.row(align=True)
                        row.prop(obj.data.cycles, "max_bounces")
                        row = box1.row(align=True)
                        row.prop_search(obj, "lightgroup", view_layer, "lightgroups", text="Light Group ", results_are_suggestions=True)
                        # row.enabled = bool(obj.lightgroup) and not any(lg.name == obj.lightgroup for lg in view_layer.lightgroups)
                        # row.operator("scene.view_layer_add_lightgroup", icon='ADD', text="").name = obj.lightgroup

                # if not obj.constraints:
                #     continue
                # for c in obj.constraints:
                #     if c.type != "TRACK_TO":
                #         continue
                #     box1 = box.box()
                #     box1.label(text = "Target :     " + obj.constraints['Aim Target'].target.name)
                      
        # Handle emissive objects
        lumos = context.window_manager.lumos
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH' and lumos.is_emissive_object(obj):
                box = layout.box()
                row = box.row()
                row.alignment = "CENTER"
                row.label(text = f"{obj.name} (Emissive)", icon='MATERIAL')
                box1 = box.box()
                
                # Direct access to emission properties
                emission_inputs = lumos.get_emission_node_inputs(obj)
                if emission_inputs:
                    if emission_inputs['color']:
                        row = box1.row(align=True)
                        row.prop(emission_inputs['color'], 'default_value', text="Emission Color")
                    
                    if emission_inputs['strength']:
                        row = box1.row(align=True)
                        row.prop(emission_inputs['strength'], 'default_value', text="Emission Strength")
    
######################## PIE MENU LIGHT ###############################

class LUMOS_MANAGER_VIEW3D_MT_PIE_Light(Menu):
    bl_label = "Lumos : Light Creator"
    bl_idname = "LUMOS_MANAGER_VIEW3D_MT_PIE_Light"
    bl_space_type = "VIEW_3D"
           
    def draw(self, context):

        
        lumos = context.window_manager.lumos
        
        layout = self.layout
        pie = layout.menu_pie()        
        selected = context.selected_objects
        lgt = context.active_object       
        

        if lgt and selected and lgt.type == 'LIGHT':    
            #1 : GAUCHE
            op = pie.operator("lumos_manager.lookthrough_light", text="Look Through / Outside", icon='OUTLINER_OB_CAMERA').light=lgt.name
            #2 : DROITE
            pie.prop(bpy.data.lights[lgt.data.name], 'lumos_lock_light', text="Unlock" if is_locked(lgt) else 'Lock', icon='LOCKED' if is_locked(lgt) else 'UNLOCKED')
            #3: BAS       
            op = pie.operator("lumos_manager.delete_light", text="Delete", icon="PANEL_CLOSE").light_name=lgt.data.name
            #4: HAUT
            op = pie.operator("lumos_manager.isolate_light", text="Isolate", icon="PMARKER_ACT").light=lgt.name
            #5: HAUT GAUCHE
            op = pie.operator('lumos_manager.all_light_visibility', text="Show All", icon='HIDE_OFF').visible = False
            #6: HAUT DROITE
            op = pie.operator('lumos_manager.all_light_visibility', text="Hide All", icon='HIDE_ON').visible = True
            # #7: BAS GAUCHE
            # op = pie.operator("lumos_manager.create_target", text="Create Target Aim", icon="TRACKING").light_name=lgt.data.name
            # #8: BAS DROITE
            # op = pie.operator('lumos_manager.delete_target', text="Delete Target Aim", icon="CANCEL").light_name=lgt.data.name

        else:
            #1 : GAUCHE
            op = pie.operator('lumos_manager.add_light', text="Spot Light", icon='LIGHT_SPOT')
            op.type_='SPOT'
            #2 : DROITE
            op = pie.operator('lumos_manager.add_light', text="Area Light", icon='LIGHT_AREA')
            op.type_='AREA'
            #3: BAS
            op = pie.operator('lumos_manager.add_light', text="Point Light", icon='LIGHT_POINT')
            op.type_='POINT'                 
            #4: HAUT
            op = pie.operator('lumos_manager.add_light', text="Sun Light", icon='LIGHT_SUN')
            op.type_='SUN'            
            #5 et 6: HAUT GAUCHE et HAUT DROITE
            op = pie.operator('lumos_manager.all_light_visibility', text="Show All", icon='HIDE_OFF').visible = False
            op = pie.operator('lumos_manager.all_light_visibility', text="Hide All", icon='HIDE_ON').visible = True
            #7 et 8: BAS GAUCHE et BAS DROITE
            pie.prop(lumos, 'light_origin', text="text", expand=True)