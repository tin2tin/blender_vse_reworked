# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
import bpy
from bpy.types import Header, Menu, Panel
from rna_prop_ui import PropertyPanel
from .properties_grease_pencil_common import (
    AnnotationDataPanel,
    GreasePencilToolsPanel,
)
from bpy.app.translations import pgettext_iface as iface_


def act_strip(context):
    try:
        return context.scene.sequence_editor.active_strip
    except AttributeError:
        return None


def draw_color_balance(layout, color_balance):

    flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
    col = flow.column()

    box = col.box()
    split = box.split(factor=0.35)
    col = split.column(align=True)
    col.label(text="Lift:")
    col.separator()
    col.separator()
    col.prop(color_balance, "lift", text="")
    col.prop(color_balance, "invert_lift", text="Invert", icon='ARROW_LEFTRIGHT')
    split.template_color_picker(color_balance, "lift", value_slider=True, cubic=True)

    col = flow.column()

    box = col.box()
    split = box.split(factor=0.35)
    col = split.column(align=True)
    col.label(text="Gamma:")
    col.separator()
    col.separator()
    col.prop(color_balance, "gamma", text="")
    col.prop(color_balance, "invert_gamma", text="Invert", icon='ARROW_LEFTRIGHT')
    split.template_color_picker(color_balance, "gamma", value_slider=True, lock_luminosity=True, cubic=True)

    col = flow.column()

    box = col.box()
    split = box.split(factor=0.35)
    col = split.column(align=True)
    col.label(text="Gain:")
    col.separator()
    col.separator()
    col.prop(color_balance, "gain", text="")
    col.prop(color_balance, "invert_gain", text="Invert", icon='ARROW_LEFTRIGHT')
    split.template_color_picker(color_balance, "gain", value_slider=True, lock_luminosity=True, cubic=True)


class SEQUENCER_HT_header(Header):
    bl_space_type = 'SEQUENCE_EDITOR'

    def draw(self, context):
        layout = self.layout

        st = context.space_data
        scene = context.scene

        row = layout.row(align=True)
        row.template_header()

        layout.prop(st, "view_type", text="")

        SEQUENCER_MT_editor_menus.draw_collapsible(context, layout)

        layout.separator_spacer()

        layout.template_running_jobs()

        if st.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'}:
            layout.separator()

            if(bpy.context.scene.use_audio):
                icon = "MUTE_IPO_OFF"
            else:
                icon = "MUTE_IPO_ON"

            layout.operator( "screen.audio_mute_toggle", text = "", icon = icon )

            layout.operator("sequencer.refresh_all", icon="FILE_REFRESH", text="")

        if st.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}:
            layout.prop(st, "display_mode", text="", icon_only=True)

        if st.view_type != 'SEQUENCER':
            layout.prop(st, "preview_channels", text="", icon_only=True)
            layout.prop(st, "display_channel", text="Channel")

            ed = scene.sequence_editor
            if ed:
                row = layout.row(align=True)
                row.prop(ed, "show_overlay", text="", icon='GHOST_ENABLED')
                if ed.show_overlay:
                    row.prop(ed, "overlay_frame", text="")
                    row.prop(ed, "use_overlay_lock", text="", icon='LOCKED')

                    row = layout.row()
                    row.prop(st, "overlay_type", text="")

        if st.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}:
            gpd = context.gpencil_data
            toolsettings = context.tool_settings

            # Proportional editing
            if gpd and gpd.use_stroke_edit_mode:
                row = layout.row(align=True)
                row.prop(toolsettings, "proportional_edit", icon_only=True)
                if toolsettings.proportional_edit != 'DISABLED':
                    row.prop(toolsettings, "proportional_edit_falloff", icon_only=True)


class SEQUENCER_MT_editor_menus(Menu):
    bl_idname = "SEQUENCER_MT_editor_menus"
    bl_label = ""

    def draw(self, context):
        self.draw_menus(self.layout, context)

    @staticmethod
    def draw_menus(layout, context):
        st = context.space_data

        layout.menu("SEQUENCER_MT_view")

        if st.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'}:

            layout.menu("SEQUENCER_MT_select")
            layout.menu("SEQUENCER_MT_add")
            layout.menu("SEQUENCER_MT_edit")
            layout.menu("SEQUENCER_MT_cut")
            layout.menu("SEQUENCER_MT_transform")
            layout.menu("SEQUENCER_MT_strip")
            layout.menu("SEQUENCER_MT_navigation")
            layout.menu("SEQUENCER_MT_marker")


class SEQUENCER_MT_view_render(Menu):
    bl_label = "Render"

    def draw(self, context):
        layout = self.layout

        layout.operator("render.opengl", text="Preview Render Image", icon='RENDER_STILL').sequencer = True
        props = layout.operator("render.opengl", text="Preview Render Animation", icon='RENDER_ANIMATION')
        props.animation = True
        props.sequencer = True


class SEQUENCER_MT_view_toggle(Menu):
    bl_label = "View Type"

    def draw(self, context):
        layout = self.layout

        layout.operator("sequencer.view_toggle").type = 'SEQUENCER'
        layout.operator("sequencer.view_toggle").type = 'PREVIEW'
        layout.operator("sequencer.view_toggle").type = 'SEQUENCER_PREVIEW'


class SEQUENCER_MT_preview_zoom(Menu):
    bl_label = "Fractional Zoom"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_PREVIEW'

        ratios = ((1, 8), (1, 4), (1, 2), (1, 1), (2, 1), (4, 1), (8, 1))

        for i, (a, b) in enumerate(ratios):
            if i in {3, 4}:  # Draw separators around Zoom 1:1.
                layout.separator()

            layout.operator(
                "sequencer.view_zoom_ratio",
                text=iface_(f"Zoom {a:d}:{b:d}"),
                translate=False,
            ).ratio = a / b
        layout.operator_context = 'INVOKE_DEFAULT'


class SEQUENCER_MT_view_zoom(Menu):
    bl_label = "Frame"

    def draw(self, context):
        layout = self.layout

        layout.operator("view2d.zoom_border", text = "Box...")
        layout.operator("sequencer.view_selected", text="Selected")
        layout.operator("sequencer.view_all", text="All")
        layout.operator("sequencer.view_frame", text="Playhead")
        layout.separator()

        prop = layout.operator("view2d.zoom_in", text="Horizontal In")
        layout.operator("view2d.zoom_out", text="Horizontal Out")
        layout.operator_context = "EXEC_REGION_WIN"
        layout.operator("sequencer.zoom_vertical", text="Vertical In").direction = "IN"
        layout.operator("sequencer.zoom_vertical", text="Vertical Out").direction = "OUT"


class SEQUENCER_MT_view_preview(Menu):
    bl_label = "Preview Range"

    def draw(self, context):
        layout = self.layout

        layout.operator("anim.previewrange_set", text = "Set Box...")
        layout.operator("anim.previewrange_clear", text = "Clear Box")

        layout.separator()

        layout.operator("sequencer.preview_selected", text = "Selected")
        layout.operator("anim.start_frame_set", text = "Set Start")
        layout.operator("anim.end_frame_set", text = "Set End")


