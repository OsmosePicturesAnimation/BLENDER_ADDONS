import bpy

from bpy.types import Panel, Menu, PropertyGroup, Operator
from bpy.props import EnumProperty, StringProperty, BoolProperty, PointerProperty
from .operators import lumos_manager_operators as lumop

class LUMOS_Properties(PropertyGroup):

#######################################################################         
########################## LIGHT MANAGER ##############################
####################################################################### 

    light_origin: EnumProperty(
        items = (('WORLD', "World", "Défini l'origine de création de la Point Light au centre du monde", 'WORLD', 0),
                 ('CURSOR', "Cursor", "Défini l'origine de création de la Point Light à la position du curseur", 'CURSOR', 1)
                 ),
        default = 'WORLD'
        )

    # target_enabled: bpy.props.BoolProperty(
    #         name = "Light Target", description = "Light Target Tracking on an object",
    #         options = {'HIDDEN'},
    #         default = False,
    #     )
        

    preset_enum : bpy.props.EnumProperty(
        name = "",
        description = "Sort by Type",
        items = [
            ('OP0', "All", "Sort by type : All", 'DOT', 0),
            ('OP1', "Point", "Sort by type : Point Light", 'LIGHT_POINT', 1),
            ('OP2', "Sun", "Sort by type : Sun Light", 'LIGHT_SUN', 2),
            ('OP3', "Spot", "Sort by type : Spot Light",'LIGHT_SPOT', 3 ),
            ('OP4', "Area", "Sort by type : Area Light", 'LIGHT_AREA', 4)
        ],
        default = 'OP0'
    )

    def update_light_position_mode(self, context):
        pass

    light_position_mode_enum : bpy.props.EnumProperty(
        items=[
            ('EDIT', "Edit", "Light Edit mode", "RESTRICT_SELECT_OFF", 0),
            ('NORMALS', "Normals", "Normals mode : Modal to place light based on the normal under the mouse", "NORMALS_FACE", 1),
            ('REFLECTION', "Reflection", "Reflection mode : Modal to place light based on the light's reflection under the mouse","NODE_MATERIAL", 2),
            ('SHADOW', "Shadow", "Shadow mode : : Modal to place light based on the object's shadow under the mouse", "MATSHADERBALL", 3)
        ],
        default = 'EDIT',
        update = update_light_position_mode
    )

    preserve_energy : bpy.props.BoolProperty(
        name = "Preserve Energy",
        description = "Enable energy preservation (Compensates for loss of light energy relative to distance)",
        default = False,
    )
    
    emission_strength_temp : bpy.props.FloatProperty(
        name = "Emission Strength",
        description = "Temporary property for emission strength editing",
        default = 1.0,
        min = 0.0,
        max = 1000.0,
    )
    
#######################################################################         
######################## LIGHT TYPE FILTER ############################
#######################################################################    
    
    all_light_filter : BoolProperty(
    name="Filter All Light",
    description="Show all lights",
    default = True)
    
    point_light_filter : BoolProperty(
    name="Filter Point Light",
    description="Show only Point lights",
    default = False)
    
    sun_light_filter : BoolProperty(
    name="Filter Sun Light",
    description="Shhow only Sun lights",
    default = False)
    
    spot_light_filter : BoolProperty(
    name="Filter Spot Light",
    description="Show only Spot lights",
    default = False)
    
    area_light_filter : BoolProperty(
    name="Filter Area Light",
    description="Show only Area lights",
    default = False)
    
    emissive_filter : BoolProperty(
    name="Filter Emissive Objects",
    description="Show only objects with emissive materials",
    default = False)
    
