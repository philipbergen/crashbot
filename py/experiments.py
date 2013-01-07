# -*- coding: utf-8 -*-

class Properties(object):
    '''
    >>> p = Properties(x=10, y=20)
    >>> p.x
    10
    >>> p.y
    20
    >>> p.z
    Traceback (most recent call last):
    AttributeError: 'Properties' object has no attribute 'z'
    >>> p
    Properties(x=10, y=20)
    '''
    def __init__(self, **kwargs):
        self.__keys = sorted(kwargs.keys())
        for key, val in kwargs.iteritems():
            setattr(self, key, val)

    def __repr__(self):
        return 'Properties(' + ', '.join(['%s=%r' % (key, getattr(self, key)) for key in self.__keys]) + ')'
