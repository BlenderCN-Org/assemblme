# Copyright (C) 2018 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# system imports
import bpy
import os
from bpy.props import *
from ..ui import *
from ..buttons import *
from bpy.types import AddonPreferences

# updater import
from .. import addon_updater_ops

class ASSEMBLME_PT_preferences(AddonPreferences):
    # bl_idname = __name__
    bl_idname = __package__[:__package__.index(".lib")]

    # file path to assemblMe presets (non-user-editable)
    addonLibPath = os.path.dirname(os.path.abspath(__file__))
    defaultPresetsFP = os.path.abspath(os.path.join(addonLibPath, '..', '..', '..', 'presets', 'assemblme'))
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

	# addon updater preferences
    auto_check_update = BoolProperty(
        name = "Auto-check for Update",
        description = "If enabled, auto-check for updates using an interval",
        default = False)
    updater_intrval_months = IntProperty(
        name='Months',
        description = "Number of months between checking for updates",
        default=0, min=0)
    updater_intrval_days = IntProperty(
        name='Days',
        description = "Number of days between checking for updates",
        default=7, min=0)
    updater_intrval_hours = IntProperty(
        name='Hours',
        description = "Number of hours between checking for updates",
        min=0, max=23,
        default=0)
    updater_intrval_minutes = IntProperty(
        name='Minutes',
        description = "Number of minutes between checking for updates",
        min=0, max=59,
        default=0)


    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Auto-Save:")
        row = col.row(align=True)
        row.prop(self, "autoSaveOnCreateAnim")
        row = col.row(align=True)
        row.prop(self, "autoSaveOnStartOver")

        # updater draw function
        addon_updater_ops.update_settings_ui(self,context)
