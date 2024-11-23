import bpy
import mathutils
from bpy.types import GizmoGroup

class LUMOS_GZ_Light_Color(GizmoGroup):
    bl_idname = "lumos_gizmo.light_color"
    bl_label = "Custom Gizmo For Light Color Settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D', 'PERSISTENT'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        wm = context.window_manager
        return ob and ob.type == 'LIGHT' and wm.lumos_gizmo_active

    def setup(self, context):
        # Création d'un gizmo de type dial pour visualiser la lumière
        ob = context.object
        gz = self.gizmos.new("GIZMO_GT_dial_3d")
        gz.hide_select = True
        gz.use_draw_value = False
        color = ob.data.color

        # Personnalisation du gizmo
        gz.line_width = 5
        gz.scale_basis = 0.1
        gz.color = color
        gz.alpha = 1

        self.roll_gizmo = gz

    def draw_prepare(self, context):
        # Mise à jour dynamique de l'orientation du gizmo pour qu'il suive la vue
        ob = context.object
        gz = self.roll_gizmo
        
        # Positionner le gizmo à l'emplacement de la lumière
        gz.matrix_basis.translation = ob.matrix_world.translation
        
        # Orienter le gizmo vers la caméra active
        region_3d = context.region_data
        if region_3d:
            # Obtenir la rotation de la vue inversée pour que le gizmo soit perpendiculaire
            view_rotation = region_3d.view_matrix.inverted().to_3x3()
            view_matrix = mathutils.Matrix.Identity(4)
            view_matrix.translation = ob.matrix_world.translation  # Position de la lumière
            view_matrix @= view_rotation.to_4x4()  # Orientation vers la caméra

            # Appliquer la matrice d'orientation au gizmo
            gz.matrix_basis = view_matrix
            
        # Mise à jour de la couleur du gizmo en fonction de la couleur de la lumière
        light_color = ob.data.color
        gz.color = light_color
#        gz.color_highlight = light_color  # Assure que la couleur reste identique en mode survol
