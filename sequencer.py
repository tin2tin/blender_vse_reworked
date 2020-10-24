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
import time
from bpy.types import Operator
from operator import attrgetter
from bpy.props import (
    IntProperty,
    BoolProperty,
    EnumProperty,
    StringProperty,
)


class SEQUENCER_OT_crossfade_sounds(Operator):
    """Do cross-fading volume animation of two selected sound strips"""

    bl_idname = "sequencer.crossfade_sounds"
    bl_label = "Crossfade sounds"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if (
            context.scene
            and context.scene.sequence_editor
            and context.scene.sequence_editor.active_strip
        ):
            return context.scene.sequence_editor.active_strip.type == "SOUND"
        else:
            return False

    def execute(self, context):
        seq1 = None
        seq2 = None
        for s in context.scene.sequence_editor.sequences:
            if s.select and s.type == "SOUND":
                if seq1 is None:
                    seq1 = s
                elif seq2 is None:
                    seq2 = s
                else:
                    seq2 = None
                    break
        if seq2 is None:
            self.report({"ERROR"}, "Select 2 sound strips")
            return {"CANCELLED"}
        if seq1.frame_final_start > seq2.frame_final_start:
            s = seq1
            seq1 = seq2
            seq2 = s
        if seq1.frame_final_end > seq2.frame_final_start:
            tempcfra = context.scene.frame_current
            context.scene.frame_current = seq2.frame_final_start
            seq1.keyframe_insert("volume")
            context.scene.frame_current = seq1.frame_final_end
            seq1.volume = 0
            seq1.keyframe_insert("volume")
            seq2.keyframe_insert("volume")
            context.scene.frame_current = seq2.frame_final_start
            seq2.volume = 0
            seq2.keyframe_insert("volume")
            context.scene.frame_current = tempcfra
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, "The selected strips don't overlap")
            return {"CANCELLED"}


class SEQUENCER_OT_cut_multicam(Operator):
    """Cut multi-cam strip and select camera"""

    bl_idname = "sequencer.cut_multicam"
    bl_label = "Cut multicam"
    bl_options = {"REGISTER", "UNDO"}

    camera: IntProperty(
        name="Camera",
        min=1,
        max=32,
        soft_min=1,
        soft_max=32,
        default=1,
    )

    @classmethod
    def poll(cls, context):
        if (
            context.scene
            and context.scene.sequence_editor
            and context.scene.sequence_editor.active_strip
        ):
            return context.scene.sequence_editor.active_strip.type == "MULTICAM"
        else:
            return False

    def execute(self, context):
        camera = self.camera

        s = context.scene.sequence_editor.active_strip

        if s.multicam_source == camera or camera >= s.channel:
            return {"FINISHED"}
        if not s.select:
            s.select = True
        cfra = context.scene.frame_current
        bpy.ops.sequencer.cut(frame=cfra, type="SOFT", side="RIGHT")
        for s in context.scene.sequence_editor.sequences_all:
            if (
                s.select
                and s.type == "MULTICAM"
                and s.frame_final_start <= cfra
                and cfra < s.frame_final_end
            ):
                context.scene.sequence_editor.active_strip = s
        context.scene.sequence_editor.active_strip.multicam_source = camera
        return {"FINISHED"}


class SEQUENCER_OT_deinterlace_selected_movies(Operator):
    """Deinterlace all selected movie sources"""

    bl_idname = "sequencer.deinterlace_selected_movies"
    bl_label = "Deinterlace Movies"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene and context.scene.sequence_editor

    def execute(self, context):
        for s in context.scene.sequence_editor.sequences_all:
            if s.select and s.type == "MOVIE":
                s.use_deinterlace = True
        return {"FINISHED"}


class SEQUENCER_OT_reverse_selected_movies(Operator):
    """Reverse all selected movie sources"""

    bl_idname = "sequencer.reverse_selected_movies"
    bl_label = "Reverse Movies"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene and context.scene.sequence_editor

    def execute(self, context):
        for s in context.scene.sequence_editor.sequences_all:
            if s.select:
                if s.type == "MOVIE" or s.type == "IMAGE":
                    s.use_reverse_frames = not s.use_reverse_frames
        return {"FINISHED"}


