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
import time
from ..functions import *
props = bpy.props

class ASSEMBLME_OT_new_collection_from_selection(bpy.types.Operator):
    """Create new collection containing selected objects, and set as collection to assemble""" # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "assemblme.new_collection_from_selection"                       # unique identifier for buttons and menu items to reference.
    bl_label = "New Collection"                                                 # display name in the interface.
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
            # create new animated collection
            ag.collection_name = "AssemblMe_{}_collection".format(ag.name)
            agColl = bpy.data.collections.get(ag.collection_name)
            if agColl is not None:
                bpy.data.collections.remove(agColl)
            agColl = bpy.data.collections.new(ag.collection_name)
            # add selected objects to new collection
            for obj in self.objs_to_move:
                agColl.objects.link(obj)
            ag.collection_name = agColl.name
        except:
            handle_exception()

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
