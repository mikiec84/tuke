# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# ### BOILERPLATE ###
# Tuke - Electrical Design Automation toolset
# Copyright (C) 2008 Peter Todd <pete@petertodd.org>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ### BOILERPLATE ###

from Tuke import ReprableByArgsElement,Id
from Tuke.geometry import Circle,Hole,Polygon,V

class Pin(ReprableByArgsElement):
    """Defines a pin

    dia - diameter of the hole
    thickness - thickness of the surrounding pad
    clearance - width of clearance from the pad
    mask - diameter of the mask, independent of other values
    square - square flag

    """

    __required__ = ('dia','thickness','clearance','mask')
    __defaults__ = {'square':False}

    def _init(self):
        self.square = bool(self.square)

        def gen_pad_shape(dia,id,layer=None):
            if self.square:
                r = dia / 2
                return Polygon(ext=(V(-r,-r),V(r,-r),V(r,r),V(-r,r)),id=id,layer=layer)
            else:
                return Circle(dia=dia,id=id,layer=layer)

        self.add(Hole(dia=self.dia,id=Id()))

        self.add(gen_pad_shape(self.dia + (self.thickness * 2),
                               id=Id('pad'),layer='top.pad'))
        self.add(gen_pad_shape(self.mask,id=Id('mask'),layer='top.mask'))
        self.add(gen_pad_shape(self.mask + (self.clearance * 2),
                               id=Id('clearance'),layer='top.clearance'))

        self.connects.add(Id('pad'))
