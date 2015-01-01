#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


# Starts with a lowercase letter, followed by a sequence of lowercase letters
# and underscores.
FUNCTION_PATTERN = re.compile(r'^[a-z][a-z_]*$')
PROPERTY_PATTERN = FUNCTION_PATTERN
# Starts with an uppercase letter, followed by a sequence of uppercase letters
# and underscores.
CONSTANT_PATTERN = re.compile(r'^[A-Z][A-Z_]*$')
# Like FUNCTION_PATTERN, but starts with 'get_' or 'set_'
GETTER_PATTERN = re.compile(r'^get_[a-z][a-z_]*$')
SETTER_PATTERN = re.compile(r'^set_[a-z][a-z_]*$')
# Starts with an uppercase letter, followed by a sequence of letters.
CLASS_PATTERN = re.compile(r'^[A-Z][A-Za-z]*$')


class AttributeNotFound(Exception):
    pass


class PropertyDescriptor(dict):
    pass


def _camelcase(name, capitalize=False):
    # foo_bar_baz => fooBarBaz
    comps = name.split('_')
    if capitalize:
        return ''.join(c.title() for c in comps)
    return ''.join(comps[:1] + [c.title() for c in comps[1:]])


def find_module_attribute(qt_module, name):
    if CONSTANT_PATTERN.match(name):
        # Constant macro name (e.g. VERSION_STR => QT_VERSION_STR)
        qt_name = 'QT_' + name
        try:
            return getattr(qt_module, qt_name)
        except AttributeError:
            pass
    if CLASS_PATTERN.match(name):
        # Class name (e.g. MutexLocker => QMutexLocker)
        qt_name = 'Q' + name
        try:
            return getattr(qt_module, qt_name)
        except AttributeError:
            pass
        # Some special cases (e.g. Signal => pyqtSignal)
        if qt_module.__name__.startswith('PyQt'):
            qt_name = 'pyqt' + name
            try:
                return getattr(qt_module, qt_name)
            except AttributeError:
                pass
    if GETTER_PATTERN.match(name):
        # Global function name (e.g. get_version => qVersion)
        qt_name = 'q' + _camelcase(name[4:], capitalize=True)
        try:
            return getattr(qt_module, qt_name)
        except AttributeError:
            pass
    if FUNCTION_PATTERN.match(name):
        # Global function name (e.g. float_distance => qFloatDistance)
        qt_name = 'q' + _camelcase(name, capitalize=True)
        try:
            return getattr(qt_module, qt_name)
        except AttributeError:
            pass
    # Macro name (e.g. return_arg => Q_RETURN_ARG)
    qt_name = 'Q_' + name.upper()
    try:
        return getattr(qt_module, qt_name)
    except AttributeError:
        pass
    # Macro name (e.g. translate_noop => QT_TRANSLATE_NOOP)
    qt_name = 'QT_' + name.upper()
    try:
        return getattr(qt_module, qt_name)
    except AttributeError:
        pass
    raise AttributeNotFound


def find_object_attribute(obj, name, old_getattribute):
    # Property name (e.g. object_name => objectName)
    if PROPERTY_PATTERN.match(name):
        qt_name = _camelcase(name)
        meta = obj.metaObject()
        if meta.indexOfProperty(qt_name) >= 0:
            # Has matching Qt property. Build a Python property to match.
            idx = meta.indexOfProperty(qt_name)
            qt_prop = meta.property(idx)
            descriptor = PropertyDescriptor()
            if qt_prop.isReadable():
                descriptor['fget'] = qt_prop.read
            if qt_prop.isWritable():
                descriptor['fset'] = qt_prop.write
            if qt_prop.isResettable():
                descriptor['fdel'] = qt_prop.reset
            return descriptor
    if GETTER_PATTERN.match(name):
        qt_name = _camelcase(name[4:])  # Strip "get_" prefix
        try:
            return old_getattribute(obj, qt_name)
        except AttributeError:
            pass
    if FUNCTION_PATTERN.match(name):    # Either a setter or a regular method.
        qt_name = _camelcase(name)
        try:
            return old_getattribute(obj, qt_name)
        except AttributeError:
            pass
    if CONSTANT_PATTERN.match(name):
        # Enum names (e.g. READ_WRITE => ReadWrite)
        qt_name = _camelcase(name, capitalize=True)
        try:
            return old_getattribute(obj, qt_name)
        except AttributeError:
            pass
    raise AttributeNotFound
