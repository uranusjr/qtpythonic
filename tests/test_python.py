#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from nose.tools import eq_, assert_false, assert_true

import PyQt5
from PyQt5.QtCore import pyqtSignal
from qtpythonic import pythonize


def setup():
    pythonize(PyQt5)


def test_signal():
    from qtpythonic.core import Signal
    eq_(Signal, pyqtSignal)


def test_connect():
    from qtpythonic.core import Signal
    try:    # Qt 5
        from qtpythonic.widgets import Application, Widget
    except ImportError:     # Qt 4
        from qtpythonic.gui import Application, Widget

    class TestWidget(Widget):

        call_me = Signal()

        def __init__(self):
            super(TestWidget, self).__init__()
            self.call_me.connect(self.show_normal)  # Map to showNormal

        def call(self):
            self.call_me.emit()

    app = Application(sys.argv)
    w = TestWidget()
    assert_false(w.is_visible())
    w.call()
    assert_true(w.is_visible())
    app.quit()