#######################################################################         
######################### SETTINGS FILTER #############################
#######################################################################     
    
    color_filter : BoolProperty(
    name="Filter Color",
    description="Hide Color property",
    default = True)
    
    energy_filter : BoolProperty(
    name="Filter Energy",
    description="Hide Energy property",
    default = True)

    max_bounces_filter : BoolProperty(
    name="Filter Max Bounces",
    description="Hide Max Bounces property",
    default = True)
    
    specular_filter : BoolProperty(
    name="Filter Specular",
    description="Hide Specular property",
    default = True)

    lightgroup_filter : BoolProperty(
    name="Filter Lightgroup",
    description="Hide Lightgroup property",
    default = True)
    
    radius_filter : BoolProperty(
    name="Filter Radius",
    description="Hide Radius property",
    default = False)
    
    angle_filter : BoolProperty(
    name="Filter Angle",
    description="Hide Angle property",
    default = False)
    
    size_filter : BoolProperty(
    name="Filter Size",
    description="Hide Size property",
    default = False)
    
    shape_filter : BoolProperty(
    name="Filter Shape",
    description="Hide Shape property",
    default = False)
    
    search_filter : StringProperty(
    name="Filter Search",
    description="Allow filtring by searching light's name(no case sensitive)",
    default = "",
    maxlen = 50)

    
    # Custom Search function for searching filter
    def searcher(self, origin, target):
        if origin.casefold() in target.casefold():
            return True
    
    # Function to check if an object has emissive materials
    def is_emissive_object(self, obj):
        if not obj.material_slots:
            return False
        
        for slot in obj.material_slots:
            if slot.material and slot.material.use_nodes:
                for node in slot.material.node_tree.nodes:
                    if node.type == 'EMISSION':
                        # For emission shader, check both color and strength
                        color_input = node.inputs.get('Color')
                        strength_input = node.inputs.get('Strength')
                        
                        # Check if emission color is not black
                        color_not_black = False
                        if color_input and hasattr(color_input, 'default_value'):
                            color = color_input.default_value
                            if len(color) >= 3 and (color[0] > 0 or color[1] > 0 or color[2] > 0):
                                color_not_black = True
                        
                        # Check if emission strength > 0
                        strength_positive = False
                        if strength_input and strength_input.default_value > 0:
                            strength_positive = True
                            
                        # Both conditions must be true
                        if color_not_black and strength_positive:
                            return True
                            
                    # Check for Principled BSDF with emission
                    elif node.type == 'BSDF_PRINCIPLED':
                        emission_strength = node.inputs.get('Emission Strength')
                        emission_color = node.inputs.get('Emission Color') or node.inputs.get('Emission')
                        
                        # Check if emission strength > 0
                        strength_positive = False
                        if emission_strength and emission_strength.default_value > 0:
                            strength_positive = True
                        
                        # Check if emission color is not black
                        color_not_black = False
                        if emission_color and hasattr(emission_color, 'default_value'):
                            color = emission_color.default_value
                            if len(color) >= 3 and (color[0] > 0 or color[1] > 0 or color[2] > 0):
                                color_not_black = True
                        
                        # Both conditions must be true for Principled BSDF
                        if color_not_black and strength_positive:
                            return True
        return False
    
    # Function to get emission strength from an emissive object
    def get_emission_strength(self, obj):
        if not obj.material_slots:
            return 0.0
        
        for slot in obj.material_slots:
            if slot.material and slot.material.use_nodes:
                for node in slot.material.node_tree.nodes:
                    if node.type == 'EMISSION':
                        strength_input = node.inputs.get('Strength')
                        if strength_input:
                            return strength_input.default_value
                    # Check for Principled BSDF with emission
                    if node.type == 'BSDF_PRINCIPLED':
                        emission_strength = node.inputs.get('Emission Strength')
                        if emission_strength and emission_strength.default_value > 0:
                            return emission_strength.default_value
        return 0.0
    
    # Function to set emission strength for an emissive object  
    def set_emission_strength(self, obj, strength):
        if not obj.material_slots:
            return False
        
        for slot in obj.material_slots:
            if slot.material and slot.material.use_nodes:
                for node in slot.material.node_tree.nodes:
                    if node.type == 'EMISSION':
                        strength_input = node.inputs.get('Strength')
                        if strength_input:
                            strength_input.default_value = strength
                            return True
                    # Set emission strength for Principled BSDF
                    if node.type == 'BSDF_PRINCIPLED':
                        emission_strength = node.inputs.get('Emission Strength')
                        if emission_strength:
                            emission_strength.default_value = strength
                            return True
        return False
    
    # Function to get emission color from an emissive object
    def get_emission_color(self, obj):
        if not obj.material_slots:
            return (1.0, 1.0, 1.0)  # Default white
        
        for slot in obj.material_slots:
            if slot.material and slot.material.use_nodes:
                for node in slot.material.node_tree.nodes:
                    if node.type == 'EMISSION':
                        color_input = node.inputs.get('Color')
                        if color_input and hasattr(color_input, 'default_value'):
                            return color_input.default_value[:3]  # RGB only
                    # Check for Principled BSDF with emission
                    if node.type == 'BSDF_PRINCIPLED':
                        emission_color = node.inputs.get('Emission Color') or node.inputs.get('Emission')
                        if emission_color and hasattr(emission_color, 'default_value'):
                            return emission_color.default_value[:3]  # RGB only
        return (1.0, 1.0, 1.0)  # Default white
    
    # Function to set emission color for an emissive object
    def set_emission_color(self, obj, color):
        if not obj.material_slots:
            return False
        
        for slot in obj.material_slots:
            if slot.material and slot.material.use_nodes:
                for node in slot.material.node_tree.nodes:
                    if node.type == 'EMISSION':
                        color_input = node.inputs.get('Color')
                        if color_input:
                            color_input.default_value = (*color, 1.0)  # RGB + Alpha
                            return True
                    # Set emission color for Principled BSDF
                    if node.type == 'BSDF_PRINCIPLED':
                        emission_color = node.inputs.get('Emission Color') or node.inputs.get('Emission')
                        if emission_color:
                            emission_color.default_value = (*color, 1.0)  # RGB + Alpha
                            return True
        return False
    
    # Function to get direct access to emission node inputs for an object
    def get_emission_node_inputs(self, obj):
        """Returns a dict with direct references to emission node inputs"""
        if not obj.material_slots:
            return None
        
        for slot in obj.material_slots:
            if slot.material and slot.material.use_nodes:
                for node in slot.material.node_tree.nodes:
                    if node.type == 'EMISSION':
                        return {
                            'color': node.inputs.get('Color'),
                            'strength': node.inputs.get('Strength'),
                            'node': node,
                            'type': 'EMISSION'
                        }
                    elif node.type == 'BSDF_PRINCIPLED':
                        emission_strength = node.inputs.get('Emission Strength')
                        emission_color = node.inputs.get('Emission Color') or node.inputs.get('Emission')
                        if emission_strength or emission_color:
                            return {
                                'color': emission_color,
                                'strength': emission_strength,
                                'node': node,
                                'type': 'PRINCIPLED'
                            }
        return None