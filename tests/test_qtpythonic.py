#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_qtpythonic
----------------------------------

Top-level general tests that don't fit anywhere else.
"""

import nose
from nose.tools import ok_

import PyQt5
from qtpythonic import pythonize


def test_package():
    pythonize(PyQt5)
    import qtpythonic
    ok_(qtpythonic.qt)
    ok_(qtpythonic.core)
    ok_(qtpythonic.gui)

if __name__ == '__main__':
    nose.run()
