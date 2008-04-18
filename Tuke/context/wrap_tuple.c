// ### BOILERPLATE ###
// Tuke - Electrical Design Automation toolset
// Copyright (C) 2008 Peter Todd <pete@petertodd.org>
// 
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
// ### BOILERPLATE ###

#include <Python.h>

#include "wrapper.h"

PyObject *
wrap_tuple(PyObject *context,PyObject *obj,int apply){
    // Since tuples are immutable, although their contents may not be, wrapping
    // a tuple is a matter of creating a new tuple, with wrapped inner
    // elements.
    PyObject *r = PyTuple_New(PyTuple_GET_SIZE(obj));
    if (!r) return NULL;

    int i;
    for (i = 0; i < PyTuple_GET_SIZE(obj); i++){
        PyObject *w = NULL,*v;
        v = PyTuple_GET_ITEM(obj,i);
        w = apply_remove_context(context,v,apply);
        if (!w){
            Py_DECREF(r);
            return NULL;
        }
        PyTuple_SET_ITEM(r,i,w);
    }
    return r;
}

// Local Variables:
// mode: C
// fill-column: 76
// c-file-style: "gnu"
// indent-tabs-mode: nil
// End:
// vim: et:sw=4:sts=4:ts=4:cino=>4s,{s,\:s,+s,t0,g0,^-4,e-4,n-4,p4s,(0,=s:
