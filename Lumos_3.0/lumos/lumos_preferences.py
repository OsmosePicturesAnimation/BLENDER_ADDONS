import bpy

addon_keymaps = []

def update_bool(self, context):
        remove_default_keymaps()
        remove_custom_keymaps()
        assign_custom_keymaps(use_custom=self.use_keymaps_bool)

def remove_default_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user  # Utiliser le keyconfig utilisateur car c'est là où les raccourcis par défaut sont souvent stockés

    # Accéder au keymap pour le mode objet
    km = kc.keymaps.get('Object Mode')

    if km:
        # Filtrer pour ne garder que les raccourcis simples sans alt, ctrl, ou shift
        keymap_items_to_remove = [
            item for item in km.keymap_items
            if item.type in {'ONE', 'TWO', 'THREE', 'FOUR'}
            and not item.alt and not item.ctrl and not item.shift
        ]

        for kmi in keymap_items_to_remove:
            km.keymap_items.remove(kmi)

def remove_custom_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc: 
        for km,kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
        addon_keymaps.clear()

def assign_default_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user

    km = kc.keymaps.get('Object Mode')

    if km:
        # Clear previous keymaps if necessary (optional)
        remove_default_keymaps()
        
        for keys, values in {'ONE': 1, 'TWO': 2, 'THREE': 3, 'FOUR': 4}.items():
            kmi = km.keymap_items.new("object.hide_collection", type=keys, value='PRESS')
            kmi.properties.collection_index = values  # Assuming collections are indexed as such
            
            # kmi_alt = km.keymap_items.new("object.hide_collection", type=keys, value='PRESS', alt=True)
            # kmi_alt.properties.collection_index = values
            
            # kmi_shift = km.keymap_items.new("object.hide_collection", type=keys, value='PRESS', shift=True)
            # kmi_shift.properties.collection_index = values
            
            # kmi_shift_alt = km.keymap_items.new("object.hide_collection", type=keys, value='PRESS', shift=True, alt=True)
            # kmi_shift_alt.properties.collection_index = values


def assign_custom_keymaps(use_custom: bool=True):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type = 'VIEW_3D')

        kmi = km.keymap_items.new("lumos_editor.popupmenu", type = 'QUOTE', value = 'PRESS', ctrl = True)
        addon_keymaps.append((km, kmi))

        kmi1 = km.keymap_items.new("wm.call_menu_pie", type='QUOTE', value='PRESS', shift=True)
        kmi1.properties.name = "LUMOS_MANAGER_VIEW3D_MT_PIE_Light"
        addon_keymaps.append((km, kmi1))

        kmi6 = km.keymap_items.new("lumos_manager.light_edit_tool_toggle", type = 'L', value = 'PRESS')
        addon_keymaps.append((km, kmi6))

        if use_custom:
            # Assignation personnalisée en 3D View pour le mode Object seulement
            for key, mode in zip(['ONE', 'TWO', 'THREE', 'FOUR'], ['EDIT', 'NORMALS', 'REFLECTION', 'SHADOW']):
                kmi = km.keymap_items.new("lumos_manager.light_edit_mode_switcher", type=key, value='PRESS')
                kmi.properties.mode = mode
                addon_keymaps.append((km, kmi))
        else:
            for key, mode in zip(['P', 'Y', 'U', 'J'], ['EDIT', 'NORMALS', 'REFLECTION', 'SHADOW']):
                kmi = km.keymap_items.new("lumos_manager.light_edit_mode_switcher", type=key, value='PRESS')
                kmi.properties.mode = mode
                addon_keymaps.append((km, kmi))

            assign_default_keymaps()

class LUMOS_PREFERENCES(bpy.types.AddonPreferences):
    bl_idname = __package__

    use_keymaps_bool: bpy.props.BoolProperty(
        name="1, 2, 3, 4 as Keymaps",
        description="Choose to use 1, 2, 3, 4 as keymaps for light edit or not",
        default=True,
        update = update_bool
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "use_keymaps_bool")