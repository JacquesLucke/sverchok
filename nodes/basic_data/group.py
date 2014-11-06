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

import bpy
from bpy.props import StringProperty, EnumProperty

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import multi_socket, node_id
from sverchok.core.update_system import make_tree_from_nodes, do_update
import ast


class StoreSockets:
    
    socket_data = StringProperty()


    def draw_buttons(self, context, layout):
        if self.id_data.bl_idname == "SverchCustomTreeType" and self.parent:
            op = layout.operator("node.sv_node_group_done")
            op.frame_name = self.parent.name
            col = layout.column(align=True)
            for s in next(self.get_sockets())[0]:
                layout.prop(s, "name")
        
    def collect(self):
        out = {}
        for sockets, name in self.get_sockets():
            data = [(s.bl_idname, s.name) for s in sockets if s.is_linked]
            out[name] = data
        self.socket_data = str(out)
            
    def load(self):
        data = ast.literal_eval(self.socket_data)
        for k,values in data.items():
            sockets = getattr(self, k)
            sockets.clear()
            for s in values:
                if not s[1] in sockets:
                    sockets.new(*s)
    
    def get_stype(self, socket):
        if socket.is_output:
            return socket.links[0].to_node.bl_idname
        else:
            return socket.links[0].from_node.bl_idname
        
    def update(self):
        if self.id_data.bl_idname == "SverchCustomTreeType":
            sockets, name = next(self.get_sockets())
            if self.socket_data and sockets[-1].links:
                sockets.new("StringsSocket", str(len(sockets)))
                
    s_types = (("StringsSocket","StringsSocket", "Generic number socket"),
              ("VerticesSocket", "VerticesSocket", "Vertex data"),
              ("MatrixSocket", "MatrixSocket", "Matrix data"))
            
    s_type = EnumProperty(items=s_types)
    
class SvGroupNode(bpy.types.Node, SverchCustomTreeNode, StoreSockets):
    '''
    Sverchok Group node
    '''
    bl_idname = 'SvGroupNode'
    bl_label = 'Group'
    bl_icon = 'OUTLINER_OB_EMPTY'

    group_name = StringProperty()
    
    def update(self):
        '''
        Override inherited
        '''
        pass
        
    def draw_buttons(self, context, layout):
        if self.id_data.bl_idname == "SverchCustomTreeType":
            op = layout.operator("node.sv_node_group_edit")
            op.group_name = self.group_name
            
    def adjust_sockets(self, nodes):
        swap = {"inputs":"outputs",
                "outputs": "inputs"}
        for n in nodes:
            data = ast.literal_eval(n.socket_data)
            for k, values in data.items():
                sockets = getattr(self, swap[k])
                for i,s in enumerate(values):
                    if i < len(sockets):
                        sockets[i].name = s[1]
                    else:
                        sockets.new(*s)

    def process(self):
        group_ng = bpy.data.node_groups[self.group_name]
        in_node = find_node("SvGroupInputsNode", group_ng)
        out_node = find_node('SvGroupOutputsNode', group_ng)
        for socket in self.inputs:
            if socket.links:
                data = socket.sv_get(deepcopy=False)
                in_node.outputs[socket.name].sv_set(data)
        #  get update list
        #  could be cached
        ul = make_tree_from_nodes([out_node.name], group_ng, down=False)
        do_update(ul, group_ng.nodes)
        # set output sockets correctly
        for socket in self.outputs:
            if socket.links:
                data = out_node.inputs[socket.name].sv_get(deepcopy=False)
                socket.sv_set(data)
    
    def get_sockets(self):
        yield self.inputs, "inputs"
        yield self.outputs, "outputs"
    

def find_node(id_name, ng):
    for n in ng.nodes:
        if n.bl_idname == id_name:
            return n
    raise NotFoundErr
    


class SvGroupInputsNode(bpy.types.Node, SverchCustomTreeNode, StoreSockets):
    bl_idname = 'SvGroupInputsNode'
    bl_label = 'Group Inputs'
    bl_icon = 'OUTLINER_OB_EMPTY'

    def get_sockets(self):
        yield self.outputs, "outputs"
            
    
class SvGroupOutputsNode(bpy.types.Node, SverchCustomTreeNode, StoreSockets):
    bl_idname = 'SvGroupOutputsNode'
    bl_label = 'Group outputs'
    bl_icon = 'OUTLINER_OB_EMPTY'
    
    def get_sockets(self):
        yield self.inputs, "inputs"
    
    
def register():
    bpy.utils.register_class(SvGroupNode)
    bpy.utils.register_class(SvGroupInputsNode)
    bpy.utils.register_class(SvGroupOutputsNode)

def unregister():
    bpy.utils.unregister_class(SvGroupNode)
    bpy.utils.unregister_class(SvGroupInputsNode)
    bpy.utils.unregister_class(SvGroupOutputsNode)
