#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile

import nose
from nose.tools import eq_, assert_true, assert_is_none

import PyQt5
from PyQt5.QtCore import QT_TRANSLATE_NOOP, qVersion, QFile
from qtpythonic import pythonize


def setup():
    pythonize(PyQt5)


def test_qt_module():
    from qtpythonic import core
    # This is not a module, but actually a proxy object. It's not pratical to
    # create proxy classes for all Qt classes at import time (performance
    # issues), so we just proxy them to the real thing the first time they are
    # actually accessed.
    eq_(core.translate_noop, QT_TRANSLATE_NOOP)
    eq_(core.version, qVersion)
    eq_(core.get_version, qVersion)


def test_property():
    from qtpythonic.core import Object
    obj = Object()
    eq_(obj.object_name, '')
    obj.object_name = 'foo'
    eq_(obj.object_name, 'foo')
    obj.set_object_name('bar')
    eq_(obj.get_object_name(), 'bar')


def test_accessors():
    from qtpythonic.core import Object
    parent = Object()
    obj = Object(parent=parent)
    assert_is_none(parent.get_parent())
    eq_(obj.get_parent(), parent)
    obj.set_parent(None)
    assert_is_none(obj.get_parent())


def test_constant_and_method():
    from qtpythonic.core import File
    _, filename = tempfile.mkstemp()
    f = File(filename)
    f.open(f.WRITE_ONLY)
    f.write('foo bar baz')
    f.close()
    with open(filename) as pf:
        eq_(pf.read(), 'foo bar baz')
    f.remove()
    assert_true(type(f), QFile)


def test_returned_object():
    # Objects returned by Qt methods should also be proxied.
    from qtpythonic.core import Object
    level_1 = Object()
    level_1.object_name = '1'
    level_2 = Object(parent=level_1)
    level_2.object_name = '2'
    level_2.get_parent().object_name = '1'
    level_3 = Object(parent=level_2)
    level_3.object_name = '3'
    level_3.get_parent().get_parent().object_name = '1'


if __name__ == '__main__':
    nose.run()