class SEQUENCER_OT_flip_x_selected_movies(Operator):
    """Flip X of all selected movie sources"""

    bl_idname = "sequencer.flip_x_selected_movies"
    bl_label = "Flip X Movies"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene and context.scene.sequence_editor

    def execute(self, context):
        for s in context.scene.sequence_editor.sequences_all:
            if s.select:
                if s.type == "MOVIE" or s.type == "IMAGE":
                    s.use_flip_x = not s.use_flip_x
        return {"FINISHED"}


class SEQUENCER_OT_flip_y_selected_movies(Operator):
    """Flip Y of all selected movie sources"""

    bl_idname = "sequencer.flip_y_selected_movies"
    bl_label = "Flip Y Movies"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene and context.scene.sequence_editor

    def execute(self, context):
        for s in context.scene.sequence_editor.sequences_all:
            if s.select:
                if s.type == "MOVIE" or s.type == "IMAGE":
                    s.use_flip_y = not s.use_flip_y
        return {"FINISHED"}


class SEQUENCER_OT_show_waveform_selected_sounds(Operator):
    """Toggle draw waveform of all selected audio sources"""

    bl_idname = "sequencer.show_waveform_selected_sounds"
    bl_label = "Show Waveform"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene and context.scene.sequence_editor

    def execute(self, context):

        for strip in context.scene.sequence_editor.sequences_all:
            if strip.select and strip.type == "SOUND":
                strip.show_waveform = not strip.show_waveform
        return {"FINISHED"}


class SEQUENCER_OT_select_current_frame(bpy.types.Operator):
    """Select strips at current frame"""

    bl_idname = "sequencer.select_current_frame"
    bl_label = "Select Strips at Current Frame"
    bl_options = {"REGISTER", "UNDO"}

    extend: EnumProperty(
        name="Extend",
        description="Extend",
        items=(
            ("TRUE", "True", "Extend True"),
            ("FALSE", "False", "Extend False"),
        ),
    )

    @classmethod
    def poll(cls, context):
        return (
            bpy.context.area.type == "SEQUENCE_EDITOR"
            and bpy.context.scene.sequence_editor
        )

    def execute(self, context):
        current_frame = bpy.context.scene.frame_current
        sel_strips = []
        lock_num = 0
        lock_sel_num = 0
        reportMessage = ""
        if self.extend == "FALSE":
            bpy.ops.sequencer.select_all(action="DESELECT")

        for strip in bpy.context.sequences:
            if strip.lock and strip.select:
                lock_sel_num += 1
            if strip.frame_final_end >= current_frame:
                if strip.frame_final_start <= current_frame:
                    if strip.lock and not strip.select:
                        lock_num += 1
                    else:
                        strip.select = True
                        context.scene.sequence_editor.active_strip = strip
                        sel_strips.append(strip)
        if sel_strips != []:
            for strip in sel_strips:
                if strip.frame_final_end == current_frame:
                    strip.select_right_handle = True
                elif strip.frame_final_start == current_frame:
                    strip.select_left_handle = True
        return {"FINISHED"}


class SEQUENCER_OT_select_channel_strips(Operator):
    """Add all strips in channel to selection"""

    bl_idname = "sequencer.select_channel_strips"
    bl_label = "Select Channel Strips"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene and context.scene.sequence_editor

    def execute(self, context):
        selection = bpy.context.selected_sequences
        if not selection:
            return {"CANCELLED"}
        sequences = bpy.context.scene.sequence_editor.sequences_all

        for s in selection:
            for strip in sequences:
                strip.select = strip.channel == s.channel
        return {"FINISHED"}


class SEQUENCER_OT_select_locked_strips(bpy.types.Operator):
    """Select locked strips"""

    bl_idname = "sequencer.select_locked_strips"
    bl_label = "Select Locked Strips"
    bl_description = "Select locked strips"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.sequences:
            return True
        return False

    def execute(self, context):
        lockedStrips = []
        for strip in bpy.context.sequences:
            if strip.lock:
                lockedStrips.append(strip)
        if lockedStrips != []:
            bpy.ops.sequencer.select_all(action="DESELECT")
            for strip in lockedStrips:
                strip.select = True
        return {"FINISHED"}


