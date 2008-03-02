# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2008 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

from unittest import TestCase
import Tuke
from Tuke.geometry import V 

from numpy import matrix

class VTest(TestCase):
    """Perform tests of the v module"""

    def testV(self):
        """V class"""

        def T(x):
            self.assert_(x)

        v = V(5,6.6)
        T((v == V(5,6.6)).all())

        T((v + v == V(10,13.2)).all())

    def testVrepr(self):
        """repr(V)"""

        def T(v):
            v2 = eval(repr(v))
            self.assert_(isinstance(v2,V))
            self.assert_((v == v2).all())

        T(V(0,0))
        T(V(1,2))
        T(V(1.0,2))
        T(V(1.1,2))

    def testVslice(self):
        """V[] reprs to matrix"""

        v = V(5,6)

        vs = v[0:,0]

        self.assert_(repr(vs) == 'matrix([[ 5.]])') 