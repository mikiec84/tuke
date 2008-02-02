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
from Tuke import Element

class ElementTest(TestCase):
    """Perform tests of the element module"""

    def testElementInterator(self):
        """Element interation"""

        a = Element()

        j = set((Element(),Element(),Element()))

        for i in j:
            a.add(i)

        self.assert_(set(a.subs) == j)