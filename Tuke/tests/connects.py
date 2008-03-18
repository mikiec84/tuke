# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2008 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

import os
import shutil

import common

from unittest import TestCase
import Tuke
from Tuke import Element,Id,rndId,Connects

class ConnectsTest(TestCase):
    """Perform tests of the Connects module"""

    def testConnectsExplicit(self):
        """Explicit connections"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))
        def R(ex,fn):
            self.assertRaises(ex,fn)

        a = Element('a')
        T(a.connects,set())

        b = Element('b')
        R(TypeError,lambda: a.connects.add(b))

        a.add(b)
        a.add(Element('c'))

        a.connects.add(a.b)

        T(a.b in a.connects)
        T(Id('b') in a.connects)
        T('b' in a.connects)
        T(not ('c' in a.connects))
        T(not (a.c in a.connects))

        R(TypeError,lambda: b in a.connects)


    def testConnectsImplicit(self):
        """Implicit connections"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))
        def R(ex,fn):
            self.assertRaises(ex,fn)


        a = Element('a')
        a.add(Element('b'))

        T(not a.b.connects.to('..'))
        a.connects.add(a.b)

        T(a.connects.to(a.b))
        T(a.b.connects.to('..'))


    def testElementRemoveNotImplemented(self):
        """Element.remove() not yet implemented"""

        # This is a real test, if this fails, we need to make sure that
        # Connects handles the case where a Element parent is removed.
        a = Element('a')
        self.assert_(not hasattr(a,'remove'))