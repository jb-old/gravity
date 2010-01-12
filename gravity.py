#!/usr/bin/env python3.1
"""This module provides basic gravitional system simulation and
visualization using the dubious math raster image module.

You may encounter issues if you do not treat the types in this module
as though they were immutable. Maybe not. This keeps changing."""

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
        return type(self)(a + b for (a, b) in (self.components, vector.components))
    
    def __sub__(self, vector):
        return type(self)(a - b for (a, b) in (self.components, vector.components))
    
    def __mul__(self, scalar):
        return type(self)(x * scalar for x in self.components)
    
    def __div__(self, scalar):
        return type(self)(x / scalar for x in self.components)
    
    def __neg__(self):
        return type(self)(-x for x in self.components)

    def __iter__(self): # meant for use in iterable instantation, not direct iteration
        return iter(self.components)

    def __bool__(self):
        return any(self)

    def __eq__(self, other):
        return self.components == other.components

    def __repr__(self):
        return "V({})".format(", ".join(repr(v) for v in self.components))

def V(*components):
    """Shortcut for creating Vectors: V(x, y...) -> Vector((x, y...))"""
    
    return Vector(components)

from copy import copy

class Object(object):
    """A kinematic Object with mass, displacement and velocity."""
    
    def __init__(self, mass, displacement, velocity):
        self.mass = mass
        self.displacement = Vector(displacement)
        self.velocity = Vector(velocity)
    
    @classmethod
    def from_dict(cls, source_dict,
                  default_dict = { "m": 1, "d": [ 0, 0 ], "v": [ 0, 0 ], "comment": None }):
        input_dict = copy(default_dict)
        input_dict.update(source_dict)
        
        return cls(input_dict["m"], input_dict["d"], input_dict["v"])

    def __repr__(self):
        return "{.__name__}(mass={!r}, displacement={!r}, velocity={!r})".format(type(self), self.mass,
                                                                                 self.displacement, self.velocity)

class System(list):
    def advanced(self, dt, frames=1, G=6.67428e-11):
        current = System(self)

        dt_per_frame = dt / frames
        
        for _ in range(frames):
            next = System()
            
            for old_object in self:
                new_object = copy(old_object)
                
                for other in self:
                    if other is not old_object:
                        displacement = old_object.displacement - other.displacement
                        
                        if displacement.magnitude > .5:
                            acceleration_magnitude = G * other.mass / displacement.magnitude ** 2
                            
                            x_to_y = displacement[0] / sum(abs(v) for v in displacement)
                            y_to_x = displacement[1] / sum(abs(v) for v in displacement)
                            
                            acceleration = V(acceleration_magnitude * x_to_y,
                                             acceleration_magnitude * (1 - x_to_y))
                            
                            new_object.velocity += acceleration * dt_per_frame
                new_object.displacement += new_object.velocity
                next.append(new_object)
            current = next
        
        return current # Python not having tail recursion optimization is stupid.
                       # If it did, I'd implement this recursively and be happier.

import random

def starify_raster(raster, n=200):
    """Draws background-ish "stars" on a Raster image."""
    for _ in range(100):
        x = random.random() * (raster.width + 4) - 2
        y = random.random() * (raster.height + 4) - 2
        
        r, g, b = [ .5 + .25 * random.random() + .25 * random.random() for _ in range(3) ]
        
        g = min(r, min(b, g)) # ensure green is never above red or blue
        # maybe I could draw colours from a gradient instead, and use one limiting green by default?
        
        raster.dot([x, y], [r, g, b], 1.0, radius=random.random() * 1.2)

import sys
import raster
import json

raster.Raster.starify = starify_raster

def main(in_filename="-", out_filename="-"):
    in_file  = open(in_filename,  "rt") if in_filename  != "-" else sys.stdin
    out_file = open(out_filename, "wb") if out_filename != "-" else sys.stdout.buffer
    
    # later I should add many more rendering control options to this, but this will do to start
    input_defaults = { "comment": None, # it's a comment, ignored
                       "dimensions": [ 256, 256 ], # size of output image, should have some zoom/positioning
                       "G": 6.67428e-11, # gravitational constant (you will want to set this, ha ha maybe I should fix that)
                       "dt": 1.0, # seconds elasped in render
                       "frames": 100, # physics and drawing "frames" to use
                       "objects": [] } # objects in system we're rendering
    
    with in_file, out_file:
        input_dict = input_defaults
        input_dict.update(json.load(in_file))
        
        width, height = dimensions = input_dict["dimensions"]
        offset = V(width / 2 + .5, height / 2 + .5)
        
        frames = input_dict["frames"]
        frame_dt = input_dict["dt"] / (input_dict["frames"] - 1) or 1
        
        sys.stderr.write("Loading input system...\n")
        system = System(Object.from_dict(d) for d in input_dict["objects"])
        
        sys.stderr.write("Instantiating image...\n")
        image = raster.Raster_24RGB(width, height, fill=[0, 0, 0], pen=raster.PEN_MAX)
        sys.stderr.write("Rendering background \"stars\"...\n")
        image.starify()

        offset[1] /= 2
        
        for f in range(input_dict["frames"]):
            sys.stderr.write("Calculating frame {}...           \r".format(f))
            sys.stderr.flush()
            
            if f: system = system.advanced(frame_dt, G=input_dict["G"])
            
            r, g, b, a = raster.mah_spectrum(f / (frames - 1) if frames > 1 else .5)
            
            sys.stderr.write("Calculuated, rendering frame {}...\r".format(f))
            sys.stderr.flush()
            
            if a:
                for object in system:
                    dot_position = object.displacement + offset
                    dot_radius = object.mass ** .5 * 2
                    
                    image.dot(dot_position, [r, g, b], a, radius=dot_radius)
        
        sys.stderr.write("\n")
        
        sys.stderr.write("Writing image to file...")
        image.write_bmp(out_file)
    
if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))

