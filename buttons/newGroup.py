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
import time
from ..functions import *
props = bpy.props

class newGroupFromSelection(bpy.types.Operator):
    """Create new group containing selected objects, and set as group to assemble""" # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.new_group_from_selection"                                # unique identifier for buttons and menu items to reference.
    bl_label = "New Group"                                                      # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}                                           # enable undo for the operator.

    ################################################
    # Blender Operator methods

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = bpy.context.scene
        if scn.aglist_index == -1:
            return False
        return True

    def execute(self, context):
        if not self.canRun():
            return{"CANCELLED"}
        try:
            scn, ag = getActiveContextInfo()
            # create new animated group
            newGroupName = "AssemblMe_{}_group".format(ag.name)
            overwriteGroup = bpy.data.groups.get(newGroupName)
            if overwriteGroup is not None:
                bpy.data.groups.remove(overwriteGroup)
            ag.group = bpy.data.groups.new(newGroupName)
            # add selected objects to new group
            for obj in self.objs_to_move:
                ag.group.objects.link(obj)
        except:
            assemblme_handle_exception()

        return{"FINISHED"}

    ################################################
    # initialization method

    def __init__(self):
        scn, ag = getActiveContextInfo()
        self.objs_to_move = [obj for obj in bpy.context.selected_objects if not ag.meshOnly or obj.type == "MESH"]

    ################################################
    # class method

    def canRun(self):
        if len(self.objs_to_move) == 0:
            self.report({"WARNING"}, "No objects selected")
            return False
        return True

    #############################################