class SEQUENCER_MT_view(Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout

        st = context.space_data
        is_preview = st.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}
        is_sequencer_view = st.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'}

        if st.view_type == 'PREVIEW':
            # Specifying the REGION_PREVIEW context is needed in preview-only
            # mode, else the lookup for the shortcut will fail in
            # wm_keymap_item_find_props() (see #32595).
            layout.operator_context = 'INVOKE_REGION_PREVIEW'
        layout.operator("sequencer.properties", icon='MENU_PANEL', text = "Toggle Sidebar")
        layout.operator_context = 'INVOKE_DEFAULT'

        layout.separator()    

        if is_sequencer_view:
            layout.operator_context = 'INVOKE_REGION_WIN'

            layout.menu("SEQUENCER_MT_view_zoom")

            layout.menu("SEQUENCER_MT_view_preview")

            layout.operator_context = 'INVOKE_DEFAULT'

            layout.separator()

        if is_preview:
            layout.operator_context = 'INVOKE_REGION_PREVIEW'
            
            if st.display_mode == 'IMAGE':

                layout.prop(st, "show_safe_areas")
                layout.prop(st, "show_metadata")

                layout.separator()

            elif st.display_mode == 'WAVEFORM':

                layout.prop(st, "show_separate_color") 

                layout.separator()

            layout.operator("view2d.zoom_in", text = "Zoom In")
            layout.operator("view2d.zoom_out", text = "Zoom Out")
            layout.operator("view2d.zoom_border", text = "Zoom Box...")

            layout.separator()
                        
            layout.menu("SEQUENCER_MT_preview_zoom")

            layout.separator()
                                  
            layout.operator("sequencer.view_all_preview", text="Fit Preview in window")            

            layout.operator_context = 'INVOKE_DEFAULT'

            # # XXX, invokes in the header view
            #layout.operator("sequencer.view_ghost_border", text="Overlay Border")

        if is_sequencer_view:

            layout.prop(st, "show_backdrop",text="Backdrop")
            layout.prop(st, "show_strip_offset", text="Offsets")

            layout.prop(st, "show_frame_indicator", text="Frame Number")

            layout.prop(st, "show_seconds", text="Seconds")
            if context.space_data.show_seconds:
                layout.prop(context.preferences.view, "timecode_style", text="")

            layout.prop_menu_enum(st, "waveform_display_type", text="Waveform")

        layout.separator()

        layout.menu("SEQUENCER_MT_view_render")

        layout.separator()

        layout.menu("INFO_MT_area")


class SEQUENCER_MT_transform_gaps(Menu):
    bl_label = "Gaps"

    def draw(self, context):
        layout = self.layout

        layout.operator("sequencer.gap_remove", text = "Extract at Playhead").all=False
        layout.operator("sequencer.gap_remove", text = "Extract All").all=True
        layout.operator("sequencer.concatenate", text = "Extract after Selection")

        layout.separator()

        layout.operator("sequencer.gap_insert", text = "Insert Gap")


class SEQUENCER_MT_transform_move(Menu):
    bl_label = "Move in Steps"

    def draw(self, context):
        layout = self.layout

        layout.operator("sequencer.move", text = "Up").direction = "UP"
        layout.operator("sequencer.move", text = "Down").direction = "DOWN"
        layout.operator("sequencer.move", text = "Left").direction = "LEFT"
        layout.operator("sequencer.move", text = "Right").direction = "RIGHT"


class SEQUENCER_MT_transform(Menu):
    bl_label = "Transform"

    def draw(self, context):
        layout = self.layout

        layout.operator("transform.transform", text="Move").mode = 'TRANSLATION'
        layout.operator("transform.transform", text="Move/Extend from Frame").mode = 'TIME_EXTEND'
        layout.operator("sequencer.slip", text="Slip Strip Contents")

        layout.separator()

        layout.menu("SEQUENCER_MT_transform_move")

        layout.separator()

        layout.operator_menu_enum("sequencer.swap", "side")

        layout.separator()

        layout.menu("SEQUENCER_MT_transform_gaps")

        layout.separator()

        layout.operator("sequencer.snap", text = "Snap to Playhead")


class SEQUENCER_MT_edit_input(Menu):
    bl_label = "Inputs"

    def draw(self, context):
        layout = self.layout
        edit = act_edit(context)

        layout.operator("sequencer.reload", text="Reload Strips")
        layout.operator("sequencer.reload", text="Reload Strips and Adjust Length").adjust_length = True
        prop = layout.operator("sequencer.change_path", text="Change Path/Files")
        layout.operator("sequencer.swap_data", text="Swap Data")

        if edit:
            stype = edit.type

            if stype == 'IMAGE':
                prop.filter_image = True
            elif stype == 'MOVIE':
                prop.filter_movie = True
            elif stype == 'SOUND':
                prop.filter_sound = True


class SEQUENCER_MT_select_cursor(Menu):
    bl_label = "Select Playhead"

    def draw(self, context):
        layout = self.layout
        layout.operator("sequencer.select_under_playhead", text="Current Frame").extend = False
        props = layout.operator("sequencer.select", text="Left")
        props.left_right = 'LEFT'
        props.linked_time = True
        props = layout.operator("sequencer.select", text="Right")
        props.left_right = 'RIGHT'
        props.linked_time = True


class SEQUENCER_MT_select_handle(Menu):
    bl_label = "Select Handle"

    def draw(self, context):
        layout = self.layout

        layout.operator("sequencer.select_handles", text="Both").side = 'BOTH'
        layout.operator("sequencer.select_handles", text="Left").side = 'LEFT'
        layout.operator("sequencer.select_handles", text="Right").side = 'RIGHT'


class SEQUENCER_MT_select_channel(Menu):
    bl_label = "Select Channel"

    def draw(self, context):
        layout = self.layout

        layout.operator("sequencer.select_channel_strips", text="All")
        layout.operator("sequencer.select_active_side", text="Left").side = 'LEFT'
        layout.operator("sequencer.select_active_side", text="Right").side = 'RIGHT'


# Info about these functions should be moved into the statusbar
class SEQUENCER_MT_select_Mouse(Menu):
    bl_label = "Select Mouse"

    def draw(self, context):
        layout = self.layout

        props = layout.operator("sequencer.select", text = "Handles")
        props.extend = False
        props.linked_time = False
        props.left_right = 'NONE'
        props.linked_handle = True

        props = layout.operator("sequencer.select", text = "Time Linked")
        props.extend = False
        props.linked_time = True
        props.left_right = 'MOUSE'
        props.linked_handle = False

        props = layout.operator("sequencer.select", text = "Extended")
        props.extend = True
        props.linked_time = False
        props.left_right = 'NONE'
        props.linked_handle = False


class SEQUENCER_MT_select_linked(Menu):
    bl_label = "Select Linked"

    def draw(self, context):
        layout = self.layout

        layout.operator("sequencer.select_linked", text = "All")
        layout.operator("sequencer.select_less", text = "Less")
        layout.operator("sequencer.select_more", text = "More")


