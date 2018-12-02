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

# System imports
# NONE!

# Blender imports
import bpy
from bpy.props import *
from bpy.types import Panel, UIList
props = bpy.props

# Addon imports
from ..functions import *
from ..buttons.visualizer import *

# ui list item actions
class ASSEMBLME_OT_uilist_actions(bpy.types.Operator):
    bl_idname = "aglist.list_action"
    bl_label = "List Action"

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
        )
    )

    # @classmethod
    # def poll(cls, context):
    #     """ ensures operator can execute (if not, returns false) """
    #     scn = context.scene
    #     for ag in scn.aglist:
    #         if ag.animated:
    #             return False
    #     return True

    def invoke(self, context, event):

        scn = context.scene
        idx = scn.aglist_index

        try:
            item = scn.aglist[idx]
        except IndexError:
            pass

        if self.action == 'REMOVE':
            ag = scn.aglist[scn.aglist_index]
            if not ag.animated:
                if visualizer.enabled():
                    visualizer.disable()
                curGroup = bpy.data.groups.get(ag.group_name)
                if curGroup is not None:
                    bpy.data.groups.remove(curGroup, True)
                    bpy.context.area.tag_redraw()
                if len(scn.aglist) - 1 == scn.aglist_index:
                    scn.aglist_index -= 1
                scn.aglist.remove(idx)
                if scn.aglist_index == -1 and len(scn.aglist) > 0:
                    scn.aglist_index = 0
            else:
                self.report({"WARNING"}, "Please press 'Start Over' to clear the animation before removing this item.")

        if self.action == 'ADD':
            if visualizer.enabled():
                visualizer.disable()
            item = scn.aglist.add()
            last_index = scn.aglist_index
            scn.aglist_index = len(scn.aglist)-1
            item.name = "<New Animation>"
            # get all existing IDs
            existingIDs = []
            for ag in scn.aglist:
                existingIDs.append(ag.id)
            i = max(existingIDs) + 1
            # protect against massive item IDs
            if i > 9999:
                i = 1
                while i in existingIDs:
                    i += 1
            # set item ID to unique number
            item.id = i
            item.idx = len(scn.aglist)-1

        elif self.action == 'DOWN' and idx < len(scn.aglist) - 1:
            scn.aglist.move(scn.aglist_index, scn.aglist_index+1)
            scn.aglist_index += 1
            item.idx = scn.aglist_index

        elif self.action == 'UP' and idx >= 1:
            scn.aglist.move(scn.aglist_index, scn.aglist_index-1)
            scn.aglist_index -= 1
            item.idx = scn.aglist_index

        return {"FINISHED"}

# -------------------------------------------------------------------
# draw
# -------------------------------------------------------------------

class ASSEMBLME_UL_uilist_items(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # Make sure your code supports all 3 layout types
        if self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
        split = layout.split(0.9)
        split.prop(item, "name", text="", emboss=False, translate=False, icon='MOD_BUILD')

    def invoke(self, context, event):
        pass


# copy settings from current index to all other indices
class ASSEMBLME_OT_uilist_copySettingsToOthers(bpy.types.Operator):
    bl_idname = "aglist.copy_to_others"
    bl_label = "Copy Settings to Other Animations"
    bl_description = "Copies the settings from the current animation to all other animations"

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = context.scene
        if scn.aglist_index == -1:
            return False
        if len(scn.aglist) == 1:
            return False
        return True

    def execute(self, context):
        scn = context.scene
        ag0 = scn.aglist[scn.aglist_index]
        for ag1 in scn.aglist:
            if ag0 != ag1:
                matchProperties(ag1, ag0)
        return{'FINISHED'}


# copy settings from current index to memory
class ASSEMBLME_OT_uilist_copySettings(bpy.types.Operator):
    bl_idname = "aglist.copy_settings"
    bl_label = "Copy Settings from Current Animation"
    bl_description = "Stores the ID of the current animation for pasting"

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = context.scene
        if scn.aglist_index == -1:
            return False
        return True

    def execute(self, context):
        scn, ag = getActiveContextInfo()
        scn.assemblme_copy_from_id = ag.id
        return{'FINISHED'}


# paste settings from index in memory to current index
class ASSEMBLME_OT_uilist_pasteSettings(bpy.types.Operator):
    bl_idname = "aglist.paste_settings"
    bl_label = "Paste Settings to Current animation"
    bl_description = "Pastes the settings from stored animation ID to the current index"

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = context.scene
        if scn.aglist_index == -1:
            return False
        return True

    def execute(self, context):
        scn = context.scene
        ag0 = scn.aglist[scn.aglist_index]
        for ag1 in scn.aglist:
            if ag0 != ag1 and ag1.id == scn.assemblme_copy_from_id:
                matchProperties(ag0, ag1)
                break
        return{'FINISHED'}


# print button
class ASSEMBLME_OT_uilist_printAllItems(bpy.types.Operator):
    bl_idname = "aglist.print_list"
    bl_label = "Print List"
    bl_description = "Print all items to the console"

    def execute(self, context):
        scn = context.scene
        for i in scn.aglist:
            print (i.source_name, i.id)
        return{'FINISHED'}


# set source to active button
class ASSEMBLME_OT_uilist_setSourceGroupToActive(bpy.types.Operator):
    bl_idname = "aglist.set_to_active"
    bl_label = "Set to Active"
    bl_description = "Set group name to next group in active object"

    @classmethod
    def poll(cls, context):
        """ ensures operator can execute (if not, returns false) """
        scn = context.scene
        if scn.aglist_index == -1:
            return False
        if context.scene.objects.active == None:
            return False
        return True

    def execute(self, context):
        scn, ag = getActiveContextInfo()
        active_object = context.scene.objects.active
        if len(active_object.users_group) == 0:
            self.report({"INFO"}, "Active object has no linked groups.")
            return {"CANCELLED"}
        if ag.lastActiveObjectName == active_object.name:
            ag.activeGroupIndex = (ag.activeGroupIndex + 1) % len(active_object.users_group)
        else:
            ag.lastActiveObjectName = active_object.name
            ag.activeGroupIndex = 0
        ag.group_name = active_object.users_group[ag.activeGroupIndex].name

        return{'FINISHED'}


# clear button
class ASSEMBLME_OT_uilist_clearAllItems(bpy.types.Operator):
    bl_idname = "aglist.clear_list"
    bl_label = "Clear List"
    bl_description = "Clear all items in the list"

    def execute(self, context):
        scn = context.scene
        lst = scn.animatedGroupsCollection
        current_index = scn.aglist_index

        if len(lst) > 0:
             # reverse range to remove last item first
            for i in range(len(lst)-1,-1,-1):
                scn.animatedGroupsCollection.remove(i)
            self.report({'INFO'}, "All items removed")

        else:
            self.report({'INFO'}, "Nothing to remove")

        return{'FINISHED'}