class SEQUENCER_OT_select_mute_strips(bpy.types.Operator):
    """Select muted strips"""

    bl_idname = "sequencer.select_mute_strips"
    bl_label = "Select Muted"
    bl_description = "Select all muted"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.sequences:
            return True
        return False

    def execute(self, context):
        muteStrips = []
        for strip in bpy.context.sequences:
            if strip.mute:
                muteStrips.append(strip)
        if muteStrips != []:
            bpy.ops.sequencer.select_all(action="DESELECT")
            for strip in muteStrips:
                strip.select = True
        return {"FINISHED"}


class SEQUENCER_OT_audio_mute_toggle(bpy.types.Operator):
    """Toggle audio on/off"""

    bl_idname = "screen.audio_mute_toggle"
    bl_label = "Audio Mute Toggle"
    bl_description = "Toggle all audio on/off"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.sequences:
            return True
        return False

    def execute(self, context):

        bpy.context.scene.use_audio = not bpy.context.scene.use_audio

        return {"FINISHED"}


class SEQUENCER_OT_set_preview_range(bpy.types.Operator):
    """Sets current frame to preview start/end"""

    bl_idname = "sequencer.set_preview_range"
    bl_label = "Set Preview Start/End"
    bl_options = {"REGISTER", "UNDO"}
    type: EnumProperty(
        name="Type",
        description="Set Type",
        items=(
            ("START", "Start", "Set Start"),
            ("END", "End", "Set End"),
        ),
    )

    @classmethod
    def poll(cls, context):
        return bpy.context.scene is not None

    def execute(self, context):
        scene = bpy.context.scene
        if self.type == "END":
            # the -1 below is because we want the scene to end where the cursor is
            # positioned, not one frame after it (as scene.frame_current behaves)
            scene.frame_end = scene.frame_current - 1
            scene.frame_preview_end = scene.frame_current - 1
        else:
            scene.frame_start = scene.frame_current
            scene.frame_preview_start = scene.frame_current
        return {"FINISHED"}


class SEQUENCER_OT_preview_selected(bpy.types.Operator):
    """Sets preview range to selected strips"""

    bl_idname = "sequencer.preview_selected"
    bl_label = "Preview Selected"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bpy.context.scene is not None

    def execute(self, context):
        scene = bpy.context.scene
        selectedStrips = bpy.context.selected_sequences

        reference = 0
        for strip in selectedStrips:
            if strip.frame_final_end > reference:
                reference = strip.frame_final_end
        for strip in selectedStrips:
            stripStart = strip.frame_start + strip.frame_offset_start
            if stripStart < reference:
                reference = stripStart
        scene.frame_start = reference
        scene.frame_preview_start = reference

        for strip in selectedStrips:
            if strip.frame_final_end > reference:
                reference = strip.frame_final_end - 1
        scene.frame_end = reference
        scene.frame_preview_end = reference

        return {"FINISHED"}


class SEQUENCER_OT_split_remove(bpy.types.Operator):
    """Splits selected strips and removes"""

    bl_idname = "sequencer.split_remove"
    bl_label = "Split Remove"
    bl_options = {"REGISTER", "UNDO"}

    direction: EnumProperty(
        name="Direction",
        description="Split Extract Direction",
        items=(
            ("LEFT", "Left", "Split Extract Direction Left"),
            ("RIGHT", "Right", "Split Extract Direction Right"),
        ),
    )
    method: EnumProperty(
        name="Method",
        description="Split Remove Method",
        items=(
            ("EXTRACT", "Extract", "Split Extract"),
            ("LIFT", "Lift", "Split Lift"),
        ),
    )

    @classmethod
    def poll(cls, context):
        if context.sequences:
            return True
        return False

    def execute(self, context):
        scene = bpy.context.scene
        sequencer = bpy.ops.sequencer
        selection = bpy.context.selected_sequences
        if not selection:
            return {"CANCELLED"}
        # Get current frame selection:
        bpy.ops.sequencer.select_current_frame(extend="FALSE")
        cf_selection = bpy.context.selected_sequences
        bpy.ops.sequencer.select_all(action="DESELECT")

        for s in selection:
            for i in cf_selection:
                if not s.lock and s == i:
                    bpy.ops.sequencer.select_all(action="DESELECT")
                    s.select = True
                    sequencer.cut(
                        frame=scene.frame_current, type="SOFT", side=self.direction
                    )
                    if self.method == "EXTRACT":
                        sequencer.ripple_delete()
                    else:
                        sequencer.delete_lift()
                    s.select = False
        for s in selection:
            s.select = True

        return {"FINISHED"}