class SEQUENCER_MT_select(Menu):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        layout.operator("sequencer.select_all", text="All").action = 'SELECT'
        layout.operator("sequencer.select_all", text="None").action = 'DESELECT'
        layout.operator("sequencer.select_all", text="Invert").action = 'INVERT'

        layout.separator()

        prop = layout.operator("sequencer.select_box", text = "Box...")

        layout.separator()
        
        layout.menu("SEQUENCER_MT_select_cursor", text ="Playhead")
        layout.menu("SEQUENCER_MT_select_handle", text ="Handle")
        layout.menu("SEQUENCER_MT_select_channel", text ="Channel")
        layout.menu("SEQUENCER_MT_select_linked", text ="Linked")
        
        # Info about Mouse Cursor functions should be moved into the statusbar:       
        layout.menu("SEQUENCER_MT_select_Mouse", text ="Mouse Cursor")

        layout.separator()

        # The following two functions should be moved into the Grouped menu:
        layout.operator("sequencer.select_locked_strips", text = "Locked")
        layout.operator("sequencer.select_muted_strips", text ="Muted")

        layout.separator()

        layout.operator_menu_enum("sequencer.select_grouped", "type", text="Grouped")


class SEQUENCER_MT_marker(Menu):
    bl_label = "Marker"

    def draw(self, context):
        layout = self.layout

        st = context.space_data
        is_sequencer_view = st.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'}

        from .space_time import marker_menu_generic
        marker_menu_generic(layout)

        if is_sequencer_view:
            layout.prop(st, "use_marker_sync")

class SEQUENCER_MT_change(Menu):
    bl_label = "Change"

    def draw(self, context):
        layout = self.layout
        strip = act_strip(context)

        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.operator_menu_enum("sequencer.change_effect_input", "swap")
        layout.operator_menu_enum("sequencer.change_effect_type", "type")
        prop = layout.operator("sequencer.change_path", text="Path/Files")

        if strip:
            stype = strip.type

            if stype == 'IMAGE':
                prop.filter_image = True
            elif stype == 'MOVIE':
                prop.filter_movie = True
            elif stype == 'SOUND':
                prop.filter_sound = True
                

class SEQUENCER_MT_navigation_play(Menu):
    bl_label = "Toggle Play"

    def draw(self, context):
        layout = self.layout

        layout.operator("screen.animation_play", text="Forward", icon = "PLAY")
        props = layout.operator("screen.animation_play", text="Reverse", icon = "PLAY_REVERSE")
        props.reverse = True


class SEQUENCER_MT_navigation_frame(Menu):
    bl_label = "Frame"

    def draw(self, context):
        layout = self.layout

        props = layout.operator("screen.frame_offset", text="Previous")
        props.delta = -1
        props = layout.operator("screen.frame_offset", text="Next")
        props.delta = 1


class SEQUENCER_MT_navigation_cut(Menu):
    bl_label = "Cut"

    def draw(self, context):
        layout = self.layout

        props = layout.operator("sequencer.strip_jump", text="Previous")
        props.next = False
        props.center = False
        props = layout.operator("sequencer.strip_jump", text="Next")
        props.next = True
        props.center = False


class SEQUENCER_MT_navigation_strip(Menu):
    bl_label = "Strip"

    def draw(self, context):
        layout = self.layout

        props = layout.operator("sequencer.strip_jump", text="Previous")
        props.next = False
        props.center = True
        props = layout.operator("sequencer.strip_jump", text="Next")
        props.next = True
        props.center = True


class SEQUENCER_MT_navigation_keyframe(Menu):
    bl_label = "Keyframe"

    def draw(self, context):
        layout = self.layout

        props = layout.operator("screen.keyframe_jump", text="Previous", icon = "PREV_KEYFRAME")
        props.next = False
        props = layout.operator("screen.keyframe_jump", text="Next", icon = "NEXT_KEYFRAME")
        props.next = True

class SEQUENCER_MT_navigation_range(Menu):
    bl_label = "Range"

    def draw(self, context):
        layout = self.layout        
        props = layout.operator("screen.frame_jump", text="Start", icon = "REW")
        props.end = False
        props = layout.operator("screen.frame_jump", text="End", icon = "FF")
        props.end = True        

class SEQUENCER_MT_navigation(Menu):
    bl_label = "Navigation"

    def draw(self, context):
        layout = self.layout

        layout.menu("SEQUENCER_MT_navigation_play")

        layout.separator()

        layout.menu("SEQUENCER_MT_navigation_frame")

        layout.menu("SEQUENCER_MT_navigation_cut")

        layout.menu("SEQUENCER_MT_navigation_strip")

        layout.menu("SEQUENCER_MT_navigation_keyframe")

        layout.menu("SEQUENCER_MT_navigation_range")        


class SEQUENCER_MT_add(Menu):
    bl_label = "Add"

    def draw(self, context):

        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'

        bpy_data_scenes_len = len(bpy.data.scenes)
        if bpy_data_scenes_len > 10:
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("sequencer.scene_strip_add", text="Scene...", icon='SCENE_DATA')
        elif bpy_data_scenes_len > 1:
            layout.operator_menu_enum("sequencer.scene_strip_add", "scene", text="Scene", icon='SCENE_DATA')
        else:
            layout.menu("SEQUENCER_MT_add_empty", text="Scene", icon='SCENE_DATA')
        del bpy_data_scenes_len

        bpy_data_movieclips_len = len(bpy.data.movieclips)
        if bpy_data_movieclips_len > 10:
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("sequencer.movieclip_strip_add", text="Clip...", icon='TRACKER')
        elif bpy_data_movieclips_len > 0:
            layout.operator_menu_enum("sequencer.movieclip_strip_add", "clip", text="Clip", icon='TRACKER')
        else:
            layout.menu("SEQUENCER_MT_add_empty", text="Clip", icon='TRACKER')
        del bpy_data_movieclips_len

        bpy_data_masks_len = len(bpy.data.masks)
        if bpy_data_masks_len > 10:
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("sequencer.mask_strip_add", text="Mask...", icon='MOD_MASK')
        elif bpy_data_masks_len > 0:
            layout.operator_menu_enum("sequencer.mask_strip_add", "mask", text="Mask", icon='MOD_MASK')
        else:
            layout.menu("SEQUENCER_MT_add_empty", text="Mask", icon='MOD_MASK')
        del bpy_data_masks_len

        layout.separator()

        layout.operator("sequencer.movie_strip_add", text="Movie", icon='FILE_MOVIE')
        layout.operator("sequencer.sound_strip_add", text="Sound", icon='FILE_SOUND')
        layout.operator("sequencer.image_strip_add", text="Image/Sequence", icon='FILE_IMAGE')

        layout.separator()

        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("sequencer.effect_strip_add", text="Color", icon='COLOR').type = 'COLOR'
        layout.operator("sequencer.effect_strip_add", text="Text", icon='FONT_DATA').type = 'TEXT'

        layout.separator()

        layout.operator("sequencer.effect_strip_add", text="Adjustment Layer", icon='COLOR').type = 'ADJUSTMENT'

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.menu("SEQUENCER_MT_add_effect")

        col = layout.column()
        col.menu("SEQUENCER_MT_add_transitions")


class SEQUENCER_MT_add_empty(Menu):
    bl_label = "Empty"

    def draw(self, context):
        layout = self.layout

        layout.label(text="No Items Available")


class SEQUENCER_MT_add_transitions(Menu):
    bl_label = "Transitions"

    def draw(self, context):
        def sel_sequences(context):
            return len(getattr(context, "selected_sequences", ())) 

        selected_seq = sel_sequences(context)

        layout = self.layout

        col = layout.column()
        col.operator("sequencer.crossfade_sounds", text="Sound Crossfade")

        col.separator()

        col.operator("sequencer.effect_strip_add", text="Crossfade").type = 'CROSS'
        col.operator("sequencer.effect_strip_add", text="Gamma Crossfade").type = 'GAMMA_CROSS'

        col.separator()

        col.operator("sequencer.effect_strip_add", text="Wipe").type = 'WIPE'
        col.enabled = selected_seq >= 2


