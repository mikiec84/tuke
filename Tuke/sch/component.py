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

from Tuke import Element,Id

from Tuke.sch.pin import Pin

class Component(Element):
    """Defines a Component.
   
    Components are representations of electrical components in a schematic.
    They are meant to be subclassed by the actual schematic symbols who will
    provide a custom rendering.

    A component has pins, which are defined by define_pins() A component can
    link() pins of itself, or sub components, together.

    Pin names must be valid python names, sutable for c.pin_name
    """
    pass