class SEQUENCER_OT_delete_lift(bpy.types.Operator):
    """Lift selected strips"""

    bl_idname = "sequencer.delete_lift"
    bl_label = "Lift Selection"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.sequences:
            return True
        return False

    def execute(self, context):

        selection = context.selected_sequences
        if not selection:
            return {"CANCELLED"}
        for s in selection:
            if not s.lock:
                bpy.ops.sequencer.select_all(action="DESELECT")
                s.select = True
                bpy.ops.sequencer.delete()
                s.select = False
                for s in selection:
                    s.select = True
        return {"FINISHED"}


class SEQUENCER_OT_ripple_delete(bpy.types.Operator):
    """Ripple delete selected strips"""

    bl_idname = "sequencer.ripple_delete"
    bl_label = "Ripple Delete Selection"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.sequences:
            return True
        return False

    def execute(self, context):

        selection = context.selected_sequences
        selection = sorted(selection, key=attrgetter("channel", "frame_final_start"))

        if not selection:
            return {"CANCELLED"}
        for seq in selection:
            if seq.lock == False:
                context.scene.sequence_editor.active_strip = (
                    seq  # set as active or it won't work
                )
                distance = seq.frame_final_end - seq.frame_final_start
                bpy.ops.sequencer.select_all(action="DESELECT")
                seq.select = True

                bpy.ops.sequencer.select_active_side(
                    side="RIGHT"
                )  # Select to the right
                seq.select = False
                seqs = context.selected_sequences

                bpy.ops.sequencer.select_all(action="DESELECT")  # cut only active strip
                seq.select = True
                seq_out = seq.frame_final_end
                bpy.ops.sequencer.delete()

                seqs = sorted(seqs, key=attrgetter("channel", "frame_final_start"))

                # delete effect strips(ex. dissolves) if they are adjoined selected strips:
                if len(seqs) - 1 > 1:
                    if seqs[1].type in {
                        "CROSS",
                        "ADD",
                        "SUBTRACT",
                        "ALPHA_OVER",
                        "ALPHA_UNDER",
                        "GAMMA_CROSS",
                        "MULTIPLY",
                        "OVER_DROP",
                        "WIPE",
                        "GLOW",
                        "TRANSFORM",
                        "SPEED",
                        "GAUSSIAN_BLUR",
                        "COLORMIX",
                    }:
                        seqs[1].select = True
                        # distance=distance + (seqs[1].frame_final_duration) # can't get the duration of the transition?
                        bpy.ops.sequencer.delete()
                distance = -distance

                for s in seqs:
                    if s.lock == True:
                        break
                    if s.type not in {
                        "CROSS",
                        "ADD",
                        "SUBTRACT",
                        "ALPHA_OVER",
                        "ALPHA_UNDER",
                        "GAMMA_CROSS",
                        "MULTIPLY",
                        "OVER_DROP",
                        "WIPE",
                        "GLOW",
                        "TRANSFORM",
                        "SPEED",
                        "GAUSSIAN_BLUR",
                        "COLORMIX",
                    }:
                        s.frame_start += distance
        return {"FINISHED"}


class SEQUENCER_OT_zoom_vertical(bpy.types.Operator):
    """Zoom vertical"""

    bl_idname = "sequencer.zoom_vertical"
    bl_label = "Zoom Vertical"
    bl_options = {"REGISTER", "UNDO"}

    direction: EnumProperty(
        name="Direction",
        description="Vertical Zoom Direction",
        items=(
            ("OUT", "Out", "Zoom Vertical Out"),
            ("IN", "In", "Zoom Vertical In"),
        ),
    )

    @classmethod
    def poll(cls, context):
        return bpy.context.scene is not None

    def execute(self, context):

        if self.direction == "OUT":
            bpy.ops.view2d.zoom(deltay=-1)
        else:
            bpy.ops.view2d.zoom(deltay=1)
        return {"FINISHED"}


