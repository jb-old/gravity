#!/usr/bin/env python3
import itertools

def sqrt(n):
    """Returns the square root of a number.

    The default math.sqrt only works on floats, you see."""
    
    return n ** .5

class Vector(object):
    """A Vector value of any number of dimensions."""
    
    def __init__(self, components):
        self.components = list(components)

    @property
    def magnitude(self):
        return sum(x ** 2 for x in self.components) ** (1/2)
    
    @magnitude.setter
    def magnitude(self, value):
        self *= value / self.magnitude
    
    def __getitem__(self, index):
        return self.components[index]
    
    def __setitem__(self, index, value):
        self.components[index] = value
    
    def __add__(self, vector):
        return type(self)(a + b for (a, b) in itertools.zip_longest(self.components, vector.components, fillvalue=0))
    
    def __iadd__(self, vector):
        self.components = [a + b for (a, b) in itertools.zip_longest(self.components, vector.components, fillvalue=0)]
        return self
    
    def __sub__(self, vector):
        return type(self)(a - b for (a, b) in itertools.zip_longest(self.components, vector.components, fillvalue=0))
    
    def __isub__(self, vector):
        self.components = [a - b for (a, b) in itertools.zip_longest(self.components, vector.components, fillvalue=0)]
        return self
    
    def __mul__(self, scalar):
        return type(self)(x * scalar for x in self.components)
    
    __rmul__ = __mul__
    
    def __imul__(self, scalar):
        self.components = [x * scalar for x in self.components]
        return self
    
    def __truediv__(self, scalar):
        return type(self)(x / scalar for x in self.components)
    
    def __itruediv__(self, scalar):
        self.components = [x / scalar for x in self.components]
        return self
    
    def __floordiv__(self, scalar):
        return type(self)(x // scalar for x in self.components)
    
    def __ifloordiv__(self, scalar):
        self.components = [x // scalar for x in self.components]
    
    def __neg__(self):
        return type(self)(-x for x in self.components)

    def __iter__(self):
        return iter(self.components)

    def __bool__(self):
        return any(self)

    def __eq__(self, other):
        return self.components == other.components

    def __repr__(self):
        return "V({})".format(", ".join(repr(v) for v in self.components))

    # use shifts to repr rotations cw and ccw

def V(*components):
    """Shortcut for creating Vectors: V(x, y...) -> Vector((x, y...))"""
    
    return Vector(components)