class SEQUENCER_MT_add_effect(Menu):
    bl_label = "Effect Strip"

    def draw(self, context):
        def sel_sequences(context):
            return len(getattr(context, "selected_sequences", ())) 

        selected_seq = sel_sequences(context)

        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'

        col = layout.column()
        col.operator("sequencer.effect_strip_add", text="Add").type = 'ADD'
        col.operator("sequencer.effect_strip_add", text="Subtract").type = 'SUBTRACT'
        col.operator("sequencer.effect_strip_add", text="Multiply").type = 'MULTIPLY'
        col.operator("sequencer.effect_strip_add", text="Over Drop").type = 'OVER_DROP'
        col.operator("sequencer.effect_strip_add", text="Alpha Over").type = 'ALPHA_OVER'
        col.operator("sequencer.effect_strip_add", text="Alpha Under").type = 'ALPHA_UNDER'
        col.operator("sequencer.effect_strip_add", text="Color Mix").type = 'COLORMIX'
        col.enabled = selected_seq >=2

        layout.separator()

        layout.operator("sequencer.effect_strip_add", text="Multicam Selector").type = 'MULTICAM'

        layout.separator()

        col = layout.column()
        col.operator("sequencer.effect_strip_add", text="Transform").type = 'TRANSFORM'
        col.operator("sequencer.effect_strip_add", text="Speed Control").type = 'SPEED'

        col.separator()

        col.operator("sequencer.effect_strip_add", text="Glow").type = 'GLOW'
        col.operator("sequencer.effect_strip_add", text="Gaussian Blur").type = 'GAUSSIAN_BLUR'
        col.enabled = selected_seq != 0


class SEQUENCER_MT_cut(Menu):
    bl_label = "Cut"

    def draw(self, context):
        layout = self.layout

        layout.operator("sequencer.cut", text="Soft").type = "SOFT"
        layout.operator("sequencer.cut", text="Hard").type = "HARD"

        layout.separator()

        layout.operator("sequencer.preview_and_cut_mode", text="Mode...")

        layout.separator()

        props = layout.operator("sequencer.cut_and_delete", text="Extract Left")
        props.side = "LEFT"
        props.method = True
        props = layout.operator("sequencer.cut_and_delete", text="Extract Right")
        props.side = "RIGHT"
        props.method = True

        layout.separator()

        props = layout.operator("sequencer.cut_and_delete", text="Lift Left")
        props.side = "LEFT"
        props.method = False       
        props = layout.operator("sequencer.cut_and_delete", text="Lift Right")
        props.side = "RIGHT"
        props.method = False
        

class SEQUENCER_MT_edit_remove(Menu):
    bl_label = "Delete"

    def draw(self, context):
        layout = self.layout

        layout.operator("sequencer.delete_lift", text="Lift")
        layout.operator("sequencer.ripple_delete", text="Extract")


class SEQUENCER_MT_edit(Menu):
    bl_label = "Edit"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.menu("SEQUENCER_MT_edit_remove")
        layout.operator("sequencer.copy", text="Copy", icon="COPYDOWN")
        layout.operator("sequencer.paste", text="Paste", icon="PASTEDOWN")

        layout.separator()

        layout.operator("sequencer.duplicate_move")
        layout.operator("sequencer.extend_to_fill")

        layout.separator()

        layout.operator("sequencer.meta_toggle", text="Toggle Meta")


class SEQUENCER_MT_strip_input(Menu):
    bl_label = "Inputs"

    def draw(self, context):
        layout = self.layout
        strip = act_strip(context)

        layout.operator("sequencer.reload", text="Reload Strips")
        layout.operator("sequencer.reload", text="Reload Strips and Adjust Length").adjust_length = True
        prop = layout.operator("sequencer.change_path", text="Change Path/Files")
        layout.operator("sequencer.swap_data", text="Swap Data")

        if strip:
            stype = strip.type

            if stype == 'IMAGE':
                prop.filter_image = True
            elif stype == 'MOVIE':
                prop.filter_movie = True
            elif stype == 'SOUND':
                prop.filter_sound = True


class SEQUENCER_MT_strip_movie(Menu):
    bl_label = "Movie"

    def draw(self, context):
        layout = self.layout

        layout.operator("sequencer.deinterlace_selected_strips", text="Deinterlace")
        layout.operator("sequencer.reverse_selected_strips", text="Reverse")
        layout.operator("sequencer.flip_x_selected_strips", text="Flip X")
        layout.operator("sequencer.flip_y_selected_strips", text="Flip Y")

        layout.separator()

        layout.operator("sequencer.rendersize")


class SEQUENCER_MT_strip_mute(Menu):
    bl_label = "Mute"

    def draw(self, context):
        layout = self.layout

        layout.operator("sequencer.mute", text="Mute").unselected = False
        layout.operator("sequencer.unmute", text="Un-Mute").unselected = False

        layout.separator()

        layout.operator("sequencer.mute", text="Mute Deselected").unselected = True
        layout.operator("sequencer.unmute", text="Un-Mute Deselected").unselected = True


class SEQUENCER_MT_strip_effect(Menu):
    bl_label = "Effect"

    def draw(self, context):
        layout = self.layout

        layout.operator_menu_enum("sequencer.change_effect_input", "swap")
        layout.operator_menu_enum("sequencer.change_effect_type", "type")
        layout.operator("sequencer.reassign_inputs")
        layout.operator("sequencer.swap_inputs")


class SEQUENCER_MT_strip(Menu):
    bl_label = "Strip"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.menu("SEQUENCER_MT_strip_mute")

        layout.separator()

        layout.operator("sequencer.lock", text = "Lock", icon='LOCKED')
        layout.operator("sequencer.unlock", text = "Unlock", icon='UNLOCKED')

        layout.separator()

        layout.operator("sequencer.meta_make")

        strip = act_strip(context)

        if strip:
            stype = strip.type

            if stype in {
                    'CROSS', 'ADD', 'SUBTRACT', 'ALPHA_OVER', 'ALPHA_UNDER',
                    'GAMMA_CROSS', 'MULTIPLY', 'OVER_DROP', 'WIPE', 'GLOW',
                    'TRANSFORM', 'COLOR', 'SPEED', 'MULTICAM', 'ADJUSTMENT',
                    'GAUSSIAN_BLUR', 'TEXT',
            }:

                layout.separator()

                layout.menu("SEQUENCER_MT_strip_effect")

            elif stype in {'MOVIE'}:

                layout.separator()

                layout.menu("SEQUENCER_MT_strip_movie")

            elif stype in {'IMAGE'}:

                layout.separator()

                layout.operator("sequencer.rendersize")
                layout.operator("sequencer.images_separate")

            elif stype == 'META':

                layout.operator("sequencer.meta_separate", text = "Un-Meta")

            elif stype == 'SOUND':
                st = context.space_data
                strip = act_strip(context)
                sound = strip.sound
                if st.waveform_display_type == 'DEFAULT_WAVEFORMS':

                    layout.separator()

                    #layout.prop(strip, "show_waveform") # only for active strip, but with checkbox.
                    layout.operator("sequencer.show_waveform_selected_strips", text = "Toggle Draw Waveform")

            if stype != 'SOUND':

                layout.separator()

                layout.operator_menu_enum("sequencer.strip_modifier_add", "type", text="Add Modifier")
                layout.operator("sequencer.strip_modifier_copy", text = "Copy Modifiers to Selection")

        layout.separator()

        #layout.operator("sequencer.offset_clear") #Replaced by match frame
        layout.operator("sequencer.match_frame")

        layout.operator("sequencer.rebuild_proxy")

        layout.separator()

        layout.menu("SEQUENCER_MT_strip_input")


