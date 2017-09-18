bl_info = {
    "name"        : "AssemblMe",
    "author"      : "Christopher Gearhart <chris@bblanimation.com>",
    "version"     : (1, 1, 0),
    "blender"     : (2, 78, 0),
    "description" : "Iterative object assembly animations made simple",
    "location"    : "View3D > Tools > AssemblMe",
    # "wiki_url"    : "",
    "tracker_url" : "https://github.com/bblanimation/lego_add_ons/issues",
    "category"    : "Animation"}

"""
Copyright (C) 2017 Bricks Brought to Life
http://bblanimation.com/
chris@bblanimation.com

Created by Christopher Gearhart

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# system imports
import bpy
import os
from bpy.props import *
from .ui import *
from .buttons import *
from .buttons.presets import animPresets
from bpy.types import Operator, AddonPreferences
props = bpy.props

class AssemblMePreferences(AddonPreferences):
    bl_idname = __name__

    # file path to assemblMe presets (non-user-editable)
    addonPath = os.path.dirname(os.path.abspath(__file__))
    defaultPresetsFP = os.path.join(addonPath, "lib", "presets")
    presetsFilepath = StringProperty(
            name="Path to assemblMe presets",
            subtype='FILE_PATH',
            default=defaultPresetsFP)

    # auto save preferences
    autoSaveOnCreateAnim = BoolProperty(
            name="Before 'Create Build Animation'",
            description="Save backup .blend file to project directory before executing 'Create Build Animation' actions",
            default=False)
    autoSaveOnStartOver = BoolProperty(
            name="Before 'Start Over'",
            description="Save backup .blend file to project directory before executing 'Start Over' actions",
            default=False)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Auto-Save:")
        row = col.row(align=True)
        row.prop(self, "autoSaveOnCreateAnim")
        row = col.row(align=True)
        row.prop(self, "autoSaveOnStartOver")

# class OBJECT_OT_addon_prefs_example(Operator):
#     """Display example preferences"""
#     bl_idname = "object.addon_prefs_example"
#     bl_label = "Addon Preferences Example"
#     bl_options = {'REGISTER', 'UNDO'}
#
#     def execute(self, context):
#         user_preferences = context.user_preferences
#         addon_prefs = user_preferences.addons[__name__].preferences
#
#         info = ("Path: %s, Number: %d, Boolean %r" %
#                 (addon_prefs.filepath, addon_prefs.number, addon_prefs.boolean))
#
#         self.report({'INFO'}, info)
#         print(info)
#
#         return {'FINISHED'}

def register():
    # bpy.utils.register_class(OBJECT_OT_addon_prefs_example)
    bpy.utils.register_class(AssemblMePreferences)
    user_preferences = bpy.context.user_preferences
    props.addon_prefs = user_preferences.addons[__name__].preferences
    bpy.utils.register_module(__name__)
    bpy.props.assemblme_module_name = __name__

    props.addonVersion = "1.1.0"

    bpy.types.Scene.assemblme_copy_from_id = IntProperty(default=-1)

    # items used by selection app handler
    bpy.types.Scene.assemblMe_runningOperation = BoolProperty(default=False)
    bpy.types.Scene.assemblMe_last_layers = StringProperty(default="")
    bpy.types.Scene.assemblMe_last_aglist_index = IntProperty(default=-2)
    bpy.types.Scene.assemblMe_active_object_name = StringProperty(default="")
    bpy.types.Scene.assemblMe_last_active_object_name = StringProperty(default="")

    bpy.types.Scene.skipEmptySelections = BoolProperty(
        name="Skip Empty Selections",
        description="Skip frames where nothing is selected if checked",
        default=True)

    bpy.types.Scene.newPresetName = StringProperty(
        name="Name of New Preset",
        description="Full name of new custom preset",
        default="")
    presetNames = animPresets.getPresetTuples()
    bpy.types.Scene.animPreset = EnumProperty(
        name="Presets",
        description="Stored AssemblMe presets",
        items=presetNames,
        update=updateAnimPreset,
        default="None")
    bpy.types.Scene.animPresetToDelete = EnumProperty(
        name="Preset to Delete",
        description="Another list of stored AssemblMe presets",
        items=bpy.types.Scene.animPreset[1]['items'],
        default="None")

    bpy.types.Scene.visualizerScale = FloatProperty(
        name="Scale",
        description="Scale of layer orientation visualizer",
        precision=1,
        min=0.1, max=100,
        default=10)
    bpy.types.Scene.visualizerNumCuts = FloatProperty(
        name="Num Cuts",
        description="Scale of layer orientation visualizer",
        precision=0,
        min=2, max=64,
        default=50)

    # list properties
    bpy.types.Scene.aglist = CollectionProperty(type=AssemblMe_AnimatedGroups)
    bpy.types.Scene.aglist_index = IntProperty(default=-1)

    # Session properties
    props.z_upper_bound = None
    props.z_lower_bound = None
    props.ignoredTypes = ["CAMERA", "LAMP", "POINT", "PLAIN_AXES", "EMPTY"]
    props.objMinLoc = 0
    props.objMaxLoc = 0

def unregister():
    Scn = bpy.types.Scene

    del Scn.aglist_index
    del Scn.aglist

    del Scn.visualizerNumCuts
    del Scn.visualizerScale

    del Scn.animPresetToDelete
    del Scn.animPreset
    del Scn.newPresetName

    del Scn.skipEmptySelections

    del Scn.assemblMe_last_active_object_name
    del Scn.assemblMe_active_object_name
    del Scn.assemblMe_last_aglist_index
    del Scn.assemblMe_last_layers
    del Scn.assemblMe_runningOperation

    del Scn.assemblme_copy_from_id

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