class SEQUENCER_OT_move(bpy.types.Operator):
    """Move selection"""

    bl_idname = "sequencer.move"
    bl_label = "Move"
    bl_options = {"REGISTER", "UNDO"}

    direction: EnumProperty(
        name="Direction",
        description="Move",
        items=(
            ("UP", "Up", "Move Selection Up"),
            ("DOWN", "Down", "Move Selection Down"),
            ("LEFT", "Left", "Move Selection Left"),
            ("RIGHT", "Right", "Move Selection Right"),
        ),
    )

    @classmethod
    def poll(cls, context):
        return bpy.context.scene is not None

    def execute(self, context):

        selection = context.selected_sequences
        selection = sorted(selection, key=attrgetter("channel", "frame_final_start"))

        if self.direction == "UP":
            selection.reverse()
        if not selection:
            return {"CANCELLED"}
        for s in selection:
            if not s.lock and s.type not in {
                "CROSS",
                "ADD",
                "SUBTRACT",
                "ALPHA_OVER",
                "ALPHA_UNDER",
                "GAMMA_CROSS",
                "MULTIPLY",
                "OVER_DROP",
                "WIPE",
                "GLOW",
                "TRANSFORM",
                "SPEED",
                "GAUSSIAN_BLUR",
                "COLORMIX",
            }:
                current_start = s.frame_final_start
                current_channel = s.channel
                bpy.ops.sequencer.select_all(action="DESELECT")
                s.select = True
                context.scene.sequence_editor.active_strip = s
                if self.direction == "UP":
                    if s.channel < 32:
                        s.channel += 1
                elif self.direction == "DOWN":
                    if s.channel > 1:
                        s.channel -= 1
                elif self.direction == "LEFT":
                    bpy.ops.transform.seq_slide(value=(-25, 0))
                    if s.frame_final_start == current_start:
                        bpy.ops.sequencer.swap(side="LEFT")
                elif self.direction == "RIGHT":
                    bpy.ops.transform.seq_slide(value=(25, 0))
                    if s.frame_final_start == current_start:
                        bpy.ops.sequencer.swap(side="RIGHT")
                s.select = False
        for s in selection:
            s.select = True

        return {"FINISHED"}


class SEQUENCER_OT_match_frame(bpy.types.Operator):
    """Add full source to empty channel and match frame"""

    bl_idname = "sequencer.match_frame"
    bl_label = "Match Frame"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bpy.context.scene is not None

    def execute(self, context):

        selection = context.selected_sequences
        selection = sorted(selection, key=attrgetter("channel", "frame_final_start"))

        if not selection:
            return {"CANCELLED"}
        for seq in selection:

            if seq.type not in {
                "CROSS",
                "ADD",
                "SUBTRACT",
                "ALPHA_OVER",
                "ALPHA_UNDER",
                "GAMMA_CROSS",
                "MULTIPLY",
                "OVER_DROP",
                "WIPE",
                "GLOW",
                "TRANSFORM",
                "SPEED",
                "GAUSSIAN_BLUR",
                "COLORMIX",
            }:

                # Find empty channel:
                sequences = bpy.context.sequences
                if not sequences:
                    return 1
                channels = [s.channel for s in sequences]
                channels = sorted(list(set(channels)))
                empty_channel = channels[-1] + 1

                # Duplicate strip to first empty channel and clear offsets
                if empty_channel < 33:
                    bpy.ops.sequencer.select_all(action="DESELECT")
                    seq.select = True
                    context.scene.sequence_editor.active_strip = (
                        seq  # set as active or it won't work
                    )
                    bpy.ops.sequencer.duplicate_move(
                        SEQUENCER_OT_duplicate={"mode": "TRANSLATION"},
                        TRANSFORM_OT_seq_slide={
                            "value": (0, empty_channel - seq.channel),
                            "snap": False,
                            "snap_target": "CLOSEST",
                            "snap_point": (0, 0, 0),
                            "snap_align": False,
                            "snap_normal": (0, 0, 0),
                            "release_confirm": False,
                            "use_accurate": False,
                        },
                    )
                    bpy.ops.sequencer.offset_clear()
        # re-select previous selection
        for seq in selection:
            seq.select = True
        return {"FINISHED"}