class SequencerButtonsPanel:
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    @staticmethod
    def has_sequencer(context):
        return (context.space_data.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'})

    @classmethod
    def poll(cls, context):
        return cls.has_sequencer(context) and (act_strip(context) is not None)


class SequencerButtonsPanel_Output:
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    @staticmethod
    def has_preview(context):
        st = context.space_data
        return (st.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}) or st.show_backdrop

    @classmethod
    def poll(cls, context):
        return cls.has_preview(context)


class SEQUENCER_PT_edit(SequencerButtonsPanel, Panel):
    bl_label = "Edit Strip"
    bl_category = "Strip"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  

        scene = context.scene
        frame_current = scene.frame_current
        strip = act_strip(context)

        row = layout.row(align=True)
        row.prop(strip, "name", text=""+strip.type.title()+"")
        row.prop(strip, "lock", toggle=True, icon_only=True)

        if strip.type != 'SOUND':

            layout.prop(strip, "blend_type", text="Blend")

            row = layout.row(align=True)
            sub = row.row(align=True)
            sub.active = (not strip.mute)

            sub.prop(strip, "blend_alpha", text="Opacity", slider=True)
            sub.prop(strip, "mute", toggle=True, icon_only=True)

            if strip.type == 'SCENE':
                scene = strip.scene
                if scene:

                    row = layout.row(align=True)
                    sub = row.row(align=True)
                    sub.active = (not strip.mute)

                    sub.prop(scene, "audio_volume", text="Volume")

                    if strip.mute:
                        icon = "MUTE_IPO_OFF"
                    else:
                        icon = "MUTE_IPO_ON"

                    sub.prop(strip, "mute", toggle=True, icon_only=True, icon=icon) #icon not working!

            layout.prop(strip, "use_translation", text="Image Offset")
            if strip.use_translation:
                layout.prop(strip.transform, "offset_x", text="X")
                layout.prop(strip.transform, "offset_y", text="Y")

            layout.prop(strip, "use_crop", text="Image Crop")
            if strip.use_crop:
                col = layout.column(align=True)
                col.prop(strip.crop, "max_y")
                row = col.row(align=True)
                row.prop(strip.crop, "min_x", text = "Left/Right")
                row.prop(strip.crop, "max_x", text = "")
                col.prop(strip.crop, "min_y")

        if strip.type == 'SOUND':

            st = context.space_data
            sound = strip.sound

            col = layout.column()

            row = col.row(align=True)
            sub = row.row(align=True)
            sub.active = (not strip.mute)

            sub.prop(scene, "audio_volume", text="Volume")

            if strip.mute:
                icon = "MUTE_IPO_OFF"
            else:
                icon = "MUTE_IPO_ON"

            sub.prop(strip, "mute", toggle=True, icon_only=True, icon=icon) #Icon not working!

            col.prop(strip, "pitch")
            col.prop(strip, "pan")

            if sound is not None:

                row = layout.row()
                if st.waveform_display_type == 'DEFAULT_WAVEFORMS':
                    row = row.split(factor=0.60)
                    row.prop(strip, "show_waveform")
                row.prop(sound, "use_mono")


class SEQUENCER_PT_effect(SequencerButtonsPanel, Panel):
    bl_label = "Effect Strip"
    bl_category = "Strip"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return strip.type in {
            'ADD', 'SUBTRACT', 'ALPHA_OVER', 'ALPHA_UNDER',
            'CROSS', 'GAMMA_CROSS', 'MULTIPLY', 'OVER_DROP',
            'WIPE', 'GLOW', 'TRANSFORM', 'COLOR', 'SPEED',
            'MULTICAM', 'GAUSSIAN_BLUR', 'TEXT', 'COLORMIX'
        }

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        strip = act_strip(context)

        if strip.input_count > 0:
            col = layout.column()
            col.enabled = False
            col.prop(strip, "input_1")
            if strip.input_count > 1:
                col.prop(strip, "input_2")

        if strip.type == 'COLOR':
            layout.prop(strip, "color")

        elif strip.type == 'WIPE':
            col = layout.column()
            col.prop(strip, "transition_type")
            col.alignment = "RIGHT"
            col.row().prop(strip, "direction", expand=True)

            col = layout.column()
            col.prop(strip, "blur_width", slider=True)
            if strip.transition_type in {'SINGLE', 'DOUBLE'}:
                col.prop(strip, "angle")

        elif strip.type == 'GLOW':
            flow = layout.column_flow()
            flow.prop(strip, "threshold", slider=True)
            flow.prop(strip, "clamp", slider=True)
            flow.prop(strip, "boost_factor")
            flow.prop(strip, "blur_radius")

            row = layout.row()
            row.prop(strip, "quality", slider=True)
            row.prop(strip, "use_only_boost")

        elif strip.type == 'SPEED':
            layout.prop(strip, "use_default_fade", text="Stretch to input strip length")
            if not strip.use_default_fade:
                layout.prop(strip, "use_as_speed")
                if strip.use_as_speed:
                    layout.prop(strip, "speed_factor")
                else:
                    layout.prop(strip, "speed_factor", text="Frame Number")
                    layout.prop(strip, "scale_to_length")

        elif strip.type == 'TRANSFORM':
            layout = self.layout
            col = layout.column()

            col.prop(strip, "interpolation")
            col.prop(strip, "translation_unit")
            layout=layout.column(align=True)
            layout.prop(strip, "translate_start_x", text="Position X")
            layout.prop(strip, "translate_start_y", text="Y")

            layout.separator()

            col = layout.column(align=True)
            col.prop(strip, "use_uniform_scale")
            if strip.use_uniform_scale:
                col = layout.column(align=True)
                col.prop(strip, "scale_start_x", text="Scale")
            else:
                layout.prop(strip, "scale_start_x", text="Scale X")
                layout.prop(strip, "scale_start_y", text="Y")

            layout.separator()

            layout.prop(strip, "rotation_start", text="Rotation")

        elif strip.type == 'MULTICAM':
            col = layout.column(align=True)
            strip_channel = strip.channel

            col.prop(strip, "multicam_source", text="Source Channel")

            # The multicam strip needs at least 2 strips to be useful
            if strip_channel > 2:
                BT_ROW = 4
                #col.alignment = "RIGHT"
                col.label(text="    Cut to")
                row = col.row()

                for i in range(1, strip_channel):
                    if (i % BT_ROW) == 1:
                        row = col.row(align=True)

                    # Workaround - .enabled has to have a separate UI block to work
                    if i == strip.multicam_source:
                        sub = row.row(align=True)
                        sub.enabled = False
                        sub.operator("sequencer.cut_multicam", text=f"{i:d}").camera = i
                    else:
                        sub_1 = row.row(align=True)
                        sub_1.enabled = True
                        sub_1.operator("sequencer.cut_multicam", text=f"{i:d}").camera = i

                if strip.channel > BT_ROW and (strip_channel - 1) % BT_ROW:
                    for i in range(strip.channel, strip_channel + ((BT_ROW + 1 - strip_channel) % BT_ROW)):
                        row.label(text="")
            else:
                col.separator()
                col.label(text="Two or more channels are needed below this strip", icon='INFO')

        elif strip.type == 'TEXT':
            col = layout.column()
            col.prop(strip, "text")
            col.template_ID(strip, "font", open="font.open", unlink="font.unlink")            
            col.prop(strip, "font_size")

            row = col.row()
            row.prop(strip, "color")
            row = col.row()
            row.prop(strip, "use_shadow")
            rowsub = row.row()
            rowsub.active = strip.use_shadow
            rowsub.prop(strip, "shadow_color", text="")

            col.prop(strip, "align_x")
            col.prop(strip, "align_y", text = "Y")
            row = col.row(align=True)
            row.prop(strip, "location", text="Location")
            col.prop(strip, "wrap_width")
            
            layout.operator("sequencer.export_subtitles", text="Export Subtitles", icon='EXPORT')

        col = layout.column(align=True)
        if strip.type == 'SPEED':
            col.prop(strip, "multiply_speed")
        elif strip.type in {'CROSS', 'GAMMA_CROSS', 'WIPE', 'ALPHA_OVER', 'ALPHA_UNDER', 'OVER_DROP'}:
            col.prop(strip, "use_default_fade", text="Default fade")
            if not strip.use_default_fade:
                col.prop(strip, "effect_fader", text="Effect Fader")
        elif strip.type == 'GAUSSIAN_BLUR':
            layout = layout.column(align=True)
            layout.prop(strip, "size_x", text = "Size X")
            layout.prop(strip, "size_y", text = "Y")
        elif strip.type == 'COLORMIX':
            layout.prop(strip, "blend_effect", text="Blend Mode")
            row = layout.row(align=True)
            row.prop(strip, "factor", slider=True)


