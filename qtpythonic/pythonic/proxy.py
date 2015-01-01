#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect

from . import lookup


def make_module_proxy(module, QObject):

    module_type = type(module)

    class ModuleProxy(module_type):

        def __getattr__(self, name):
            try:
                thing = lookup.find_module_attribute(module, name)
            except lookup.AttributeNotFound:
                # Try to load the name as-is. Complain if this fails.
                thing = getattr(module, name)
            if inspect.isclass(thing):
                thing = make_class_proxy(thing, QObject)
            return thing

    return ModuleProxy(module.__name__)


def make_class_proxy(qt_klass, QObject):
    # We only want to patch QObject descendants.
    if not issubclass(qt_klass, QObject):
        return qt_klass

    old_getattribute = qt_klass.__getattribute__

    # If this class is already patched, we're good.
    if getattr(old_getattribute, 'patched', False):
        return qt_klass

    def __getattribute__(self, name):
        try:
            attr = lookup.find_object_attribute(self, name, old_getattribute)
        except lookup.AttributeNotFound:
            # Try to load the name as-is. Complain if this fails.
            attr = old_getattribute(self, name)
        if isinstance(attr, lookup.PropertyDescriptor):
            for k in attr:
                attr[k] = make_method_proxy(attr[k], QObject)
            setattr(qt_klass, name, property(**attr))
            return old_getattribute(self, name)
        elif inspect.ismethod(attr):
            attr = make_method_proxy(attr, QObject)
        return attr

    __getattribute__.patched = True
    qt_klass.__getattribute__ = __getattribute__
    return qt_klass


def make_method_proxy(method, QObject):

    def method_proxy(*args, **kwargs):
        retval = method(*args, **kwargs)
        # Patch the returned object's class if needed.
        if isinstance(retval, QObject):
            make_class_proxy(type(retval), QObject)
        return retval

    return method_proxy
