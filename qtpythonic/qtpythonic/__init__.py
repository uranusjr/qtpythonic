#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import importlib
import pkgutil
import sys
import traceback

from . import proxy


def pythonize(qt_package, debug=False):
    this_package_name = __name__.split('.')[0]
    this_package = sys.modules[this_package_name]

    # If this package Pythonized, we're good.
    if getattr(this_package, 'pythonized_for', None) == qt_package:
        return

    QtCore = importlib.import_module(qt_package.__name__ + '.QtCore')

    # Loop through submodules in the Qt module.
    prefix = qt_package.__name__ + '.'
    path = qt_package.__path__
    for _, full_name, _ in pkgutil.iter_modules(path, prefix):
        name = full_name.split('.')[-1]
        if name == 'Qt':
            # This is PyQt's catch-all module. We don't want this.
            continue
        elif name.startswith('Qt'):
            # Modules like QtCore, QtGui, QtWidgets, etc.
            # Strip "Qt" prefix, convert to lower (i.e. core, gui, widgets)
            # Note that multiword modules won't contain underscores. For
            # example "QtPrintSupport" will become "printsupport".
            local_name = name[2:].lower()
        else:
            # Other packages we just convert the name to lowercase.
            local_name = name.lower()
        try:
            qt_module = importlib.import_module(full_name)
        except ImportError:
            if debug:
                print('Could not import ' + full_name, file=sys.stderr)
                traceback.print_stack(file=sys.stderr)
            continue
        proxy_module = proxy.make_module_proxy(qt_module, QtCore.QObject)

        # Inject this into this package (top level).
        setattr(this_package, local_name, proxy_module)
        sys.modules[this_package_name + '.' + local_name] = proxy_module

    this_package.pythonized_for = qt_package