class SEQUENCER_PT_input(SequencerButtonsPanel, Panel):
    bl_label = "Strip Input"
    bl_category = "Strip"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return strip.type in {'MOVIE', 'IMAGE'}

        ''', 'SCENE', 'MOVIECLIP', 'META',
        'ADD', 'SUBTRACT', 'ALPHA_OVER', 'ALPHA_UNDER',
        'CROSS', 'GAMMA_CROSS', 'MULTIPLY', 'OVER_DROP',
        'WIPE', 'GLOW', 'TRANSFORM', 'COLOR',
        'MULTICAM', 'SPEED', 'ADJUSTMENT', 'COLORMIX' }'''

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene

        strip = act_strip(context)

        seq_type = strip.type

        # draw a filename if we have one
        if seq_type == 'IMAGE':
            layout.prop(strip, "directory", text="")

            # Current element for the filename

            elem = strip.strip_elem_from_frame(scene.frame_current)
            if elem:
                layout.prop(elem, "filename", text="")  # strip.elements[0] could be a fallback

            layout.prop(strip.colorspace_settings, "name", text="Color Space")

            layout.prop(strip, "alpha_mode", text="Alpha")
            sub = layout.column(align=True)
            sub.operator("sequencer.change_path", text="Change Data/Files", icon='FILEBROWSER').filter_image = True

        elif seq_type == 'MOVIE':
            layout.prop(strip, "filepath", text="")

            layout.prop(strip.colorspace_settings, "name", text="Color Space")

            layout.prop(strip, "mpeg_preseek")
            layout.prop(strip, "stream_index")

        if scene.render.use_multiview and seq_type in {'IMAGE', 'MOVIE'}:
            layout.prop(strip, "use_multiview")

            col = layout.column()
            col.active = strip.use_multiview

            col.row().prop(strip, "views_format", expand=True)

            box = col.box()
            box.active = strip.views_format == 'STEREO_3D'
            box.template_image_stereo_3d(strip.stereo_3d_format)


class SEQUENCER_PT_sound(SequencerButtonsPanel, Panel):
    bl_label = "Sound"
    bl_category = "Strip"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return (strip.type == 'SOUND')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        st = context.space_data
        strip = act_strip(context)
        sound = strip.sound

        layout.template_ID(strip, "sound", open="sound.open")
        if sound is not None:
            layout.prop(sound, "filepath", text="")

            layout.use_property_split = True
            layout.use_property_decorate = False

            layout.alignment = 'RIGHT'
            sub = layout.column(align=True)
            split = sub.split(factor=0.5, align=True)
            split.alignment = 'RIGHT'
            if sound.packed_file:
                split.label(text="Unpack")
                split.operator("sound.unpack", icon='PACKAGE', text="")
            else:
                split.label(text="Pack")
                split.operator("sound.pack", icon='UGLYPACKAGE', text="")

            layout.prop(sound, "use_memory_cache")


class SEQUENCER_PT_scene(SequencerButtonsPanel, Panel):
    bl_label = "Scene"
    bl_category = "Strip"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return (strip.type == 'SCENE')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        strip = act_strip(context)

        layout.template_ID(strip, "scene")

        scene = strip.scene
        layout.prop(strip, "use_sequence")

        if not strip.use_sequence:
            layout.alignment = 'RIGHT'
            sub = layout.column(align=True)
            split = sub.split(factor=0.5, align=True)
            split.alignment = 'RIGHT'
            split.label(text="Camera Override")
            split.template_ID(strip, "scene_camera")

            layout.prop(strip, "use_grease_pencil", text="Show Grease Pencil")

        if not strip.use_sequence:
            if scene:
                # Warning, this is not a good convention to follow.
                # Expose here because setting the alpha from the 'Render' menu is very inconvenient.
                #layout.label(text="Preview")
                layout.prop(scene.render, "alpha_mode")


class SEQUENCER_PT_mask(SequencerButtonsPanel, Panel):
    bl_label = "Mask"
    bl_category = "Strip"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return (strip.type == 'MASK')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        strip = act_strip(context)

        layout.template_ID(strip, "mask")

        mask = strip.mask

        if mask:
            sta = mask.frame_start
            end = mask.frame_end
            layout.label(text=iface_("Original frame range: %d-%d (%d)") % (sta, end, end - sta + 1), translate=False)


