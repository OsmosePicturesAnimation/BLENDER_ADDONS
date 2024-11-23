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