class SEQUENCER_OT_split(bpy.types.Operator):
    """Split Unlocked Un/Seleted Strips Soft"""

    bl_idname = "sequencer.split"
    bl_label = "Split Soft"
    bl_options = {"REGISTER", "UNDO"}

    type: EnumProperty(
        name="Type",
        description="Split Type",
        items=(
            ("SOFT", "Soft", "Split Soft"),
            ("HARD", "Hard", "Split Hard"),
        ),
    )

    @classmethod
    def poll(cls, context):
        if context.sequences:
            return True
        return False

    def execute(self, context):
        selection = context.selected_sequences
        sequences = bpy.context.scene.sequence_editor.sequences_all
        cf = bpy.context.scene.frame_current
        at_cursor = []
        cut_selected = False

        # find unlocked strips at cursor
        for s in sequences:
            if s.frame_final_start <= cf and s.frame_final_end > cf:
                if s.lock == False:
                    at_cursor.append(s)
                    if s.select == True:
                        cut_selected = True
        for s in at_cursor:
            if cut_selected:
                if s.select:  # only cut selected
                    bpy.ops.sequencer.select_all(action="DESELECT")
                    s.select = True
                    bpy.ops.sequencer.cut(
                        frame=bpy.context.scene.frame_current,
                        type=self.type,
                        side="RIGHT",
                    )

                    # add new strip to selection
                    for i in bpy.context.scene.sequence_editor.sequences_all:
                        if i.select:
                            selection.append(i)
                    bpy.ops.sequencer.select_all(action="DESELECT")
                    for s in selection:
                        s.select = True
            else:  # cut unselected
                bpy.ops.sequencer.select_all(action="DESELECT")
                s.select = True
                bpy.ops.sequencer.cut(
                    frame=bpy.context.scene.frame_current, type=self.type
                )
                bpy.ops.sequencer.select_all(action="DESELECT")
                for s in selection:
                    s.select = True
        return {"FINISHED"}


class SEQUENCER_OT_extend_to_fill(bpy.types.Operator):
    """Extend to fill gaps after selected strips"""

    bl_idname = "sequencer.extend_to_fill"
    bl_label = "Extend to Fill"
    bl_description = "Extend selected strips forward to fill adjacent space"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        current_scene = context.scene
        if current_scene and current_scene.sequence_editor:
            return True
        else:
            return False

    def execute(self, context):
        current_scene = context.scene
        current_sequence = current_scene.sequence_editor
        selection = context.selected_sequences
        meta_level = len(current_sequence.meta_stack)

        if meta_level > 0:
            current_sequence = current_sequence.meta_stack[meta_level - 1]
        if not selection:
            return {"CANCELLED"}
        error = False
        for strip in selection:
            if strip.lock == False and strip.type not in {
                "CROSS",
                "ADD",
                "SUBTRACT",
                "ALPHA_OVER",
                "ALPHA_UNDER",
                "GAMMA_CROSS",
                "MULTIPLY",
                "OVER_DROP",
                "WIPE",
                "GLOW",
                "TRANSFORM",
                "SPEED",
                "GAUSSIAN_BLUR",
                "COLORMIX",
            }:

                current_channel = strip.channel
                current_end = strip.frame_final_end
                new_end = 300000

                for i in current_sequence.sequences:
                    next_start = i.frame_final_start
                    if i.channel == current_channel and next_start + 1 > current_end:
                        if next_start < new_end:
                            new_end = next_start
                if new_end == 300000 and current_end < current_scene.frame_end:
                    new_end = current_scene.frame_end
                if new_end == 300000 or new_end == current_end:
                    error = True
                else:
                    error = False
                    strip.frame_final_end = new_end
        if error:
            return {"CANCELLED"}
        return {"FINISHED"}