class SEQUENCER_PT_data(SequencerButtonsPanel, Panel):
    bl_label = "Strip Data"
    bl_category = "Strip"
    #bl_parent_id = "SEQUENCER_PT_edit"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return strip.type

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = False

        scene = context.scene
        frame_current = scene.frame_current
        strip = act_strip(context)

        length_list = [str(strip.frame_start), str(strip.frame_final_end), str(strip.frame_final_duration), str(strip.frame_offset_start), str(strip.frame_offset_end), str(strip.animation_offset_start), str(strip.animation_offset_end)]
        max_length = max(len(x) for x in length_list)
        max_factor = (1.9-max_length)/30

        sub = layout.row(align=True)
        sub.enabled = not strip.lock
        split = sub.split(factor=0.5+max_factor)
        split.alignment = 'RIGHT'
        split.label(text='Channel')
        split.prop(strip, "channel", text="")

        sub = layout.column(align=True)
        sub.enabled = not strip.lock
        split = sub.split(factor=0.5+max_factor)
        split.alignment = 'RIGHT'
        split.label(text="Start")
        split.prop(strip, "frame_start", text=str(bpy.utils.smpte_from_frame(strip.frame_start)).replace(':', ' '))
        split = sub.split(factor=0.5+max_factor)
        split.alignment = 'RIGHT'
        split.label(text="End")
        split.prop(strip, "frame_final_end", text=str(bpy.utils.smpte_from_frame(strip.frame_final_end)).replace(':', ' '))
        split = sub.split(factor=0.5+max_factor)
        split.alignment = 'RIGHT'
        split.label(text="Duration")
        split.prop(strip, "frame_final_duration", text=str(bpy.utils.smpte_from_frame(strip.frame_final_duration)).replace(':', ' '))

        if not isinstance(strip, bpy.types.EffectSequence):
            layout.alignment = 'RIGHT'
            sub = layout.column(align=True)
            split = sub.split(factor=0.5+max_factor, align=True)
            split.alignment = 'RIGHT'
            split.label(text="Soft Trim Start")
            split.prop(strip, "frame_offset_start", text=str(bpy.utils.smpte_from_frame(strip.frame_offset_start)).replace(':', ' '))
            split = sub.split(factor=0.5+max_factor, align=True)
            split.alignment = 'RIGHT'
            split.label(text='End')
            split.prop(strip, "frame_offset_end", text=str(bpy.utils.smpte_from_frame(strip.frame_offset_end)).replace(':', ' '))

            layout.alignment = 'RIGHT'
            sub = layout.column(align=True)
            split = sub.split(factor=0.5+max_factor)
            split.alignment = 'RIGHT'
            split.label(text="Hard Trim Start")
            split.prop(strip, "animation_offset_start", text=str(bpy.utils.smpte_from_frame(strip.animation_offset_start)).replace(':', ' '))
            split = sub.split(factor=0.5+max_factor, align=True)
            split.alignment = 'RIGHT'
            split.label(text='End')
            split.prop(strip, "animation_offset_end", text=str(bpy.utils.smpte_from_frame(strip.animation_offset_end)).replace(':', ' '))

        playhead = frame_current - strip.frame_start
        col = layout.column(align=True)
        col = col.box()
        col.active = (frame_current >= strip.frame_start and frame_current <= strip.frame_start + strip.frame_final_duration)
        split = col.split(factor=0.5+max_factor)
        split.alignment = 'RIGHT'
        split.label(text="Playhead")
        split.label(text="%s:   %s" % ((bpy.utils.smpte_from_frame(playhead).replace(':', ' ')), (str(playhead))))

        ''' Old data - anyone missing this data?
        col.label(text=iface_("Frame Offset %d:%d") % (strip.frame_offset_start, strip.frame_offset_end),
                  translate=False)
        col.label(text=iface_("Frame Still %d:%d") % (strip.frame_still_start, strip.frame_still_end), translate=False)'''

        elem = False

        if strip.type == 'IMAGE':
            elem = strip.strip_elem_from_frame(frame_current)
        elif strip.type == 'MOVIE':
            elem = strip.elements[0]

        if strip.type != "SOUND":
            split = col.split(factor=0.5+max_factor)
            split.alignment = 'RIGHT'
            split.label(text="Resolution")
            if elem and elem.orig_width > 0 and elem.orig_height > 0:
                split.label(text="%dx%d" % (elem.orig_width, elem.orig_height), translate=False)
            else:
                split.label(text="None")

        if strip.type == "SCENE":
            scene = strip.scene

            if scene:
                sta = scene.frame_start
                end = scene.frame_end
                split = col.split(factor=0.5+max_factor)
                split.alignment = 'RIGHT'
                split.label(text="Original Frame Range")
                split.alignment = 'LEFT'
                split.label(text="%d-%d (%d)" % (sta, end, end - sta + 1), translate=False)


class SEQUENCER_PT_filter(SequencerButtonsPanel, Panel):
    bl_label = "Filter"
    bl_category = "Strip"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return strip.type in {
            'MOVIE', 'IMAGE', 'SCENE', 'MOVIECLIP', 'MASK',
            'META', 'ADD', 'SUBTRACT', 'ALPHA_OVER',
            'ALPHA_UNDER', 'CROSS', 'GAMMA_CROSS', 'MULTIPLY',
            'OVER_DROP', 'WIPE', 'GLOW', 'TRANSFORM', 'COLOR',
            'MULTICAM', 'SPEED', 'ADJUSTMENT', 'COLORMIX'
        }

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        strip = act_strip(context)

        col = layout.column()
        col.prop(strip, "strobe")

        if strip.type == 'MOVIECLIP':
            col = layout.column()
            col.label(text="Tracker")
            col.prop(strip, "stabilize2d")

            col = layout.column()
            col.label(text="Distortion")
            col.prop(strip, "undistort")

        split = layout.split(factor=0.6)
        col = split.column()
        col.prop(strip, "use_reverse_frames", text="Reverse")
        col.prop(strip, "use_deinterlace")

        col = split.column()
        col.prop(strip, "use_flip_x", text="X Flip")
        col.prop(strip, "use_flip_y", text="Y Flip")

        col = layout.column(align=True)
        col.prop(strip, "color_saturation", text="Saturation")
        col.prop(strip, "color_multiply", text="Multiply")
        layout.prop(strip, "use_float", text="Convert to Float")


class SEQUENCER_PT_proxy(SequencerButtonsPanel, Panel):
    bl_label = "Proxy/Timecode"
    bl_category = "Strip"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return strip.type in {'MOVIE', 'IMAGE', 'SCENE', 'META', 'MULTICAM'}

    def draw_header(self, context):
        strip = act_strip(context)

        self.layout.prop(strip, "use_proxy", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        ed = context.scene.sequence_editor

        strip = act_strip(context)

        if strip.proxy:
            proxy = strip.proxy

            flow = layout.column_flow()
            flow.prop(ed, "proxy_storage", text="Storage")
            if ed.proxy_storage == 'PROJECT':
                flow.prop(ed, "proxy_dir", text="Directory")
            else:
                flow.prop(proxy, "use_proxy_custom_directory")
                flow.prop(proxy, "use_proxy_custom_file")

                if proxy.use_proxy_custom_directory and not proxy.use_proxy_custom_file:
                    flow.prop(proxy, "directory")
                if proxy.use_proxy_custom_file:
                    flow.prop(proxy, "filepath")

            layout = layout.box()
            row = layout.row(align=True)
            row.prop(strip.proxy, "build_25")
            row.prop(strip.proxy, "build_75")
            row = layout.row(align=True)
            row.prop(strip.proxy, "build_50")
            row.prop(strip.proxy, "build_100")

            layout = self.layout
            layout.use_property_split = True
            layout.use_property_decorate = False

            layout.prop(proxy, "use_overwrite")

            col = layout.column()
            col.prop(proxy, "quality", text="Build JPEG Quality")

            if strip.type == 'MOVIE':
                col = layout.column()

                col.prop(proxy, "timecode", text="Timecode Index")

        col = layout.column()
        col.operator("sequencer.enable_proxies")
        col.operator("sequencer.rebuild_proxy")


class SEQUENCER_PT_preview(SequencerButtonsPanel_Output, Panel):
    bl_label = "Scene Preview/Render"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        render = context.scene.render

        col = layout.column()
        col.prop(render, "sequencer_gl_preview", text="")

        row = col.row()
        row.active = render.sequencer_gl_preview == 'SOLID'
        row.prop(render, "use_sequencer_gl_textured_solid")

        col.prop(render, "use_sequencer_gl_dof")


class SEQUENCER_PT_view(SequencerButtonsPanel_Output, Panel):
    bl_label = "View Settings"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        st = context.space_data

        col = layout.column()
        if st.display_mode == 'IMAGE':
            col.prop(st, "show_overexposed")
            col.separator()

        elif st.display_mode == 'WAVEFORM':
            col.prop(st, "show_separate_color")

        col = layout.column()
        col.separator()
        col.prop(st, "proxy_render_size")


class SEQUENCER_PT_view_safe_areas(SequencerButtonsPanel_Output, Panel):
    bl_label = "Safe Areas"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        st = context.space_data
        is_preview = st.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}
        return is_preview and (st.display_mode == 'IMAGE')

    def draw_header(self, context):
        st = context.space_data

        self.layout.prop(st, "show_safe_areas", text="")

    def draw(self, context):
        from .properties_data_camera import draw_display_safe_settings

        layout = self.layout

        st = context.space_data
        safe_data = context.scene.safe_areas

        draw_display_safe_settings(layout, safe_data, st)


