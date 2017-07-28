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
import math
import bmesh
from ..functions import *
props = bpy.props

class visualizer(bpy.types.Operator):
    """Visualize the layer orientation with a plane"""                          # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "scene.visualize_layer_orientation"                             # unique identifier for buttons and menu items to reference.
    bl_label = "Visualize Layer Orientation"                                    # display name in the interface.
    bl_options = {"REGISTER", "UNDO"}

    def __init__(self):
        """ sets up self.visualizerObj """
        if groupExists("AssemblMe_visualizer"):
            # set self.visualizer and self.m with existing data
            self.visualizerObj = bpy.data.groups["AssemblMe_visualizer"].objects[0]
            self.m = self.visualizerObj.data
        else:
            # create visualizer object
            self.m = bpy.data.meshes.new('AssemblMe_visualizer_m')
            self.visualizerObj = bpy.data.objects.new('assemblMe_visualizer', self.m)
            self.visualizerObj.hide_select = True
            self.visualizerObj.hide_render = True
            # put in new group
            vGroup = bpy.data.groups.new("AssemblMe_visualizer")
            vGroup.objects.link(self.visualizerObj)
        # not sure what this does, to be honest
        visualizer.instance = self

    def createAnim(self):
        scn = bpy.context.scene
        ag = scn.aglist[scn.aglist_index]
        # if first and last location are the same, keep visualizer stationary
        if props.objMinLoc == props.objMaxLoc or ag.orientRandom > 0.0025:
            self.visualizerObj.animation_data_clear()
            if type(props.objMinLoc) == type(self.visualizerObj.location):
                self.visualizerObj.location = props.objMinLoc
            else:
                self.visualizerObj.location = (0,0,0)
            ag.visualizerAnimated = False
            return "static"
        # else, create animation
        else:
            # if animation already created, clear it
            if ag.visualizerAnimated:
                self.visualizerObj.animation_data_clear()
            # set up vars
            self.visualizerObj.location = props.objMinLoc
            curFrame = ag.frameWithOrigLoc
            idx = -1
            # insert keyframe and iterate current frame, and set another
            insertKeyframes(self.visualizerObj, "location", curFrame, 'LINEAR', idx)
            self.visualizerObj.location = props.objMaxLoc
            if ag.buildType == "Assemble":
                curFrame -= (ag.animLength - ag.lastLayerVelocity)
                idx -= 1
            else:
                curFrame += (ag.animLength - ag.lastLayerVelocity)
            insertKeyframes(self.visualizerObj, "location", curFrame, 'LINEAR', idx)
            ag.visualizerAnimated = True
            return "animated"

    def loadLatticeMesh(self, context):
        scn = bpy.context.scene
        visualizerBM = makeSimple2DLattice(scn.visualizerNumCuts, scn.visualizerScale)
        self.visualizerNumCuts = scn.visualizerNumCuts
        self.visualizerScale = scn.visualizerScale
        visualizerBM.to_mesh(self.visualizerObj.data)

    def enable(self, context):
        """ enables visualizer """
        scn = context.scene
        ag = scn.aglist[scn.aglist_index]
        # alert user that visualizer is enabled
        self.report({"INFO"}, "Visualizer enabled... ('ESC' to disable)")
        # add proper mesh data to visualizer object
        self.loadLatticeMesh(context)
        # link visualizer object to scene
        scn.objects.link(self.visualizerObj)
        unhide(self.visualizerObj)
        ag.visualizerLinked = True

    def disable(self, context):
        """ disables visualizer """
        scn = bpy.context.scene
        ag = scn.aglist[scn.aglist_index]
        # alert user that visualizer is disabled
        self.report({"INFO"}, "Visualizer disabled")
        # unlink visualizer object to scene
        scn.objects.unlink(self.visualizerObj)
        ag.visualizerLinked = False

    @staticmethod
    def enabled():
        """ returns boolean for visualizer linked to scene """
        scn = bpy.context.scene
        ag = scn.aglist[scn.aglist_index]
        return ag.visualizerLinked

    def modal(self, context, event):
        """ runs as long as visualizer is active """
        if event.type in {"ESC"}:
            self.report({"INFO"}, "Visualizer disabled")
            self.disable(context)
            return{"CANCELLED"}

        if event.type == "TIMER":
            scn = context.scene
            ag = scn.aglist[scn.aglist_index]
            try:
                # if the visualizer is has been disabled, stop running modal
                if not self.enabled():
                    return{"CANCELLED"}
                # if new build animation created, update visualizer animation
                if self.minAndMax != [props.objMinLoc, props.objMaxLoc]:
                    self.minAndMax = [props.objMinLoc, props.objMaxLoc]
                    self.createAnim()
                # set visualizer object rotation
                if self.visualizerObj.rotation_euler.x != ag.xOrient:
                    self.visualizerObj.rotation_euler.x = ag.xOrient
                if self.visualizerObj.rotation_euler.y != ag.yOrient:
                    self.visualizerObj.rotation_euler.y = ag.yOrient
                if self.visualizerObj.rotation_euler.z != self.zOrient:
                    self.visualizerObj.rotation_euler.z = ag.xOrient * (cos(ag.yOrient) * sin(ag.yOrient))
                    self.zOrient = self.visualizerObj.rotation_euler.z
                if scn.visualizerScale != self.visualizerScale or scn.visualizerNumCuts != self.visualizerNumCuts:
                    self.loadLatticeMesh(context)
            except:
                self.handle_exception()

        return{"PASS_THROUGH"}

    def execute(self, context):
        try:
            scn = bpy.context.scene
            ag = scn.aglist[scn.aglist_index]
            # if enabled, all we do is disable it
            if self.enabled():
                self.disable(context)
                return{"FINISHED"}
            else:
                # create animation for visualizer if build animation exists
                self.minAndMax = [props.objMinLoc, props.objMaxLoc]
                if groupExists(ag.group_name):
                    self.createAnim()
                # enable visualizer
                self.enable(context)
                # initialize self.zOrient for modal
                self.zOrient = None
                # create timer for modal
                wm = context.window_manager
                self._timer = wm.event_timer_add(.02, context.window)
                wm.modal_handler_add(self)
        except:
            self.handle_exception()

        return{"RUNNING_MODAL"}

    def handle_exception(self):
        errormsg = print_exception('AssemblMe_log')
        # if max number of exceptions occur within threshold of time, abort!
        curtime = time.time()
        print('\n'*5)
        print('-'*100)
        print("Something went wrong. Please start an error report with us so we can fix it! (press the 'Report a Bug' button under the 'Advanced' dropdown menu of AssemblMe)")
        print('-'*100)
        print('\n'*5)
        showErrorMessage("Something went wrong. Please start an error report with us so we can fix it! (press the 'Report a Bug' button under the 'Advanced' dropdown menu of AssemblMe)", wrap=240)

    def cancel(self, context):
        # remove timer
        context.window_manager.event_timer_remove(self._timer)
        # delete visualizer object and mesh
        bpy.data.objects.remove(self.visualizerObj, True)
        bpy.data.meshes.remove(self.m, True)
        # remove visualizer group
        if groupExists("AssemblMe_visualizer"):
            vGroup = bpy.data.groups["AssemblMe_visualizer"]
            bpy.data.groups.remove(vGroup, True)
