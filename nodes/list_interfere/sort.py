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
from bpy.props import BoolProperty, IntProperty, StringProperty

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import (updateNode, changable_sockets,
                            dataCorrect, svQsort,
                            SvSetSocketAnyType, SvGetSocketAnyType)


class ListSortNode(bpy.types.Node, SverchCustomTreeNode):
    ''' List Sort '''
    bl_idname = 'ListSortNode'
    bl_label = 'List Sort'
    bl_icon = 'OUTLINER_OB_EMPTY'

    level = IntProperty(name='level_to_count',
                        default=2, min=0,
                        update=updateNode)
    typ = StringProperty(name='typ',
                         default='')
    newsock = BoolProperty(name='newsock',
                           default=False)

    def draw_buttons(self, context, layout):
        layout.prop(self, "level", text="level")

    def sv_init(self, context):
        self.inputs.new('StringsSocket', "data", "data")
        self.outputs.new('StringsSocket', "data", "data")

    def update(self):
        if 'data' in self.inputs and len(self.inputs['data'].links) > 0:
            # адаптивный сокет
            inputsocketname = 'data'
            outputsocketname = ['data']
            changable_sockets(self, inputsocketname, outputsocketname)

    def process(self):
        # достаём два слота - вершины и полики
        if 'data' in self.outputs and len(self.outputs['data'].links) > 0 \
                and 'data' in self.inputs and len(self.inputs['data'].links) > 0:
            data_ = SvGetSocketAnyType(self, self.inputs['data'])

            # init_level = levelsOflist(data)
            data = dataCorrect(data_, nominal_dept=self.level)
            out_ = []
            for obj in data:
                out_.append(svQsort(obj))
            out = dataCorrect(out_)
            SvSetSocketAnyType(self, 'data', out)