class SEQUENCER_PT_modifiers(SequencerButtonsPanel, Panel):
    bl_label = "Modifiers"
    bl_category = "Modifiers"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        strip = act_strip(context)
        ed = context.scene.sequence_editor

        layout.prop(strip, "use_linear_modifiers")

        layout.operator_menu_enum("sequencer.strip_modifier_add", "type")
        layout.operator("sequencer.strip_modifier_copy")

        for mod in strip.modifiers:
            box = layout.box()

            row = box.row()
            row.prop(mod, "show_expanded", text="", emboss=False)
            row.prop(mod, "name", text="")

            row.prop(mod, "mute", text="")

            sub = row.row(align=True)
            props = sub.operator("sequencer.strip_modifier_move", text="", icon='TRIA_UP')
            props.name = mod.name
            props.direction = 'UP'
            props = sub.operator("sequencer.strip_modifier_move", text="", icon='TRIA_DOWN')
            props.name = mod.name
            props.direction = 'DOWN'

            row.operator("sequencer.strip_modifier_remove", text="", icon='X', emboss=False).name = mod.name

            if mod.show_expanded:
                row = box.row()
                row.prop(mod, "input_mask_type", expand=True)

                if mod.input_mask_type == 'STRIP':
                    sequences_object = ed
                    if ed.meta_stack:
                        sequences_object = ed.meta_stack[-1]
                    box.prop_search(mod, "input_mask_strip", sequences_object, "sequences", text="Mask")
                else:
                    box.prop(mod, "input_mask_id")
                    row = box.row()
                    row.prop(mod, "mask_time", expand=True)

                if mod.type == 'COLOR_BALANCE':
                    box.prop(mod, "color_multiply")
                    draw_color_balance(box, mod.color_balance)
                elif mod.type == 'CURVES':
                    box.template_curve_mapping(mod, "curve_mapping", type='COLOR', show_tone=True)
                elif mod.type == 'HUE_CORRECT':
                    box.template_curve_mapping(mod, "curve_mapping", type='HUE')
                elif mod.type == 'BRIGHT_CONTRAST':
                    col = box.column()
                    col.prop(mod, "bright")
                    col.prop(mod, "contrast")
                elif mod.type == 'WHITE_BALANCE':
                    col = box.column()
                    col.prop(mod, "white_value")
                elif mod.type == 'TONEMAP':
                    col = box.column()
                    col.prop(mod, "tonemap_type")
                    if mod.tonemap_type == 'RD_PHOTORECEPTOR':
                        col.prop(mod, "intensity")
                        col.prop(mod, "contrast")
                        col.prop(mod, "adaptation")
                        col.prop(mod, "correction")
                    elif mod.tonemap_type == 'RH_SIMPLE':
                        col.prop(mod, "key")
                        col.prop(mod, "offset")
                        col.prop(mod, "gamma")


class SEQUENCER_PT_grease_pencil(AnnotationDataPanel, SequencerButtonsPanel_Output, Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    # NOTE: this is just a wrapper around the generic GP Panel
    # But, it should only show up when there are images in the preview region


class SEQUENCER_PT_grease_pencil_tools(GreasePencilToolsPanel, SequencerButtonsPanel_Output, Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    # NOTE: this is just a wrapper around the generic GP tools panel
    # It contains access to some essential tools usually found only in
    # toolbar, which doesn't exist here...


class SEQUENCER_PT_custom_props(SequencerButtonsPanel, PropertyPanel, Panel):
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}
    _context_path = "scene.sequence_editor.active_strip"
    _property_type = (bpy.types.Sequence,)
    bl_category = "Strip"


classes = (
    SEQUENCER_HT_header,
    SEQUENCER_MT_editor_menus,
    SEQUENCER_MT_view,
    SEQUENCER_MT_view_render,
    SEQUENCER_MT_view_toggle,
    SEQUENCER_MT_preview_zoom,
    SEQUENCER_MT_view_zoom,
    SEQUENCER_MT_view_preview,
    SEQUENCER_MT_select_cursor,
    SEQUENCER_MT_select_handle,
    SEQUENCER_MT_select_channel,
    SEQUENCER_MT_select_Mouse,
    SEQUENCER_MT_select_linked,
    SEQUENCER_MT_select,
    SEQUENCER_MT_add,
    SEQUENCER_MT_add_effect,
    SEQUENCER_MT_add_transitions,
    SEQUENCER_MT_add_empty,
    SEQUENCER_MT_edit,
    SEQUENCER_MT_edit_input,
    SEQUENCER_MT_cut,
    SEQUENCER_MT_edit_remove,
    SEQUENCER_MT_transform,
    SEQUENCER_MT_transform_gaps,
    SEQUENCER_MT_transform_move,
    SEQUENCER_MT_strip,
    SEQUENCER_MT_strip_movie,
    SEQUENCER_MT_strip_input,
    SEQUENCER_MT_strip_mute,
    SEQUENCER_MT_strip_effect,
    SEQUENCER_MT_navigation,
    SEQUENCER_MT_navigation_play,
    SEQUENCER_MT_navigation_frame,
    SEQUENCER_MT_navigation_cut,
    SEQUENCER_MT_navigation_strip,
    SEQUENCER_MT_navigation_keyframe,
    SEQUENCER_MT_navigation_range,
    SEQUENCER_MT_marker,
    SEQUENCER_PT_edit,
    SEQUENCER_PT_effect,
    SEQUENCER_PT_input,
    SEQUENCER_PT_sound,
    SEQUENCER_PT_scene,
    SEQUENCER_PT_mask,
    SEQUENCER_PT_filter,
    SEQUENCER_PT_data,
    SEQUENCER_PT_proxy,
    SEQUENCER_PT_preview,
    SEQUENCER_PT_view,
    SEQUENCER_PT_view_safe_areas,
    SEQUENCER_PT_modifiers,
    SEQUENCER_PT_grease_pencil,
    SEQUENCER_PT_grease_pencil_tools,
    SEQUENCER_PT_custom_props,

)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
