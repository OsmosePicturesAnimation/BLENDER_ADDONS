import bpy

from bpy.types import Panel, Menu, PropertyGroup, Operator
from bpy.props import EnumProperty, StringProperty, BoolProperty, PointerProperty

class LUMOS_MT_PropertiesFilter(Menu):
    """Properties Filter Menu"""
    bl_label = "Properties Filters"
    bl_idname = "LUMOS_MT_PropertiesFilter"

    def draw(self, context):
        lumos = context.window_manager.lumos
        layout = self.layout
        
        column = layout.column(align=True)
        column.prop(lumos, "color_filter", text="Color", toggle=True)
        column.prop(lumos, "energy_filter", text="Energy", toggle=True)
        column.prop(lumos, "max_bounces_filter", text="Max Bounces", toggle=True)
        column.prop(lumos, "specular_filter", text="Specular", toggle=True)
        column.prop(lumos, "lightgroup_filter", text="Light Group", toggle=True)
        column.prop(lumos, "radius_filter", text="Radius", toggle=True)
        column.prop(lumos, "angle_filter", text="Angle", toggle=True)
        column.prop(lumos, "shape_filter", text="Shape", toggle=True)
        column.prop(lumos, "size_filter", text="Size", toggle=True)

class LUMOS_EDITOR_OT_PopUpMenu(Operator):
    """Open a popup menu Light Editor"""
    bl_label = "Lumos : Light Editor"
    bl_idname = "lumos_editor.popupmenu"
    bl_description = "Ouvre un menu popup afin de facilité la modification des lights de la scène"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

    @classmethod
    def poll(cls, context):
        return context.space_data and context.space_data.type == 'VIEW_3D'

    def get_sorted_objects(self, context, lumos):
        """Get objects sorted by type if sort_by_type is enabled"""
        scene_objects = list(context.scene.objects)
        
        if not getattr(lumos, 'sort_by_type', False):
            return scene_objects
            
        # Sort by type, then by name within each type
        def get_sort_key(scene_object):
            if scene_object.type == 'LIGHT':
                light_type_order = {'POINT': 0, 'SUN': 1, 'SPOT': 2, 'AREA': 3}
                return (0, light_type_order.get(scene_object.data.type, 99), scene_object.name.lower())
            elif scene_object.type == 'MESH' and lumos.is_emissive_object(scene_object):
                return (1, 0, scene_object.name.lower())  # Emissive objects come after lights
            else:
                return (99, 0, scene_object.name.lower())  # Other objects at the end
                
        return sorted(scene_objects, key=get_sort_key)

    def filter_and_sort_objects(self, context, lumos):
        """Filter and sort objects based on current filter settings"""
        sorted_objects = self.get_sorted_objects(context, lumos)
        
        # Check individual filter states
        all_light_active = getattr(lumos, 'all_light_filter', False)
        point_active = getattr(lumos, 'point_light_filter', False)
        sun_active = getattr(lumos, 'sun_light_filter', False)
        spot_active = getattr(lumos, 'spot_light_filter', False)
        area_active = getattr(lumos, 'area_light_filter', False)
        emissive_active = getattr(lumos, 'emissive_filter', False)
        
        # Determine which light types and emissives are active
        active_light_filters = set()
        show_emissives = False
        
        # Logic: All seul → Toutes les lights + émissifs
        if all_light_active:
            active_light_filters = {'POINT', 'SUN', 'SPOT', 'AREA'}
            show_emissives = True
        else:
            # Specific filters
            if point_active:
                active_light_filters.add('POINT')
            if sun_active:
                active_light_filters.add('SUN')
            if spot_active:
                active_light_filters.add('SPOT')
            if area_active:
                active_light_filters.add('AREA')
            if emissive_active:
                show_emissives = True

        filtered_lights = []
        filtered_emissives = []

        for scene_object in sorted_objects:
            # Filter lights
            if scene_object.type == 'LIGHT':
                if active_light_filters and scene_object.data.type in active_light_filters and \
                   lumos.searcher(lumos.search_filter, scene_object.name):
                    filtered_lights.append(scene_object)
            
            # Filter emissive meshes
            elif scene_object.type == 'MESH' and show_emissives and \
                 lumos.is_emissive_object(scene_object):
                if lumos.searcher(lumos.search_filter, scene_object.name):
                    filtered_emissives.append(scene_object)

        return filtered_lights, filtered_emissives

    def sync_master_filter(self, lumos):
        """Synchronize the all_light_filter based on specific filters"""
        # Get current state of all specific filters
        point_active = getattr(lumos, 'point_light_filter', False)
        sun_active = getattr(lumos, 'sun_light_filter', False)
        spot_active = getattr(lumos, 'spot_light_filter', False)
        area_active = getattr(lumos, 'area_light_filter', False)
        emissive_active = getattr(lumos, 'emissive_filter', False)
        
        specific_filters = [point_active, sun_active, spot_active, area_active, emissive_active]
        active_filter_count = sum(1 for filter_active in specific_filters if filter_active)
        
        # Logic selon vos spécifications:
        # - Si n'importe quel filtre spécifique est True, alors ALL est False
        # - Si tous les filtres spécifiques sont True, alors ALL est True  
        # - Si aucun filtre spécifique n'est actif, ALL reste tel qu'il est (pas de changement automatique)
        
        if active_filter_count > 0:
            if active_filter_count == len(specific_filters):
                # Tous les filtres sont actifs → ALL devient True
                lumos.all_light_filter = True
            else:
                # Quelques filtres actifs mais pas tous → ALL devient False
                lumos.all_light_filter = False

    def create_table_column(self, table_row, header_text, filtered_lights, filtered_emissives, 
                           draw_light_function, draw_emissive_function=None, column_scale=0.8):
        """Create a table column with header and content"""
        table_column = table_row.column(align=True)
        table_column.scale_x = column_scale
        
        # Header
        table_column.label(text=header_text)
        
        # Light rows
        for light_object in filtered_lights:
            draw_light_function(table_column, light_object)
        
        # Emissive rows
        for emissive_object in filtered_emissives:
            if draw_emissive_function:
                draw_emissive_function(table_column, emissive_object)
            else:
                table_column.alignment = 'CENTER'
                table_column.label(text="-")
        
        return table_column

    def draw_dash(self, table_column):
        """Draw a dash placeholder in a table cell"""
        table_column.label(text="—")

    def maybe_create_column(self, filter_property_name, header_text, table_row, filtered_lights, 
                           filtered_emissives, draw_light_function, draw_emissive_function=None, lumos=None):
        """Create a column only if the filter is active"""
        if getattr(lumos, filter_property_name, False):
            self.create_table_column(table_row, header_text, filtered_lights, filtered_emissives, 
                                   draw_light_function, draw_emissive_function)

    def draw_lights_by_type(self, layout, filtered_lights, filtered_emissives, lumos, view_layer):
        """Draw lights grouped by type when sorting is enabled"""
        if not getattr(lumos, 'sort_by_type', False):
            # Normal table layout when sorting is disabled
            self.draw_normal_table(layout, filtered_lights, filtered_emissives, lumos, view_layer)
            return
        
        # Group lights by type
        lights_by_type = {}
        for light_object in filtered_lights:
            light_type = light_object.data.type
            if light_type not in lights_by_type:
                lights_by_type[light_type] = []
            lights_by_type[light_type].append(light_object)
        
        # Define the order of light types
        type_order = ['POINT', 'SUN', 'SPOT', 'AREA']
        
        # Draw each type group
        first_group = True
        for light_type in type_order:
            if light_type in lights_by_type:
                if not first_group:
                    layout.separator()  # Add space between type groups
                
                # Create table for this light type
                self.draw_normal_table(layout, lights_by_type[light_type], [], lumos, view_layer)
                first_group = False
        
        # Add emissive objects as the last group if they exist
        if filtered_emissives:
            if not first_group:  # Only add separator if there were lights before
                layout.separator()
            self.draw_normal_table(layout, [], filtered_emissives, lumos, view_layer)

    def draw_normal_table(self, layout, filtered_lights, filtered_emissives, lumos, view_layer):
        """Draw the normal table layout with all columns"""
        # Create table layout
        table_row = layout.row(align=True)

        # 1) Name column (always visible)
        self.create_table_column(
            table_row, "Name", filtered_lights, filtered_emissives,
            draw_light_function=lambda column, light: column.prop(light, "name", text="", emboss=False),
            draw_emissive_function=lambda column, emissive: column.prop(emissive, "name", text="", emboss=False),
        )

        # 2) Type column (always visible)
        self.create_table_column(
            table_row, "Type", filtered_lights, filtered_emissives,
            draw_light_function=lambda column, light: column.prop(light.data, "type", text=""),
            draw_emissive_function=lambda column, emissive: column.label(text="EMISSIVE", icon='MATERIAL'),
        )

        # 3) Color column
        def draw_light_color(column, light):
            column.prop(light.data, "color", text="")
        
        def draw_emissive_color(column, emissive_object):
            emission_inputs = lumos.get_emission_node_inputs(emissive_object)
            if emission_inputs and emission_inputs.get('color'):
                column.prop(emission_inputs['color'], 'default_value', text="")
            else:
                self.draw_dash(column)
        
        self.maybe_create_column(
            'color_filter', "Color", table_row, filtered_lights, filtered_emissives,
            draw_light_color, draw_emissive_color, lumos
        )

        # 4) Energy column
        def draw_light_energy(column, light):
            column.prop(light.data, "energy", text="")
        
        def draw_emissive_energy(column, emissive_object):
            emission_inputs = lumos.get_emission_node_inputs(emissive_object)
            if emission_inputs and emission_inputs.get('strength'):
                column.prop(emission_inputs['strength'], 'default_value', text="")
            else:
                self.draw_dash(column)
        
        self.maybe_create_column(
            'energy_filter', "Energy", table_row, filtered_lights, filtered_emissives,
            draw_light_energy, draw_emissive_energy, lumos
        )

        # 5) Max Bounces column
        def draw_light_max_bounces(column, light):
            column.prop(light.data.cycles, "max_bounces", text="")
        
        def draw_emissive_max_bounces(column, emissive_object):
            self.draw_dash(column)
        
        self.maybe_create_column(
            'max_bounces_filter', "Max Bounces", table_row, filtered_lights, filtered_emissives,
            draw_light_max_bounces, draw_emissive_max_bounces, lumos
        )

        # 6) Specular column
        def draw_light_specular(column, light):
            column.prop(light.data, "specular_factor", text="")
        
        def draw_emissive_specular(column, emissive_object):
            self.draw_dash(column)
        
        self.maybe_create_column(
            'specular_filter', "Specular", table_row, filtered_lights, filtered_emissives,
            draw_light_specular, draw_emissive_specular, lumos
        )

        # 7) Light Group column
        def draw_light_group(column, light):
            column.prop_search(light, "lightgroup", view_layer, "lightgroups", text="", results_are_suggestions=True)
        
        def draw_emissive_light_group(column, emissive_object):
            self.draw_dash(column)
        
        self.maybe_create_column(
            'lightgroup_filter', "Light Group", table_row, filtered_lights, filtered_emissives,
            draw_light_group, draw_emissive_light_group, lumos
        )

        # 8) Radius column (POINT / SPOT only)
        def draw_light_radius(column, light):
            if light.data.type in {'POINT', 'SPOT'}:
                column.prop(light.data, "shadow_soft_size", text="")
            else:
                self.draw_dash(column)
        
        def draw_emissive_radius(column, emissive_object):
            self.draw_dash(column)
        
        self.maybe_create_column(
            'radius_filter', "Radius", table_row, filtered_lights, filtered_emissives,
            draw_light_radius, draw_emissive_radius, lumos
        )

        # 9) Angle column (SUN only)
        def draw_light_angle(column, light):
            if light.data.type == 'SUN':
                column.prop(light.data, "angle", text="")
            else:
                self.draw_dash(column)
        
        def draw_emissive_angle(column, emissive_object):
            self.draw_dash(column)
        
        self.maybe_create_column(
            'angle_filter', "Angle", table_row, filtered_lights, filtered_emissives,
            draw_light_angle, draw_emissive_angle, lumos
        )

        # 10) Shape column (AREA only)
        def draw_light_shape(column, light):
            if light.data.type == 'AREA':
                column.prop(light.data, "shape", text="")
            else:
                self.draw_dash(column)
        
        def draw_emissive_shape(column, emissive_object):
            self.draw_dash(column)
        
        self.maybe_create_column(
            'shape_filter', "Shape", table_row, filtered_lights, filtered_emissives,
            draw_light_shape, draw_emissive_shape, lumos
        )

        # 11) Size column (SPOT / AREA) - En ligne horizontale
        def draw_light_size(column, light):
            light_data = light.data
            if light_data.type == 'SPOT':
                # Spot light properties en ligne horizontale
                size_row = column.row(align=True)
                size_row.prop(light_data, "spot_size", text="")
                size_row.prop(light_data, "spot_blend", text="", slider=True)
                size_row.prop(light_data, "show_cone", text="")
            elif light_data.type == 'AREA':
                if light_data.shape in {'SQUARE', 'DISK'}:
                    column.prop(light_data, "size", text="")
                elif light_data.shape in {'RECTANGLE', 'ELLIPSE'}:
                    # Area light properties en ligne horizontale
                    size_row = column.row(align=True)
                    size_row.prop(light_data, "size", text="")
                    size_row.prop(light_data, "size_y", text="")
                else:
                    self.draw_dash(column)
            else:
                self.draw_dash(column)
        
        def draw_emissive_size(column, emissive_object):
            self.draw_dash(column)
        
        self.maybe_create_column(
            'size_filter', "Size", table_row, filtered_lights, filtered_emissives,
            draw_light_size, draw_emissive_size, lumos
        )

    def draw(self, context):
        lumos = context.window_manager.lumos
        view_layer = context.view_layer
        layout = self.layout
        
        # Title
        title_row = layout.row(align=True)
        title_row.alignment = 'CENTER'
        title_row.label(text="LIGHT EDITOR :", icon="OUTLINER_OB_LIGHT")

        # Filters row
        filters_row = layout.row(align=True)
        filters_row.prop(lumos, "search_filter", icon='VIEWZOOM', text="")
        filters_row.separator(factor=5.0)
        filters_row.alignment = 'RIGHT'
        filters_row.label(text="Filter by light type : ")
        filters_row.prop(lumos, "all_light_filter", text="", icon='DOT')
        filters_row.prop(lumos, "point_light_filter", text="", icon='LIGHT_POINT')
        filters_row.prop(lumos, "sun_light_filter", text="", icon='LIGHT_SUN')
        filters_row.prop(lumos, "spot_light_filter", text="", icon='LIGHT_SPOT')
        filters_row.prop(lumos, "area_light_filter", text="", icon='LIGHT_AREA')
        filters_row.prop(lumos, "emissive_filter", text="", icon='MATERIAL')

        filters_row.separator(factor=2.0)
        # Properties Filter Menu
        filters_row.menu("LUMOS_MT_PropertiesFilter", text="", icon='FILTER')
        filters_row.separator(factor=1.0)
        # Sort by type button
        filters_row.prop(lumos, "sort_by_type", text="", icon='SORTBYEXT')

        # Synchronize master filter (only if not in reset state)
        # Reset state = all_light_filter is True but all specific filters are False
        all_specific_active = (
            getattr(lumos, 'point_light_filter', False) or
            getattr(lumos, 'sun_light_filter', False) or  
            getattr(lumos, 'spot_light_filter', False) or
            getattr(lumos, 'area_light_filter', False) or
            getattr(lumos, 'emissive_filter', False)
        )
        
        # Only sync if we're not in a reset state (ALL True + no specific filters)
        if not (getattr(lumos, 'all_light_filter', False) and not all_specific_active):
            self.sync_master_filter(lumos)

        # Get filtered and sorted objects
        filtered_lights, filtered_emissives = self.filter_and_sort_objects(context, lumos)

        # Draw lights by type or normal table
        self.draw_lights_by_type(layout, filtered_lights, filtered_emissives, lumos, view_layer)

    def execute(self, context):
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=0)