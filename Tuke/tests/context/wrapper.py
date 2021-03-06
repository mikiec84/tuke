# vim: tabstop=4 expandtab shiftwidth=4 fileencoding=utf8
# (c) 2008 Peter Todd <pete@petertodd.org>
#
# This program is made available under the GNU GPL version 3.0 or
# greater. See the accompanying file COPYING for details.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.

from __future__ import with_statement

from unittest import TestCase

from Tuke import Element,Id
import Tuke.context
from Tuke.context.wrapper import wrap,Wrapped,_apply_remove_context,_wrapped_cache,unwrap

import sys
import gc

# Used to let values bypass wrapper mangling.
bypass = None

class WrapperTest(TestCase):
    def test_wrap_with_non_element_context(self):
        """wrap() checks that context is an Element instance"""

        self.assertRaises(TypeError,lambda: wrap(None,None))

    def test_Wrapped_obj_context_refcounts(self):
        """Wrapped maintains correct ref counts for obj and context"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id=Id('a'))
        b = Element(id=Id('b'))

        # Check ref counting behavior
        ref_orig_a = sys.getrefcount(a)
        ref_orig_b = sys.getrefcount(a)
        w = wrap(b,a)
        T(sys.getrefcount(a) - ref_orig_a,1)
        T(sys.getrefcount(b) - ref_orig_b,1)

        del w
        T(sys.getrefcount(a) - ref_orig_a,0)
        T(sys.getrefcount(b) - ref_orig_b,0)

    def test_isinstance_Wrapped(self):
        """isinstance(Wrapped)"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id=Id('a'))
        b = Element(id=Id('b'))

        w = wrap(b,a)

        T(isinstance(w,Wrapped))
        T(isinstance(w,Element))

    def test_stacked_wraps_cancel(self):
        """Opposite wraps cancel out"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id=Id('a'))
        b = Element(id=Id('b'))

        wb = wrap(b,a,True)
        T(wb.id,Id('a/b'))
        wb2 = wrap(wb,a,False)
        T(wb2.id,Id('b'))
        T(wb2 is b)

        wb = wrap(b,a,False)
        T(wb.id,Id('../b'))
        wb2 = wrap(wb,a,True)
        T(wb2.id,Id('b'))
        T(wb2 is b)

    def test_is_Wrapped(self):
        """Wrapped(foo) is Wrapped(foo)"""
        keys = _wrapped_cache.keys()

        # These objects aren't supposed to be wrapped.
        def T(obj):
            a = Element(id=Id('a'))
            self.assert_(wrap(obj,a) is obj)
        T(None)
        T(True)
        T(False)
        T(3)
        T(31415)
        T(3.14)
        T(10j)
        T(type(None))
        T(type(self))
        T('foo')
        T(u'foo')

        import tempfile
        f = tempfile.TemporaryFile()
        T(f)

        # These objects are supposed to be wrapped.
        def T(obj):
            a = Element(id=Id('a'))
            self.assert_(wrap(obj,a) is wrap(obj,a))
        T(object())

        self.assert_(_wrapped_cache.keys() == keys)

    def test_cmp_Wrapped(self):
        """cmp(Wrapped,other)"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        e = Element(id=Id('e'))

        # FIXME: this is really only checking for memory leaks right now
        a = object()
        ar = sys.getrefcount(a)
        b = object()
        br = sys.getrefcount(b)

        wa = wrap(a,e)
        war = sys.getrefcount(wa)
        wb = wrap(b,e)
        wbr = sys.getrefcount(wb)

        cmp(wa,wb)
        cmp(wa,b)
        cmp(a,b)

        T(sys.getrefcount(a) - 1,ar)
        T(sys.getrefcount(b) - 1,br)
        T(sys.getrefcount(wa),war)
        T(sys.getrefcount(wb),wbr)
        del wb
        del wa
        gc.collect(2)
        T(sys.getrefcount(a),ar)
        T(sys.getrefcount(b),br)

    def test_circular_Wrapped_are_garbage_collected(self):
        """Wrapped objects with circular references are garbage collected"""
        import gc
        gc.collect(2)
        keys = _wrapped_cache.keys()
        a = Element(id=Id('a'))

        class foo(Element):
            pass

        b = foo(id=Id('b')) 
        b.a = wrap(b,a)

        del a
        del b
        gc.collect(2)
        self.assert_(_wrapped_cache.keys() == keys)

    def test_Wrapped_getsetdel_attr(self):
        """(get|set|del)attr on Wrapped object"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        def R(ex,fn):
            self.assertRaises(ex,fn)

        class skit(object):
            def __init__(self,id):
                self.id = Id(id)
            def __eq__(self,other):
                return self.id == other.id

        a = Element(id=Id('a'))
        b = Element(id=Id('b'))
        w = wrap(b,a)

        # A fail getattr should raise an exception, but not change reference
        # counts.
        n = "NorweiganJarlsburg"
        n_refc = sys.getrefcount(n)
        R(AttributeError,lambda: getattr(w,n))
        T(sys.getrefcount(n),n_refc)
       
        n = "Abuse"
        n_refc = sys.getrefcount(n)
        v = skit('vacuous_coffee_nosed_maloderous_pervert')
        v_refc = sys.getrefcount(v)

        # setattr should add a reference to the name and value.
        setattr(w,n,v)
        T(sys.getrefcount(n) - 1,n_refc)
        T(sys.getrefcount(v) - 1,v_refc)

        # getattr should not effect anything.
        T(w.Abuse,v) 
        T(sys.getrefcount(n) - 1,n_refc)
        T(sys.getrefcount(v) - 1,v_refc)

        # delattr should decref name and value
        delattr(w,n)
        T(sys.getrefcount(n),n_refc)
        T(sys.getrefcount(v),v_refc)

    def test_Wrapped_hash(self):
        """hash(Wrapped)"""
        a = Element(id=Id('a'))

        class smoot:
            def __hash__(self):
                return 1930
        b = smoot()
        w = wrap(b,a)

        self.assert_(hash(b) == 1930)
        self.assert_(hash(w) == 1930)

    def test_Wrapped_as_mapping_sequence(self):
        """Wrapped objects support the mapping/sequence protocol"""
        global bypass
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))
        def B(got,expected,bypass_expected):
            global bypass
            T(got,expected)
            T(bypass,bypass_expected)

        context_element = Element(id=Id('a'))
        def apply(obj):
            return _apply_remove_context(context_element,obj,1)
        def remove(obj):
            return _apply_remove_context(context_element,obj,0)

        class skit(object):
            def __init__(self,id):
                self.id = Id(id)
            def __eq__(self,other):
                return self.id == other.id

        class Ortelius_A005150:
            def __len__(self):
                return 1598-1527 + 3
            def __getitem__(self,key):
                global bypass
                bypass = key 
                return bypass
            def __setitem__(self,key,value):
                global bypass
                bypass = (key,value)
            def __contains__(self,other):
                global bypass
                bypass = other
                return False

        o = wrap(Ortelius_A005150(),context_element)

        # Wrapped_length 
        T(len(o),71 + 3)

        # Wrapped_getitem 
        T(o[None],None)
        B(o[Id('b')],Id('b'),Id('../b'))
        B(o[skit('b')],skit('b'),remove(skit('b')))

        # check for memory leaks
        s1 = object()
        s1r = sys.getrefcount(s1)
        T(isinstance(o[s1],object))
        bypass = None
        gc.collect(2)
        T(sys.getrefcount(s1),s1r)

        # getitem, got slice, as non-integer slice objects can't use the faster
        # integer slice optimization path.
        #
        # FIXME: doesn't work, but this is a hell of an obscure use case...
        # B(o[Id('a'):Id('b')],
        #  apply(slice(Id('a'),Id('b'),None)),
        #  slice(0,1,None))

        # Wrapped_slice 
        B(o[0:1],slice(0,1,None),slice(0,1,None))

        # Wrapped_ass_subscript
        o[0] = 1
        T(bypass,(0,1))
        o[Id('b')] = Id('c')
        T(bypass,(Id('../b'),Id('../c')))
        o[skit('b')] = skit('c')
        T(bypass,(skit('../b'),skit('../c')))

        # Again, still a assign to subscript, non-integer slice objects can't
        # use the facter Wrapped_ass_slice optimization
        #
        # FIXME: doesn't work yet, again, obscure use case
        #
        #o['a':'b'] = 'c'
        #T(bypass,(slice('a','b',None),'c'))

        # Wrapped_ass_slice
        o[0:1] = Id('b')
        T(bypass,(slice(0,1,None),Id('../b')))

        # Wrapped_contains
        B(None in o,False,None)
        B(1 in o,False,1)
        B(Id('b') in o,False,Id('../b'))
        B(skit('b') in o,False,skit('../b'))

    def test_Wrapped_non_mapping_sequence_raises_error(self):
        """Wrapped objects that don't support the mapping/sequence protocol raise errors"""
        a = Element(id=Id('a'))
        w = wrap(object(),a)
        self.assertRaises(TypeError,lambda: len(w))
        self.assertRaises(TypeError,lambda: w[0])
        self.assertRaises(TypeError,lambda: w['a'])
        self.assertRaises(TypeError,lambda: w['a':'b'])
        self.assertRaises(TypeError,lambda: w[0:1])

    def test_Wrapped_iteration(self):
        """Wrapped objects can be iterated over"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))
        context_element = Element(id=Id('a'))
        def apply(obj):
            return _apply_remove_context(context_element,obj,1)
        def remove(obj):
            return _apply_remove_context(context_element,obj,0)

        class skit(object):
            def __init__(self,id):
                self.id = Id(id)
            def __eq__(self,other):
                return self.id == other.id

        class myrange_or_the_highrange:
            def __iter__(self):
                for i in bypass:
                    yield i

        global bypass
        bypass = [None,Id('b'),skit('c')]

        # apply a context
        b = myrange_or_the_highrange()
        r = []
        for i in _apply_remove_context(context_element,b,1):
            r += [i]
        T(r,[None,Id('a/b'),apply(skit('c'))])

        # remove a context
        b = myrange_or_the_highrange()
        r = []
        for i in _apply_remove_context(context_element,b,0):
            r += [i]
        T(r,[None,Id('../b'),remove(skit('c'))])

    def test_Wrapped_non_iterable_raises_error(self):
        """Wrapped objects that don't support the iteration protocol raise errors"""
        a = Element(id=Id('a'))
        w = wrap(object(),a)
        self.assertRaises(TypeError,lambda: iter(w))

    def test_Wrapped_repr_str(self):
        """(str|repr)(Wrapped)"""
        class skit(object):
            def __repr__(self):
                return "repr" 
            def __str__(self):
                return "str" 

        context = Element(id=Id('a'))
        s = skit()
        w = wrap(s,context)

        self.assert_(str(w),'str') 
        self.assert_(repr(w)) 

    def test_Wrapped_repr_str_special(self):
        """__wrapped_(str|repr)__ special"""
        global bypass

        a = Element(id=Id('a'))

        class skit(object):
            def __wrapped_repr__(self):
                return bypass
            def __wrapped_str__(self):
                return bypass

        w = wrap(skit(),a)

        bypass = None
        self.assertRaises(ValueError,lambda: repr(w))

        def T(chunks,expectedr,expecteds = None):
            if expecteds is None:
                expecteds = expectedr
            global bypass
            bypass = chunks
            gotr = repr(w)
            gots = str(w)
            self.assert_(expectedr == gotr,
                    'got repr: %s  expected: %s' % (gotr,expectedr))
            self.assert_(expecteds == gots,
                    'got str: %s  expected: %s' % (gots,expecteds))

        T((),'')
        T((None,),repr(None))
        T((1506,' nix',' nix'),"1506 nix nix")
        T((Id('.'),),repr(Id('a')),'a')
        T((Id('a'),),repr(Id('a/a')),'a/a')

        class foo:
            def __wrapped_repr__(self):
                return (Id('foo'),)
            def __wrapped_str__(self):
                return (Id('foo'),)

        class bar:
            def __wrapped_repr__(self):
                return (Id('bar'),',',foo())
            def __wrapped_str__(self):
                return (Id('bar'),',',foo())

        class far:
            def __wrapped_repr__(self):
                return (Id('far'),',',bar())
            def __wrapped_str__(self):
                return (Id('far'),',',bar())

        T((far(),),
                "Tuke.Id('a/far'),Tuke.Id('a/bar'),Tuke.Id('a/foo')",
                "a/far,a/bar,a/foo")

        # FIXME: recursive, and crashes
        # T((skit(),),repr(Id('.')))

    def test_Wrapped_repr_str_special_exceptions(self):
        """__wrapped_(str|repr)__ special exceptions"""
        global bypass

        a = Element(id=Id('a'))

        class skit(object):
            def __wrapped_repr__(self):
                raise bypass
            def __wrapped_str__(self):
                raise bypass

        w = wrap(skit(),a)

        bypass = AssertionError
        self.assertRaises(AssertionError,lambda:repr(w))
        self.assertRaises(AssertionError,lambda:str(w))

    def test_Wrapped_repr_str_special_noncallable(self):
        """Non-callable __wrapped_(str|repr)__ special"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id=Id('a'))

        class skit(object):
            __wrapped_str__ = None
            __wrapped_repr__ = None
            def __str__(self):
                return "Suffragium asotas"
            def __repr__(self):
                return "Refuge for the dissipated."

        w = wrap(skit(),a)

        T(str(w) != "Suffragium asotas")
        T(repr(w) != "Refuge for the dissipated.")

    def test_Wrapped_data_in_out(self):
        """Wrapped data in/out"""

        context_element = Element(id=Id('a'))
        def apply(obj):
            return _apply_remove_context(context_element,obj,1)
        def remove(obj):
            return _apply_remove_context(context_element,obj,0)

        def W(obj,expected_applied,expected_removed):
            applied = apply(obj) 
            self.assert_(expected_applied == applied,
                    'applied context, got: %s  expected: %s'
                     % (applied,expected_applied))
            removed = remove(obj) 
            self.assert_(expected_removed == removed,
                    'removed context, got: %s  expected: %s'
                     % (removed,expected_removed))

        class skit(object):
            def __init__(self,id):
                self.id = Id(id)
            def __eq__(self,other):
                return self.id == other.id

        # tuples
        W((),(),())
        W((1,),(1,),(1,))
        W((Id('b'),),(Id('a/b'),),(Id('../b'),))
        W((skit('b'),),(skit('a/b'),),(skit('../b'),))

        # lists
        W([],[],[])
        W([1,],[1,],[1,])
        W([Id('b'),],[Id('a/b'),],[Id('../b'),])
        W([skit('b'),],[skit('a/b'),],[skit('../b'),])

        # dicts
        W({},{},{})
        W({1:1},{1:1},{1:1})
        W({1:Id('b')},{1:Id('a/b')},{1:Id('../b')})
        W({1:skit('b')},{1:skit('a/b')},{1:skit('../b')})
        # Translatable object as key
        W({Id('b'):Id('b')},{Id('a/b'):Id('a/b')},{Id('../b'):Id('../b')})
        # Wrapped object as key
        f = lambda:None
        W({f:Id('b')},{apply(f):Id('a/b')},{remove(f):Id('../b')}) 

    def test_unwrap(self):
        """unwrap()"""
        def T(got,expected = True):
            self.assert_(expected == got,'got: %s  expected: %s' % (got,expected))

        a = Element(id=Id('a'))
        u = unwrap(a)
        T(u.id,Id('.'))
        u = unwrap(u)
        T(u.id,Id('.'))
