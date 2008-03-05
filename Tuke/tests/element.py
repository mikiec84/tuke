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
from Tuke import load_Element,Element,Id,rndId

from Tuke.geometry import Geometry,V,Transformation,Translation,translate,centerof

from xml.dom.minidom import Document

class ElementTest(TestCase):
    """Perform tests of the element module"""

    def testElementIdChecks(self):
        """Element id validity checks"""

        self.assertRaises(ValueError,lambda:Element('foo/bar'))

    def testElementAddCollisions(self):
        """Element.add() attr collisions"""

        def T(got,expected = True):
            self.assert_(expected == got,'expected: %s  got: %s' % (expected,got))

        # collide with existing 
        a = Element('a')
        b1 = a.add(Element('b'))
        b2 = a.add(Element('b'))

        T(a.b,set((b1,b2)))
   
        # collide with attr
        a = Element('a')
        a.b = 10
        b1 = a.add(Element('b'))
        b2 = a.add(Element('b'))
        T(a.b,10)
        T(a['b'],set((b1,b2)))

    def testElementAddReturnsWrapped(self):
        """Element.add(obj) returns wrapped obj"""

        a = Element()

        b = Element('b')
        r = a.add(b)
        self.assert_(a.b is r)

        b = Element('b')
        r = a.add(b)
        self.assert_(r in a.b)

    def testElementAddObjChecks(self):
        """Element.add(obj) checks that obj is valid"""

        def T(ex,obj):
            self.assertRaises(ex,lambda:Element().add(obj))

        # Basic wrongness
        T(TypeError,None)
        T(TypeError,'asdf')
        T(TypeError,2)

        # Check for wrapped subelements
        T(TypeError,Element().add(Element()))

    def testElementInteration(self):
        """Element interation"""

        def T(elem,id_set):
            ids = [str(e.id) for e in elem]
            self.assert_(set(ids) == set(id_set))

        a = Element('a')
        T(a,set())

        for i in range(1,4):
            a.add(Element(str(i)))

        T(a,set(('a/1','a/2','a/3')))

    def testElement_isinstance(self):
        """Element.isinstance()"""

        def T(x):
            self.assert_(x)

        a = Element('a')
        T(a.isinstance(Element))
        a.add(Element('b'))
        T(a.b.isinstance(Element))

    def testElementbyid(self):
        """Element.byid()"""
        def T(elem,key,expected):
            got = elem.byid(key)
            self.assert_(expected == got,'expected: %s  got: %s' % (expected,got))

        def R(elem,key,ex):
            self.assertRaises(ex,lambda: elem[key])

        a = Element('a')
        R(a,Id(),KeyError)
        R(a,'foo',KeyError)
        R(a,Id('foo'),KeyError)

        b1 = a.add(Element('b'))
        T(a,'b',set((b1,)))
        R(a,'b/b',KeyError)

        b2 = a.add(Element('b'))
        T(a,'b',set((b1,b2)))
        R(a,'b/b',KeyError)

        c1 = a.add(Element('c'))
        T(a,'c',set((c1,)))

        print 'GO'
        d1 = a.b.add(Element('d'))
        print [z.id for z in a.byid('b')]
        T(a,'b',set((b1,b2)))
        T(a,'b/d',set((d1,)))

        d2 = a.b.add(Element('d'))
        T(a,'b',set((b1,b2)))
        T(a,'b/d',set((d1,d2)))


    def testElementIterlayout(self):
        """Element.iterlayout()"""

        def T(got,expected = True):
            self.assert_(expected == got,'expected: %s  got: %s' % (expected,got))

        e = Element(id='base')

        e.add(Element(id = 'chip'))
        e.chip.add(Element(id = 'pad'))
        e.chip.add(Geometry(layer = 'sch.lines',id = 'sym'))
        e.chip.pad.add(Geometry(layer = 'top.copper',id = 'pad'))

        # Check returned objects and Id auto-mangling
        T(set([elem.id for elem in e.iterlayout()]),
          set((Id('base/chip/pad/pad'), Id('base/chip/sym'))))

        # Check that transforms are working
        translate(e.chip,V(1,1))

        [T(repr(elem.transform), repr(Translation(V(1.0, 1.0))))
            for elem in e.iterlayout()]

        translate(e.chip.pad,V(2,3))

        r = {Id('base/chip/sym'):Translation(V(1.0, 1.0)),
             Id('base/chip/pad/pad'):Translation(V(3.0, 4.0))}

        for elem in e.iterlayout():
            T(repr(r[elem.id]), repr(elem.transform))

        # Check layer filtering works
        T(set([elem.id for elem in e.iterlayout(layer_mask='top.*')]),
          set((Id('base/chip/pad/pad'),)))
        T(set([elem.id for elem in e.iterlayout(layer_mask='sch.*')]),
          set((Id('base/chip/sym'),)))

    def testElementIdAttr(self):
        """Auto-magical attribute lookup from sub-element Id's"""

        a = Element(id='a')
        translate(a,V(1,1))

        foo = Element(id='foo')
        translate(foo,V(2,1))
        bar = Element(id='bar')
        translate(bar,V(1,2))

        a.add(foo)
        a.add(bar)

        self.assert_(a.foo.id == 'a/foo')
        self.assert_(repr(centerof(a.foo)) == repr(V(3,2)))
        self.assert_(a.bar.id == 'a/bar')
        self.assert_(repr(centerof(a.bar)) == repr(V(2,3)))
        self.assertRaises(AttributeError,lambda: a.foobar)

    def testElementSave(self):
        """Element.save()"""

        doc = Document()

        a = Element()

        from Tuke.geometry import Circle,Hole,Line
        from Tuke.pcb import Pin,Pad

#        a.add(Element(Id('asdf')))
#        a.add(Circle(1,'foo',id=rndId()))
#        a.add(Line((0.1,-0.1),(2,3),0.05,'foo',id=rndId()))
#        a.add(Hole(3,id=rndId()))
#        a.add(Pin(1,0.1,0.1,1,id=rndId()))
#        a.add(Pin(1,0.1,0.1,1,square=True,id=rndId()))
#        a.add(Pad((0,0),(0,1),0.5,0.1,0.6,id=rndId()))
#        a.subs[0].add(Element())

        from Tuke.geda import Footprint
        common.load_dataset('geda_footprints')
        f1 = Footprint(common.tmpd + '/plcc4-rgb-led',Id('plcc4'))
        f2 = Footprint(common.tmpd + '/supercap_20mm',Id('supercap'))
        a.add(f1)
        a.add(f2)

        dom = a.save(doc)

        print a.save(doc).toprettyxml(indent="  ")

        doc = Document()
        print load_Element(dom).save(doc).toprettyxml(indent="  ")
        