class SEQUENCER_OT_concatenate(bpy.types.Operator):
    """Concatenate gaps after selected strips"""

    bl_idname = "sequencer.concatenate"
    bl_label = "Concatenate"
    bl_description = "Concatenate space after selected strips"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        current_scene = context.scene
        if current_scene and current_scene.sequence_editor:
            return True
        else:
            return False

    def execute(self, context):
        current_scene = context.scene
        current_sequence = current_scene.sequence_editor
        selection = context.selected_sequences
        meta_level = len(current_sequence.meta_stack)

        if meta_level > 0:
            current_sequence = current_sequence.meta_stack[meta_level - 1]
        if not selection:
            return {"CANCELLED"}
        error = False
        for strip in selection:
            if strip.lock == False and strip.type not in {
                "CROSS",
                "ADD",
                "SUBTRACT",
                "ALPHA_OVER",
                "ALPHA_UNDER",
                "GAMMA_CROSS",
                "MULTIPLY",
                "OVER_DROP",
                "WIPE",
                "GLOW",
                "TRANSFORM",
                "SPEED",
                "GAUSSIAN_BLUR",
                "COLORMIX",
            }:

                current_channel = strip.channel
                current_end = strip.frame_final_end
                new_end = 300000

                for i in current_sequence.sequences:
                    next_start = i.frame_final_start
                    if i.channel == current_channel and next_start - 1 > current_end:
                        if next_start < new_end:
                            new_end = next_start
                if new_end == 300000 and current_end < current_scene.frame_end:
                    new_end = current_scene.frame_end
                if new_end == 300000 or new_end == current_end:
                    error = True
                else:
                    # Add color strips in gaps and use ripple delete to extract them
                    error = False
                    bpy.ops.sequencer.select_all(action="DESELECT")
                    bpy.ops.sequencer.effect_strip_add(
                        frame_start=current_end + 1,
                        frame_end=new_end,
                        channel=current_channel,
                        type="COLOR",
                    )
                    bpy.ops.sequencer.ripple_delete()
        bpy.ops.sequencer.select_all(action="DESELECT")
        for s in selection:
            s.select = True

        if error:
            return {"CANCELLED"}
        return {"FINISHED"}


class SEQUENCER_OT_split_mode(bpy.types.Operator):
    """Split either selected or all unselected strips at current frame with preview"""

    bl_idname = "sequencer.split_mode"
    bl_label = "Split Mode..."

    @classmethod
    def poll(cls, context):
        current_scene = context.scene
        if current_scene and current_scene.sequence_editor:
            return True
        else:
            return False

    def execute(self, context):
        region = context.region
        x, y = region.view2d.region_to_view(*self.mouse_path[-1])
        context.scene.frame_set(x)

    def modal(self, context, event):
        context.area.tag_redraw()
        region = context.region

        if event.type == "MOUSEMOVE":
            self.mouse_path.append((event.mouse_region_x, event.mouse_region_y))
            self.execute(context)
        elif event.type == "LEFTMOUSE" and event.value == "PRESS":

            bpy.ops.sequencer.split(type="SOFT")
        elif event.type in {"RIGHTMOUSE", "ESC"}:

            return {"FINISHED"}
        return {"RUNNING_MODAL"}

    def invoke(self, context, event):

        args = (self, context)
        self.mouse_path = []
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


classes = (
    SEQUENCER_OT_crossfade_sounds,
    SEQUENCER_OT_cut_multicam,
    SEQUENCER_OT_deinterlace_selected_movies,
    SEQUENCER_OT_reverse_selected_movies,
    SEQUENCER_OT_flip_x_selected_movies,
    SEQUENCER_OT_flip_y_selected_movies,
    SEQUENCER_OT_show_waveform_selected_sounds,
    SEQUENCER_OT_select_current_frame,
    SEQUENCER_OT_select_channel_strips,
    SEQUENCER_OT_select_locked_strips,
    SEQUENCER_OT_select_mute_strips,
    SEQUENCER_OT_audio_mute_toggle,
    SEQUENCER_OT_set_preview_range,
    SEQUENCER_OT_preview_selected,
    SEQUENCER_OT_split_remove,
    SEQUENCER_OT_delete_lift,
    SEQUENCER_OT_ripple_delete,
    SEQUENCER_OT_zoom_vertical,
    SEQUENCER_OT_match_frame,
    SEQUENCER_OT_split,
    SEQUENCER_OT_extend_to_fill,
    SEQUENCER_OT_move,
    SEQUENCER_OT_concatenate,
    SEQUENCER_OT_split_mode,
)
